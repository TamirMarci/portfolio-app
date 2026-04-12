"""
Snapshot service — computes derived fields for portfolio snapshots.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.repositories import snapshot_repo, holding_repo
from app.schemas.snapshot import (
    SnapshotRead, SnapshotHoldingRead, SnapshotListItem,
    SnapshotCompareResult, AssetChange,
)


def _build_executive_summary(
    from_label: str,
    to_label: str,
    val_change: float | None,
    val_change_pct: float | None,
    changes: list[AssetChange],
) -> str:
    if val_change is None or val_change_pct is None:
        return "Insufficient data to generate a summary."

    direction = "grew" if val_change >= 0 else "declined"
    sign = "+" if val_change >= 0 else "-"
    abs_pct = abs(val_change_pct * 100)
    abs_val = abs(val_change)

    both = [c for c in changes if c.from_value_usd is not None and c.to_value_usd is not None]
    gainers = sorted([c for c in both if (c.value_change_usd or 0) > 0], key=lambda x: x.value_change_pct or 0, reverse=True)
    losers  = sorted([c for c in both if (c.value_change_usd or 0) < 0], key=lambda x: x.value_change_pct or 0)
    new_pos = [c for c in changes if c.from_value_usd is None]
    closed  = [c for c in changes if c.to_value_usd is None]

    parts = [
        f"Portfolio {direction} by {abs_pct:.1f}% ({sign}${abs_val:,.0f}) "
        f"from {from_label} to {to_label}."
    ]
    if gainers:
        g = gainers[0]
        parts.append(
            f"Top performer: {g.symbol} ({(g.value_change_pct or 0)*100:+.1f}%, "
            f"contributed {(g.contribution_pct or 0)*100:+.1f}% to total return)."
        )
    if losers:
        lo = losers[0]
        parts.append(
            f"Largest detractor: {lo.symbol} ({(lo.value_change_pct or 0)*100:+.1f}%, "
            f"{(lo.contribution_pct or 0)*100:+.1f}% impact on total return)."
        )
    if new_pos:
        syms = ", ".join(c.symbol for c in new_pos[:3])
        extra = f" (+{len(new_pos) - 3} more)" if len(new_pos) > 3 else ""
        parts.append(f"New positions: {syms}{extra}.")
    if closed:
        syms = ", ".join(c.symbol for c in closed[:3])
        extra = f" (+{len(closed) - 3} more)" if len(closed) > 3 else ""
        parts.append(f"Positions exited: {syms}{extra}.")

    return " ".join(parts)


def _snapshot_to_list_item(snap) -> SnapshotListItem:
    total_return_pct = None
    if snap.total_cost_usd and snap.total_value_usd and snap.total_cost_usd > 0:
        total_return_pct = (snap.total_value_usd - snap.total_cost_usd) / snap.total_cost_usd
    return SnapshotListItem(
        id=snap.id,
        snapshot_date=snap.snapshot_date,
        label=snap.label,
        total_cost_usd=snap.total_cost_usd,
        total_value_usd=snap.total_value_usd,
        total_return_pct=total_return_pct,
    )


def create_snapshot_from_holdings(db: Session, label: str | None) -> SnapshotListItem:
    """
    Capture the current portfolio state as an immutable snapshot.
    Uses cached prices for value; falls back to avg_cost_usd when no price is cached.
    Raises ValueError if no holdings exist or a snapshot for today already exists.
    """
    from app.services import market_data_service

    today = date.today().isoformat()
    if snapshot_repo.get_by_date(db, today):
        raise ValueError(f"A snapshot for {today} already exists.")

    holdings = holding_repo.get_all_with_asset(db)
    if not holdings:
        raise ValueError("No holdings to snapshot.")

    symbols = [h.asset.symbol for h in holdings]
    price_data = market_data_service.get_cached_prices(db, symbols)

    total_cost = 0.0
    total_value = 0.0
    rows = []

    for h in holdings:
        pd = price_data.get(h.asset.symbol, {})
        price = pd.get("price_usd") or h.avg_cost_usd
        cost = h.quantity * h.avg_cost_usd
        value = h.quantity * price
        total_cost += cost
        total_value += value
        rows.append((h, price, value))

    snap = snapshot_repo.create_snapshot(
        db,
        snapshot_date=today,
        label=label,
        total_cost_usd=total_cost,
        total_value_usd=total_value,
    )
    for h, price, value in rows:
        snapshot_repo.add_holding(
            db,
            snapshot_id=snap.id,
            asset_id=h.asset_id,
            quantity=h.quantity,
            avg_cost_usd=h.avg_cost_usd,
            price_at_snapshot=price,
            value_usd=value,
        )

    return _snapshot_to_list_item(snap)


def compare_snapshots(db: Session, from_id: str, to_id: str) -> SnapshotCompareResult:
    """
    Compare two snapshots and return portfolio-level and per-asset changes.
    Assets that appear in only one snapshot get None for the absent side.
    Results are sorted by absolute value change descending.
    """
    from_snap = snapshot_repo.get_by_id(db, from_id)
    to_snap = snapshot_repo.get_by_id(db, to_id)
    if not from_snap:
        raise ValueError(f"Snapshot not found: {from_id}")
    if not to_snap:
        raise ValueError(f"Snapshot not found: {to_id}")

    from_holdings = {sh.asset_id: sh for sh in from_snap.holdings}
    to_holdings = {sh.asset_id: sh for sh in to_snap.holdings}
    all_asset_ids = set(from_holdings) | set(to_holdings)

    from_total = from_snap.total_value_usd or 0.0
    to_total = to_snap.total_value_usd or 0.0

    changes: list[AssetChange] = []
    for asset_id in all_asset_ids:
        fh = from_holdings.get(asset_id)
        th = to_holdings.get(asset_id)
        asset = (fh or th).asset  # type: ignore[union-attr]

        from_val = fh.value_usd if fh else None
        to_val = th.value_usd if th else None
        from_qty = fh.quantity if fh else None
        to_qty = th.quantity if th else None

        val_change = (to_val - from_val) if (to_val is not None and from_val is not None) else None
        val_change_pct = (
            val_change / from_val if (val_change is not None and from_val and from_val > 0) else None
        )
        contribution = (
            val_change / from_total if (val_change is not None and from_total > 0) else None
        )

        changes.append(AssetChange(
            asset_id=asset_id,
            symbol=asset.symbol,
            name=asset.name,
            from_quantity=from_qty,
            to_quantity=to_qty,
            quantity_change=(to_qty - from_qty) if (to_qty is not None and from_qty is not None) else None,
            from_value_usd=from_val,
            to_value_usd=to_val,
            value_change_usd=val_change,
            value_change_pct=val_change_pct,
            contribution_pct=contribution,
        ))

    changes.sort(key=lambda x: abs(x.value_change_usd or 0), reverse=True)

    val_change = (to_total - from_total) if (from_total and to_total) else None
    val_change_pct = (val_change / from_total) if (val_change is not None and from_total > 0) else None

    from_label = from_snap.label or from_snap.snapshot_date
    to_label   = to_snap.label   or to_snap.snapshot_date
    summary = _build_executive_summary(from_label, to_label, val_change, val_change_pct, changes)

    return SnapshotCompareResult(
        from_snapshot_id=from_snap.id,
        from_snapshot_date=from_snap.snapshot_date,
        from_snapshot_label=from_snap.label,
        from_total_value_usd=from_snap.total_value_usd,
        to_snapshot_id=to_snap.id,
        to_snapshot_date=to_snap.snapshot_date,
        to_snapshot_label=to_snap.label,
        to_total_value_usd=to_snap.total_value_usd,
        value_change_usd=val_change,
        value_change_pct=val_change_pct,
        asset_changes=changes,
        executive_summary=summary,
    )


def update_snapshot_label(db: Session, snapshot_id: str, label: str | None) -> SnapshotListItem:
    """Rename a snapshot. Raises ValueError if not found."""
    snap = snapshot_repo.get_by_id(db, snapshot_id)
    if not snap:
        raise ValueError(f"Snapshot not found: {snapshot_id}")
    snapshot_repo.update_label(db, snap, label)
    return _snapshot_to_list_item(snap)


def delete_snapshot(db: Session, snapshot_id: str) -> None:
    """Delete a snapshot and all its holdings. Raises ValueError if not found."""
    snap = snapshot_repo.get_by_id(db, snapshot_id)
    if not snap:
        raise ValueError(f"Snapshot not found: {snapshot_id}")
    snapshot_repo.delete(db, snap)


def get_all_snapshots(db: Session) -> list[SnapshotListItem]:
    return [_snapshot_to_list_item(s) for s in snapshot_repo.get_all(db)]


def get_snapshot_detail(db: Session, snapshot_id: str) -> SnapshotRead | None:
    snap = snapshot_repo.get_by_id(db, snapshot_id)
    if not snap:
        return None

    total_value = snap.total_value_usd or 0.0
    total_return_pct = None
    if snap.total_cost_usd and snap.total_value_usd and snap.total_cost_usd > 0:
        total_return_pct = (snap.total_value_usd - snap.total_cost_usd) / snap.total_cost_usd

    holding_reads: list[SnapshotHoldingRead] = []
    for sh in snap.holdings:
        asset = sh.asset
        cost_basis = sh.quantity * sh.avg_cost_usd
        return_pct = ((sh.value_usd - cost_basis) / cost_basis) if cost_basis > 0 else 0.0
        allocation_pct = (sh.value_usd / total_value) if total_value > 0 else 0.0

        holding_reads.append(
            SnapshotHoldingRead(
                asset_id=asset.id,
                symbol=asset.symbol,
                name=asset.name,
                asset_type=asset.asset_type,
                quantity=sh.quantity,
                avg_cost_usd=sh.avg_cost_usd,
                cost_basis_usd=cost_basis,
                price_at_snapshot=sh.price_at_snapshot,
                value_usd=sh.value_usd,
                return_pct=return_pct,
                allocation_pct=allocation_pct,
            )
        )

    # Sort by value descending
    holding_reads.sort(key=lambda h: h.value_usd, reverse=True)

    return SnapshotRead(
        id=snap.id,
        snapshot_date=snap.snapshot_date,
        label=snap.label,
        total_cost_usd=snap.total_cost_usd,
        total_value_usd=snap.total_value_usd,
        total_return_pct=total_return_pct,
        holdings=holding_reads,
    )
