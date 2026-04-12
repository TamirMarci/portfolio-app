import { useState } from 'react'
import { useHoldings } from '../hooks/useHoldings'
import { useCreateSnapshot } from '../hooks/useSnapshots'
import HoldingsTable from '../components/tables/HoldingsTable'
import StatCard from '../components/StatCard'
import Modal from '../components/Modal'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { formatUSD, formatPnl, formatPctChange, formatDateTime } from '../lib/formatters'

export default function Dashboard() {
  const { data, isLoading, isError, error } = useHoldings()
  const createSnapshot = useCreateSnapshot()
  const [showSnapshotModal, setShowSnapshotModal] = useState(false)
  const [snapshotLabel, setSnapshotLabel] = useState('')

  if (isLoading) return <LoadingSpinner message="Loading portfolio…" />
  if (isError) return <ErrorMessage message={(error as Error).message} />
  if (!data) return null

  const {
    holdings,
    total_cost_usd,
    total_value_usd,
    total_unrealized_pnl_usd,
    total_unrealized_pnl_pct,
    price_last_updated,
    has_stale_prices,
    cash_balance_usd,
  } = data

  const pnlPositive = (total_unrealized_pnl_usd ?? 0) >= 0

  const handleCreateSnapshot = (e: React.FormEvent) => {
    e.preventDefault()
    createSnapshot.mutate(
      { label: snapshotLabel.trim() || null },
      {
        onSuccess: () => {
          setShowSnapshotModal(false)
          setSnapshotLabel('')
        },
      }
    )
  }

  const snapshotError = createSnapshot.error
    ? ((createSnapshot.error as any)?.response?.data?.detail ?? 'Failed to create snapshot')
    : null

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Portfolio</h1>
          {price_last_updated && (
            <p className="text-xs text-gray-500 mt-1">
              Prices as of {formatDateTime(price_last_updated)}
              {has_stale_prices && (
                <span className="ml-2 text-amber-400">· Some prices may be outdated</span>
              )}
            </p>
          )}
          {!price_last_updated && (
            <p className="text-xs text-amber-400 mt-1">
              No prices loaded — click "Refresh Prices" to fetch live data.
            </p>
          )}
        </div>
        <button
          onClick={() => setShowSnapshotModal(true)}
          className="px-4 py-2 text-sm font-medium bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg transition-colors"
        >
          Create Snapshot
        </button>
      </div>

      {/* Summary stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          label="Market Value"
          value={formatUSD(total_value_usd)}
          sub={total_value_usd == null ? 'Refresh prices' : undefined}
        />
        <StatCard
          label="Cash Balance"
          value={formatUSD(cash_balance_usd)}
          sub="From option deliveries"
        />
        <StatCard
          label="Total Cost Basis"
          value={formatUSD(total_cost_usd)}
        />
        <StatCard
          label="Unrealized P&L"
          value={formatPnl(total_unrealized_pnl_usd)}
          valueClass={
            total_unrealized_pnl_usd == null
              ? 'text-gray-400'
              : pnlPositive
              ? 'text-emerald-400'
              : 'text-red-400'
          }
        />
        <StatCard
          label="Return"
          value={formatPctChange(total_unrealized_pnl_pct)}
          valueClass={
            total_unrealized_pnl_pct == null
              ? 'text-gray-400'
              : pnlPositive
              ? 'text-emerald-400'
              : 'text-red-400'
          }
          sub={`${holdings.length} positions`}
        />
      </div>

      {/* Holdings table */}
      <HoldingsTable holdings={holdings} />

      {/* Create snapshot modal */}
      {showSnapshotModal && (
        <Modal title="Create Snapshot" onClose={() => setShowSnapshotModal(false)}>
          <form onSubmit={handleCreateSnapshot} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">
                Label <span className="text-gray-600">(optional)</span>
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 text-sm bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500"
                placeholder={`e.g. Q1 ${new Date().getFullYear()}`}
                value={snapshotLabel}
                onChange={(e) => setSnapshotLabel(e.target.value)}
                autoFocus
              />
              <p className="text-xs text-gray-600 mt-1">
                Snapshot date: {new Date().toISOString().slice(0, 10)}
              </p>
            </div>
            {snapshotError && (
              <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                {snapshotError}
              </p>
            )}
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowSnapshotModal(false)}
                className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createSnapshot.isPending}
                className="px-5 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white rounded-lg transition-colors"
              >
                {createSnapshot.isPending ? 'Saving…' : 'Save Snapshot'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
