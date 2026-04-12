"""
DB loader — takes normalized raw data objects and upserts them into the database.
All operations run inside a single transaction; the caller commits or rolls back.
"""

import logging
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.repositories import asset_repo, holding_repo, transaction_repo, snapshot_repo, option_repo
from importer.parsers.holdings_parser import RawHolding
from importer.parsers.transactions_parser import RawTransaction
from importer.parsers.options_parser import RawOptionTrade
from importer.parsers.snapshot_parser import RawSnapshot

logger = logging.getLogger(__name__)


@dataclass
class LoadResult:
    """Counts returned by every load_* function for summary reporting."""
    inserted: int
    skipped: int

    @property
    def total(self) -> int:
        return self.inserted + self.skipped


def load_holdings(db: Session, raw_holdings: list[RawHolding], fx_rates: dict[str, float]) -> LoadResult:
    """
    Upsert assets and holdings. FX rates convert avg_cost_native → avg_cost_usd.
    fx_rates format: {"CAD": 0.74, ...}  (value = 1 native currency in USD)

    Holdings are always upserted (never skipped); 'inserted' here means 'upserted'.
    """
    upserted = 0
    for rh in raw_holdings:
        try:
            asset = asset_repo.upsert(
                db,
                symbol=rh.symbol,
                name=rh.company,
                asset_type=rh.asset_type,
                exchange=rh.exchange,
                currency=rh.currency,
            )
            fx = fx_rates.get(rh.currency, 1.0) if rh.currency != "USD" else 1.0
            avg_cost_usd = rh.avg_cost_native * fx

            holding_repo.upsert(
                db,
                asset_id=asset.id,
                quantity=rh.quantity,
                avg_cost_usd=avg_cost_usd,
                avg_cost_native=rh.avg_cost_native,
            )
            upserted += 1
            logger.debug("Upserted holding: %s  qty=%s  avg_cost_usd=%.4f", rh.symbol, rh.quantity, avg_cost_usd)
        except Exception as exc:
            logger.error("Failed to load holding %s: %s", rh.symbol, exc)
    logger.info("Holdings — upserted: %d  (total processed: %d)", upserted, len(raw_holdings))
    return LoadResult(inserted=upserted, skipped=0)


BOOTSTRAP_DATE = "1900-01-01"


def load_bootstrap_transactions(db: Session, raw_holdings: list[RawHolding], fx_rates: dict[str, float]) -> LoadResult:
    """
    Create one synthetic BUY transaction per holding to seed the transaction history.
    Bootstrap transactions represent the portfolio state at the time of Excel import.
    They are marked with is_bootstrap=True and source="excel_import", and are
    idempotent: a holding with the same (asset_id, type, date, qty, price) is skipped.
    """
    inserted = 0
    skipped = 0
    for rh in raw_holdings:
        try:
            asset = asset_repo.get_by_symbol(db, rh.symbol)
            if not asset:
                asset = asset_repo.upsert(
                    db,
                    symbol=rh.symbol,
                    name=rh.company,
                    asset_type=rh.asset_type,
                    exchange=rh.exchange,
                    currency=rh.currency,
                )
                logger.info("Bootstrap: created asset %s", rh.symbol)
            fx = fx_rates.get(rh.currency, 1.0) if rh.currency != "USD" else 1.0
            avg_cost_usd = rh.avg_cost_native * fx
            existing = transaction_repo.get_by_natural_key(
                db,
                asset_id=asset.id,
                type="BUY",
                trade_date=BOOTSTRAP_DATE,
                quantity=rh.quantity,
                price_per_share=rh.avg_cost_native,
            )
            if existing:
                skipped += 1
                logger.debug("Bootstrap transaction already exists — skipping: %s", rh.symbol)
                continue
            transaction_repo.create(
                db,
                asset_id=asset.id,
                type="BUY",
                quantity=rh.quantity,
                price_per_share=rh.avg_cost_native,
                price_usd=avg_cost_usd,
                fx_rate_to_usd=fx,
                trade_date=BOOTSTRAP_DATE,
                fees=0.0,
                notes="Bootstrap seed from Excel Holdings",
                is_bootstrap=True,
                source="excel_import",
            )
            inserted += 1
            logger.debug("Inserted bootstrap transaction: %s  qty=%s  price=%.4f", rh.symbol, rh.quantity, rh.avg_cost_native)
        except Exception as exc:
            logger.error("Failed to create bootstrap transaction for %s: %s", rh.symbol, exc)
    logger.info("Bootstrap transactions — inserted: %d  skipped: %d", inserted, skipped)
    return LoadResult(inserted=inserted, skipped=skipped)


def load_transactions(
    db: Session,
    raw_transactions: list[RawTransaction],
    fx_rates: dict[str, float] | None = None,
) -> LoadResult:
    """
    Insert transactions that do not already exist (idempotent).
    Existence is checked via the natural key: (asset_id, type, trade_date, quantity, price_per_share).
    Running the importer twice will skip all rows on the second run.

    fx_rates: current FX rates used as best-effort for non-USD price_usd conversion.
    Historical rates are unavailable, so today's rate is used for older transactions.
    """
    rates = fx_rates or {}
    inserted = 0
    skipped = 0
    for rt in raw_transactions:
        try:
            asset = asset_repo.get_by_symbol(db, rt.symbol)
            if not asset:
                # Asset may have been sold and is no longer in Holdings — create a minimal stub
                logger.info("Transaction: creating stub asset for sold security %s", rt.symbol)
                asset = asset_repo.upsert(
                    db, symbol=rt.symbol, name=rt.symbol,
                    asset_type="STOCK", exchange=None, currency="USD",
                )
            existing = transaction_repo.get_by_natural_key(
                db,
                asset_id=asset.id,
                type=rt.type,
                trade_date=rt.trade_date,
                quantity=rt.quantity,
                price_per_share=rt.price_per_share,
            )
            if existing:
                skipped += 1
                logger.debug(
                    "Transaction already exists — skipping: %s %s %s shares @ %.4f on %s",
                    rt.type, rt.symbol, rt.quantity, rt.price_per_share, rt.trade_date,
                )
                continue
            fx = rates.get(asset.currency, 1.0) if asset.currency != "USD" else 1.0
            price_usd = rt.price_per_share * fx
            transaction_repo.create(
                db,
                asset_id=asset.id,
                type=rt.type,
                quantity=rt.quantity,
                price_per_share=rt.price_per_share,
                price_usd=price_usd,
                fx_rate_to_usd=fx,
                trade_date=rt.trade_date,
                fees=rt.fees,
            )
            inserted += 1
            logger.debug("Inserted transaction: %s %s %s shares @ %.4f", rt.type, rt.symbol, rt.quantity, rt.price_per_share)
        except Exception as exc:
            logger.error("Failed to load transaction %s: %s", rt.symbol, exc)

    logger.info(
        "Transactions — inserted: %d  skipped: %d  (total processed: %d)",
        inserted, skipped, inserted + skipped,
    )
    return LoadResult(inserted=inserted, skipped=skipped)


def load_options(db: Session, raw_options: list[RawOptionTrade]) -> LoadResult:
    """
    Insert option trades that do not already exist (idempotent).
    Existence is checked via the natural key:
    (underlying_asset_id, option_type, action, strike, expiration_date, open_date).
    Running the importer twice will skip all rows on the second run.
    """
    inserted = 0
    skipped = 0
    for ro in raw_options:
        try:
            asset = asset_repo.get_by_symbol(db, ro.underlying_symbol)
            if not asset:
                logger.warning("Option skipped: underlying asset %s not found in DB", ro.underlying_symbol)
                skipped += 1
                continue
            existing = option_repo.get_by_natural_key(
                db,
                underlying_asset_id=asset.id,
                option_type=ro.option_type,
                action=ro.action,
                strike=ro.strike,
                expiration_date=ro.expiration_date,
                open_date=ro.open_date,
            )
            if existing:
                skipped += 1
                logger.debug(
                    "Option already exists — skipping: %s %s %s strike=%s exp=%s opened=%s",
                    ro.action, ro.option_type, ro.underlying_symbol, ro.strike, ro.expiration_date, ro.open_date,
                )
                continue
            option_repo.create(
                db,
                underlying_asset_id=asset.id,
                option_type=ro.option_type,
                action=ro.action,
                strike=ro.strike,
                expiration_date=ro.expiration_date,
                quantity=ro.quantity,
                open_date=ro.open_date,
                open_price=ro.open_price,
                open_commission=ro.open_commission,
                exit_date=ro.exit_date,
                exit_price=ro.exit_price,
                close_commission=ro.close_commission,
                status=ro.status,
                net_pnl=ro.net_pnl,
            )
            inserted += 1
            logger.debug(
                "Inserted option: %s %s %s strike=%s exp=%s",
                ro.action, ro.option_type, ro.underlying_symbol, ro.strike, ro.expiration_date,
            )
        except Exception as exc:
            logger.error("Failed to load option %s: %s", ro.underlying_symbol, exc)
    logger.info(
        "Options — inserted: %d  skipped: %d  (total processed: %d)",
        inserted, skipped, inserted + skipped,
    )
    return LoadResult(inserted=inserted, skipped=skipped)


def load_snapshot(db: Session, raw_snapshot: RawSnapshot, fx_rates: dict[str, float]) -> LoadResult:
    """
    Insert a PortfolioSnapshot and all its SnapshotHoldings.
    Skips the entire snapshot if one with the same date already exists.
    Returns LoadResult where inserted=1/skipped=1 refers to the snapshot (not individual holdings).
    """
    existing = snapshot_repo.get_by_date(db, raw_snapshot.snapshot_date)
    if existing:
        logger.info("Snapshot %s already exists — skipping.", raw_snapshot.snapshot_date)
        return LoadResult(inserted=0, skipped=1)

    total_cost = 0.0
    total_value = 0.0
    valid_holdings = []

    for rsh in raw_snapshot.holdings:
        asset = asset_repo.get_by_symbol(db, rsh.symbol)
        if not asset:
            # Asset might not be in Holdings (e.g. INTC was sold) — create a minimal asset record
            logger.info("Snapshot: creating stub asset for %s", rsh.symbol)
            asset = asset_repo.upsert(
                db,
                symbol=rsh.symbol,
                name=rsh.company,
                asset_type="STOCK",
                exchange=None,
                currency="USD",
            )

        fx = fx_rates.get(asset.currency, 1.0) if asset.currency != "USD" else 1.0
        avg_cost_usd = rsh.avg_cost_native * fx
        cost_basis = rsh.quantity * avg_cost_usd
        total_cost += cost_basis
        total_value += rsh.value_usd
        valid_holdings.append((asset, rsh, avg_cost_usd))

    snap = snapshot_repo.create_snapshot(
        db,
        snapshot_date=raw_snapshot.snapshot_date,
        label=raw_snapshot.label,
        total_cost_usd=total_cost,
        total_value_usd=total_value,
    )

    for asset, rsh, avg_cost_usd in valid_holdings:
        snapshot_repo.add_holding(
            db,
            snapshot_id=snap.id,
            asset_id=asset.id,
            quantity=rsh.quantity,
            avg_cost_usd=avg_cost_usd,
            price_at_snapshot=rsh.price_at_snapshot,
            value_usd=rsh.value_usd,
        )

    logger.info(
        "Snapshot %s (%s) inserted with %d holdings.",
        raw_snapshot.snapshot_date, raw_snapshot.label, len(valid_holdings),
    )
    return LoadResult(inserted=1, skipped=0)
