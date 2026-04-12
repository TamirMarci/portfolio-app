// ─── Holdings ────────────────────────────────────────────────────────────────

export interface Holding {
  id: string
  symbol: string
  name: string
  asset_type: string
  exchange: string | null
  currency: string
  quantity: number
  avg_cost_usd: number
  avg_cost_native: number | null
  cost_basis_usd: number
  current_price_usd: number | null
  current_price_native: number | null
  current_value_usd: number | null
  unrealized_pnl_usd: number | null
  unrealized_pnl_pct: number | null
  allocation_pct: number | null
  price_stale: boolean
  price_fetched_at: string | null
}

export interface PortfolioCashAndPnl {
  options_income_cash: number     // net premium from OTM expiry + closed trades
  position_close_cash: number     // delivery proceeds from ITM assignment (±)
  total_cash: number              // options_income_cash + position_close_cash

  options_realized_pnl: number    // net option contract P&L (all closed/expired)
  stock_realized_pnl: number      // (strike - avg_cost) × shares on SELL assignments
  total_realized_pnl: number      // options_realized_pnl + stock_realized_pnl
}

export interface PortfolioSummary {
  holdings: Holding[]
  total_cost_usd: number
  total_value_usd: number | null           // equity market value (stocks only)
  total_unrealized_pnl_usd: number | null  // equity unrealized P&L only
  total_unrealized_pnl_pct: number | null
  price_last_updated: string | null
  has_stale_prices: boolean
  cash_balance_usd: number                 // = realized.total_cash (backward compat)
  realized: PortfolioCashAndPnl
}

// ─── Transactions ─────────────────────────────────────────────────────────────

export interface TransactionCreate {
  symbol: string
  type: 'BUY' | 'SELL'
  quantity: number
  price_per_share: number
  price_usd?: number | null
  trade_date: string
  fees?: number
  notes?: string | null
}

export interface Transaction {
  id: string
  symbol: string
  name: string
  asset_type: string
  type: 'BUY' | 'SELL'
  quantity: number
  price_per_share: number
  price_usd: number | null
  trade_date: string
  fees: number
  notes: string | null
  fx_rate_to_usd: number | null
  is_bootstrap: boolean
  source: string | null
  realized_pnl_usd: number | null
  realized_pnl_pct: number | null
}

export interface TransactionUpdate {
  type: 'BUY' | 'SELL'
  quantity: number
  price_per_share: number
  price_usd?: number | null
  trade_date: string
  fees?: number
  notes?: string | null
}

export interface TransactionList {
  transactions: Transaction[]
  total_count: number
}

// ─── Snapshots ────────────────────────────────────────────────────────────────

export interface SnapshotCreate {
  label?: string | null
}

export interface SnapshotUpdate {
  label: string | null
}

export interface AssetChange {
  asset_id: string
  symbol: string
  name: string
  from_quantity: number | null
  to_quantity: number | null
  quantity_change: number | null
  from_value_usd: number | null
  to_value_usd: number | null
  value_change_usd: number | null
  value_change_pct: number | null
  contribution_pct: number | null
}

export interface SnapshotCompareResult {
  from_snapshot_id: string
  from_snapshot_date: string
  from_snapshot_label: string | null
  from_total_value_usd: number | null
  to_snapshot_id: string
  to_snapshot_date: string
  to_snapshot_label: string | null
  to_total_value_usd: number | null
  value_change_usd: number | null
  value_change_pct: number | null
  asset_changes: AssetChange[]
  executive_summary: string
}

export interface SnapshotListItem {
  id: string
  snapshot_date: string
  label: string | null
  total_cost_usd: number | null
  total_value_usd: number | null
  total_return_pct: number | null
}

export interface SnapshotHolding {
  asset_id: string
  symbol: string
  name: string
  asset_type: string
  quantity: number
  avg_cost_usd: number
  cost_basis_usd: number
  price_at_snapshot: number
  value_usd: number
  return_pct: number
  allocation_pct: number
}

export interface SnapshotDetail {
  id: string
  snapshot_date: string
  label: string | null
  total_cost_usd: number | null
  total_value_usd: number | null
  total_return_pct: number | null
  holdings: SnapshotHolding[]
}

// ─── Options ──────────────────────────────────────────────────────────────────

export interface OptionTradeCreate {
  underlying_symbol: string
  option_type: 'CALL' | 'PUT'
  action: 'BUY' | 'SELL'
  strike: number
  expiration_date: string
  quantity: number
  open_date: string
  open_price: number
  open_commission?: number
  exit_date?: string | null
  exit_price?: number | null
  close_commission?: number
  status?: 'OPEN' | 'CLOSED' | 'EXPIRED'
  net_pnl?: number | null
  notes?: string | null
}

export interface OptionTradeUpdate {
  option_type: 'CALL' | 'PUT'
  action: 'BUY' | 'SELL'
  strike: number
  expiration_date: string
  quantity: number
  open_date: string
  open_price: number
  open_commission?: number
  exit_date?: string | null
  exit_price?: number | null
  close_commission?: number
  status?: 'OPEN' | 'CLOSED' | 'EXPIRED'
  net_pnl?: number | null
  notes?: string | null
}

export interface OptionTrade {
  id: string
  underlying_symbol: string
  underlying_name: string
  option_type: 'CALL' | 'PUT'
  action: 'BUY' | 'SELL'
  strike: number
  expiration_date: string
  quantity: number
  open_date: string
  open_price: number
  open_commission: number
  exit_date: string | null
  exit_price: number | null
  close_commission: number
  status: 'OPEN' | 'CLOSED' | 'EXPIRED'
  net_pnl: number | null
  pnl_type: 'cash' | 'realized'
  premium_cost: number
  notes: string | null
}

export interface UnderlyingPnlSummary {
  symbol: string
  name: string
  trade_count: number
  closed_count: number
  expired_count: number
  open_count: number
  total_net_pnl: number
  win_count: number
  win_rate: number
}

export interface OptionsSummary {
  trades: OptionTrade[]
  total_net_pnl: number
  trade_count: number
  closed_count: number
  expired_count: number
  open_count: number
  win_rate: number
  pnl_by_underlying: UnderlyingPnlSummary[]
}

export interface ExpiredOptionResult {
  option_id: string
  symbol: string
  option_type: string
  action: string
  strike: number
  expiration_date: string
  quantity: number
  itm: boolean
  shares_delivered: number
  cash_delta: number
}

export interface ProcessExpiredResult {
  processed: number
  details: ExpiredOptionResult[]
  cash_balance: number
}

// ─── Prices ───────────────────────────────────────────────────────────────────

export interface SymbolRefreshDetail {
  symbol: string
  status: 'ok' | 'failed'
  currency: string
  price_native: number | null
  price_usd: number | null
  error: string | null
}

export interface RefreshResult {
  total_attempted: number
  succeeded: number
  failed: number
  per_symbol: SymbolRefreshDetail[]
  fetched_at: string
  message: string
}
