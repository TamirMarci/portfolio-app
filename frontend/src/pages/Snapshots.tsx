import { useState } from 'react'
import AssetSymbolLink from '../components/AssetSymbolLink'
import {
  useSnapshots, useSnapshotDetail, useCompareSnapshots,
  useRenameSnapshot, useDeleteSnapshot,
} from '../hooks/useSnapshots'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { formatUSD, formatPct, formatPctChange, formatPnl } from '../lib/formatters'

export default function Snapshots() {
  const { data: list, isLoading: listLoading, isError: listError } = useSnapshots()
  const renameMutation = useRenameSnapshot()
  const deleteMutation = useDeleteSnapshot()

  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [showAnalysis, setShowAnalysis] = useState(false)

  // Rename state
  const [renaming, setRenaming] = useState(false)
  const [renameValue, setRenameValue] = useState('')

  // Delete confirmation state
  const [confirmDelete, setConfirmDelete] = useState(false)

  const effectiveId = selectedId ?? (list && list.length > 0 ? list[0].id : null)
  const { data: detail, isLoading: detailLoading } = useSnapshotDetail(effectiveId)

  // List is sorted newest-first (backend order_by desc); prev snapshot = next index
  const selectedIndex = list ? list.findIndex((s) => s.id === effectiveId) : -1
  const prevSnapshot = list && selectedIndex >= 0 && selectedIndex < list.length - 1
    ? list[selectedIndex + 1]
    : null

  const { data: compareData, isLoading: compareLoading } = useCompareSnapshots(
    showAnalysis && prevSnapshot ? prevSnapshot.id : null,
    showAnalysis && effectiveId ? effectiveId : null,
  )

  if (listLoading) return <LoadingSpinner message="Loading snapshots…" />
  if (listError) return <ErrorMessage message="Could not load snapshots." />

  if (!list || list.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-100">Snapshots</h1>
        <div className="card p-8 text-center text-gray-500 text-sm">
          No snapshots yet. Use the "Create Snapshot" button on the Portfolio page.
        </div>
      </div>
    )
  }

  const selectedSnap = list.find((s) => s.id === effectiveId)
  const returnPositive = (selectedSnap?.total_return_pct ?? 0) >= 0

  const handleSelect = (id: string) => {
    setSelectedId(id)
    setShowAnalysis(false)
    setRenaming(false)
    setConfirmDelete(false)
  }

  const startRename = () => {
    setRenameValue(selectedSnap?.label ?? selectedSnap?.snapshot_date ?? '')
    setRenaming(true)
    setConfirmDelete(false)
  }

  const commitRename = () => {
    if (!effectiveId) return
    renameMutation.mutate(
      { id: effectiveId, body: { label: renameValue.trim() || null } },
      { onSuccess: () => setRenaming(false) },
    )
  }

  const commitDelete = () => {
    if (!effectiveId) return
    deleteMutation.mutate(effectiveId, {
      onSuccess: () => {
        setSelectedId(null)
        setConfirmDelete(false)
        setShowAnalysis(false)
      },
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <h1 className="text-2xl font-bold text-gray-100">Snapshots</h1>

      {/* Snapshot tabs */}
      <div className="flex flex-wrap gap-2">
        {list.map((snap) => (
          <button
            key={snap.id}
            onClick={() => handleSelect(snap.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              effectiveId === snap.id
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'text-gray-500 border border-gray-700 hover:text-gray-300 hover:border-gray-600'
            }`}
          >
            {snap.label ?? snap.snapshot_date}
          </button>
        ))}
      </div>

      {/* Selected snapshot header: stats + actions */}
      {selectedSnap && (
        <div className="space-y-3">
          {/* Rename bar or title + action buttons */}
          {renaming ? (
            <div className="flex items-center gap-2">
              <input
                autoFocus
                className="px-3 py-1.5 text-sm bg-gray-800 border border-blue-500 rounded-lg text-gray-200 focus:outline-none w-56"
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') commitRename()
                  if (e.key === 'Escape') setRenaming(false)
                }}
              />
              <button
                onClick={commitRename}
                disabled={renameMutation.isPending}
                className="px-3 py-1.5 text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {renameMutation.isPending ? 'Saving…' : 'Save'}
              </button>
              <button
                onClick={() => setRenaming(false)}
                className="px-3 py-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : confirmDelete ? (
            <div className="flex items-center gap-3 text-sm">
              <span className="text-gray-400">Delete <span className="text-gray-200 font-medium">{selectedSnap.label ?? selectedSnap.snapshot_date}</span>? This cannot be undone.</span>
              <button
                onClick={commitDelete}
                disabled={deleteMutation.isPending}
                className="px-3 py-1.5 text-xs font-medium bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {deleteMutation.isPending ? 'Deleting…' : 'Delete'}
              </button>
              <button
                onClick={() => setConfirmDelete(false)}
                className="px-3 py-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">{selectedSnap.snapshot_date}</span>
              <button
                onClick={startRename}
                title="Rename"
                className="text-xs text-gray-600 hover:text-gray-300 transition-colors px-1.5 py-0.5 rounded hover:bg-gray-800"
              >
                ✏️ Rename
              </button>
              <button
                onClick={() => setConfirmDelete(true)}
                title="Delete"
                className="text-xs text-gray-600 hover:text-red-400 transition-colors px-1.5 py-0.5 rounded hover:bg-gray-800"
              >
                🗑 Delete
              </button>
              {prevSnapshot && (
                <button
                  onClick={() => setShowAnalysis((v) => !v)}
                  className={`ml-auto px-4 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                    showAnalysis
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                  }`}
                >
                  {showAnalysis ? 'Hide Analysis' : 'Analyze Progress'}
                </button>
              )}
            </div>
          )}

          {/* Stat cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="stat-card">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Total Value</p>
              <p className="text-2xl font-semibold text-gray-100">{formatUSD(selectedSnap.total_value_usd)}</p>
            </div>
            <div className="stat-card">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Cost Basis</p>
              <p className="text-2xl font-semibold text-gray-100">{formatUSD(selectedSnap.total_cost_usd)}</p>
            </div>
            <div className="stat-card">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Return</p>
              <p className={`text-2xl font-semibold ${returnPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                {formatPctChange(selectedSnap.total_return_pct)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Analysis panel */}
      {showAnalysis && prevSnapshot && (
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-800">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-0.5">Progress Analysis</p>
            <h3 className="text-sm font-semibold text-gray-300">
              {prevSnapshot.label ?? prevSnapshot.snapshot_date}
              {' → '}
              {selectedSnap?.label ?? selectedSnap?.snapshot_date}
            </h3>
          </div>

          {compareLoading && <div className="px-5 py-6"><LoadingSpinner message="Computing…" /></div>}

          {compareData && (
            <>
              {/* Executive summary */}
              <div className="px-5 py-4 border-b border-gray-800 bg-gray-900/40">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Summary</p>
                <p className="text-sm text-gray-300 leading-relaxed">{compareData.executive_summary}</p>
              </div>

              {/* Portfolio-level metrics */}
              <div className="grid grid-cols-3 divide-x divide-gray-800 border-b border-gray-800">
                {[
                  { label: 'From Value', value: formatUSD(compareData.from_total_value_usd), colored: false },
                  { label: 'To Value',   value: formatUSD(compareData.to_total_value_usd),   colored: false },
                  {
                    label: 'Change',
                    value: compareData.value_change_usd != null ? formatPnl(compareData.value_change_usd) : '—',
                    sub: formatPctChange(compareData.value_change_pct),
                    colored: true,
                    positive: (compareData.value_change_usd ?? 0) >= 0,
                  },
                ].map(({ label, value, sub, colored, positive }) => (
                  <div key={label} className="px-5 py-4">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">{label}</p>
                    <p className={`text-xl font-semibold ${colored ? (positive ? 'text-emerald-400' : 'text-red-400') : 'text-gray-100'}`}>
                      {value}
                    </p>
                    {sub && (
                      <p className={`text-sm mt-0.5 ${positive ? 'text-emerald-400' : 'text-red-400'}`}>{sub}</p>
                    )}
                  </div>
                ))}
              </div>

              {/* Per-asset table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-900/50">
                    <tr>
                      {['Symbol', 'Name', 'From Value', 'To Value', 'Change', 'Change %', 'Contribution'].map((h) => (
                        <th key={h} className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider text-left whitespace-nowrap">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800">
                    {compareData.asset_changes.map((ac) => {
                      const pos = (ac.value_change_usd ?? 0) >= 0
                      return (
                        <tr key={ac.asset_id} className="table-row-hover">
                          <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                            <AssetSymbolLink symbol={ac.symbol} className="font-mono font-semibold text-blue-400" />
                          </td>
                          <td className="px-4 py-3 text-gray-300 max-w-[160px] truncate">{ac.name}</td>
                          <td className="px-4 py-3 text-right text-gray-400 font-mono">{formatUSD(ac.from_value_usd)}</td>
                          <td className="px-4 py-3 text-right text-gray-300 font-mono">{formatUSD(ac.to_value_usd)}</td>
                          <td className={`px-4 py-3 text-right font-mono font-semibold ${pos ? 'text-emerald-400' : 'text-red-400'}`}>
                            {ac.value_change_usd != null ? formatPnl(ac.value_change_usd) : '—'}
                          </td>
                          <td className={`px-4 py-3 text-right font-mono ${pos ? 'text-emerald-400' : 'text-red-400'}`}>
                            {formatPctChange(ac.value_change_pct)}
                          </td>
                          <td className={`px-4 py-3 text-right font-mono text-xs ${pos ? 'text-emerald-400' : 'text-red-400'}`}>
                            {ac.contribution_pct != null ? formatPctChange(ac.contribution_pct, 1) : '—'}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

      {/* Holdings detail table */}
      {detailLoading && <LoadingSpinner message="Loading snapshot details…" />}

      {detail && (
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-800">
            <h3 className="text-sm font-semibold text-gray-300">
              Holdings at {detail.label ?? detail.snapshot_date}
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-900/50">
                <tr>
                  {['Symbol', 'Name', 'Shares', 'Avg Cost', 'Price at Snapshot', 'Value', 'Cost Basis', 'Return', 'Allocation'].map((h) => (
                    <th key={h} className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider text-left whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {detail.holdings.map((h) => {
                  const pos = h.return_pct >= 0
                  return (
                    <tr key={h.asset_id} className="table-row-hover">
                      <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                        <AssetSymbolLink symbol={h.symbol} className="font-mono font-semibold text-blue-400" />
                      </td>
                      <td className="px-4 py-3 text-gray-300 max-w-[180px] truncate">{h.name}</td>
                      <td className="px-4 py-3 text-right text-gray-300 font-mono">{h.quantity.toLocaleString()}</td>
                      <td className="px-4 py-3 text-right text-gray-400 font-mono">{formatUSD(h.avg_cost_usd)}</td>
                      <td className="px-4 py-3 text-right text-gray-300 font-mono">{formatUSD(h.price_at_snapshot)}</td>
                      <td className="px-4 py-3 text-right font-semibold text-gray-100 font-mono">{formatUSD(h.value_usd)}</td>
                      <td className="px-4 py-3 text-right text-gray-400 font-mono">{formatUSD(h.cost_basis_usd)}</td>
                      <td className={`px-4 py-3 text-right font-mono ${pos ? 'text-emerald-400' : 'text-red-400'}`}>
                        {formatPctChange(h.return_pct)}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-400 font-mono">{formatPct(h.allocation_pct)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
