import { useState, useMemo } from 'react'
import type { OptionTrade } from '../../api/types'
import AssetSymbolLink from '../AssetSymbolLink'
import { formatUSD, formatPnl, formatDate, formatNumber } from '../../lib/formatters'
import { STATUS_COLORS, TYPE_COLORS } from '../../lib/constants'
import { useDeleteOptionTrade } from '../../hooks/useDeleteOptionTrade'
import EditOptionTradeModal from '../EditOptionTradeModal'

interface Props {
  trades: OptionTrade[]
}

export default function OptionsTable({ trades }: Props) {
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'OPEN' | 'CLOSED' | 'EXPIRED'>('ALL')
  const [symbolFilter, setSymbolFilter] = useState('')
  const [confirmId, setConfirmId] = useState<string | null>(null)
  const [editTrade, setEditTrade] = useState<OptionTrade | null>(null)

  const deleteMutation = useDeleteOptionTrade()

  const filtered = useMemo(() => {
    return trades.filter((t) => {
      const matchStatus = statusFilter === 'ALL' || t.status === statusFilter
      const matchSym = !symbolFilter || t.underlying_symbol.toLowerCase().includes(symbolFilter.toLowerCase())
      return matchStatus && matchSym
    })
  }, [trades, statusFilter, symbolFilter])

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id, { onSuccess: () => setConfirmId(null) })
  }

  return (
    <div className="card overflow-hidden">
      {/* Filters */}
      <div className="p-4 border-b border-gray-800 flex gap-3">
        <input
          type="text"
          placeholder="Filter by symbol…"
          value={symbolFilter}
          onChange={(e) => setSymbolFilter(e.target.value)}
          className="w-48 px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500"
        />
        <div className="flex gap-1">
          {(['ALL', 'OPEN', 'CLOSED', 'EXPIRED'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                statusFilter === s
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-900/50">
            <tr>
              {[
                'Underlying', 'Open Date', 'Type', 'Action', 'Strike',
                'Expiry', 'Qty', 'Premium/Cost', 'Open Price', 'Exit Date', 'Exit Price',
                'Status', 'Net P&L', '',
              ].map((h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider text-left whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {filtered.map((t) => (
              <tr key={t.id} className="table-row-hover">
                <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                  <AssetSymbolLink symbol={t.underlying_symbol} className="font-mono font-semibold text-blue-400" />
                </td>
                <td className="px-4 py-3 text-gray-400">{formatDate(t.open_date)}</td>
                <td className="px-4 py-3">
                  <span className={`badge ${TYPE_COLORS[t.option_type] ?? 'badge-gray'}`}>
                    {t.option_type}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`badge ${TYPE_COLORS[t.action] ?? 'badge-gray'}`}>
                    {t.action}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-gray-300 font-mono">
                  ${formatNumber(t.strike)}
                </td>
                <td className="px-4 py-3 text-gray-400">{formatDate(t.expiration_date)}</td>
                <td className="px-4 py-3 text-right text-gray-300 font-mono">
                  {formatNumber(t.quantity, 0)}
                </td>
                <td className="px-4 py-3 text-right text-gray-300 font-mono">
                  {formatUSD(t.premium_cost)}
                </td>
                <td className="px-4 py-3 text-right text-gray-300 font-mono">
                  ${formatNumber(t.open_price)}
                </td>
                <td className="px-4 py-3 text-gray-400">{formatDate(t.exit_date)}</td>
                <td className="px-4 py-3 text-right text-gray-400 font-mono">
                  {t.exit_price != null ? `$${formatNumber(t.exit_price)}` : '—'}
                </td>
                <td className="px-4 py-3">
                  <span className={`badge ${STATUS_COLORS[t.status] ?? 'badge-gray'}`}>
                    {t.status}
                  </span>
                </td>
                <td
                  className={`px-4 py-3 text-right font-mono font-semibold ${
                    t.net_pnl == null
                      ? 'text-gray-600'
                      : t.net_pnl >= 0
                      ? 'text-emerald-400'
                      : 'text-red-400'
                  }`}
                >
                  <div className="flex flex-col items-end">
                    <span>{formatPnl(t.net_pnl)}</span>
                    <span className="text-xs text-gray-500 capitalize">{t.pnl_type}</span>
                  </div>
                </td>
                {/* Actions column */}
                <td className="px-4 py-3 text-right whitespace-nowrap">
                  {confirmId === t.id ? (
                    <span className="inline-flex items-center gap-1 text-xs">
                      <span className="text-gray-500 mr-1">Delete?</span>
                      <button
                        onClick={() => handleDelete(t.id)}
                        disabled={deleteMutation.isPending}
                        className="px-2 py-1 rounded text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setConfirmId(null)}
                        className="px-2 py-1 rounded text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
                      >
                        No
                      </button>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1">
                      <button
                        onClick={() => setEditTrade(t)}
                        className="text-gray-600 hover:text-blue-400 transition-colors px-2 py-1 rounded text-xs"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setConfirmId(t.id)}
                        className="text-gray-600 hover:text-red-400 transition-colors px-2 py-1 rounded text-xs"
                      >
                        Delete
                      </button>
                    </span>
                  )}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={14} className="px-4 py-8 text-center text-gray-600">
                  No trades match the current filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="px-4 py-2 border-t border-gray-800 text-xs text-gray-600">
        {filtered.length} of {trades.length} trades
      </div>

      {editTrade && (
        <EditOptionTradeModal trade={editTrade} onClose={() => setEditTrade(null)} />
      )}
    </div>
  )
}
