from pydantic import BaseModel


class SnapshotCreate(BaseModel):
    label: str | None = None


class SnapshotUpdate(BaseModel):
    label: str | None = None


class AssetChange(BaseModel):
    asset_id: str
    symbol: str
    name: str
    from_quantity: float | None
    to_quantity: float | None
    quantity_change: float | None
    from_value_usd: float | None
    to_value_usd: float | None
    value_change_usd: float | None
    value_change_pct: float | None
    contribution_pct: float | None   # value_change / from_portfolio_value


class SnapshotCompareResult(BaseModel):
    from_snapshot_id: str
    from_snapshot_date: str
    from_snapshot_label: str | None
    from_total_value_usd: float | None
    to_snapshot_id: str
    to_snapshot_date: str
    to_snapshot_label: str | None
    to_total_value_usd: float | None
    value_change_usd: float | None
    value_change_pct: float | None
    asset_changes: list[AssetChange]
    executive_summary: str


class SnapshotHoldingRead(BaseModel):
    asset_id: str
    symbol: str
    name: str
    asset_type: str
    quantity: float
    avg_cost_usd: float
    cost_basis_usd: float       # quantity * avg_cost_usd
    price_at_snapshot: float
    value_usd: float
    return_pct: float           # (value_usd - cost_basis_usd) / cost_basis_usd
    allocation_pct: float       # value_usd / snapshot total_value_usd

    model_config = {"from_attributes": True}


class SnapshotRead(BaseModel):
    id: str
    snapshot_date: str
    label: str | None
    total_cost_usd: float | None
    total_value_usd: float | None
    total_return_pct: float | None  # (total_value - total_cost) / total_cost
    holdings: list[SnapshotHoldingRead]

    model_config = {"from_attributes": True}


class SnapshotListItem(BaseModel):
    id: str
    snapshot_date: str
    label: str | None
    total_cost_usd: float | None
    total_value_usd: float | None
    total_return_pct: float | None
