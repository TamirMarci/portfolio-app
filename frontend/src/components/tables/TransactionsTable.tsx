import { useState, useMemo } from 'react'
import type { Transaction } from '../../api/types'
import AssetSymbolLink from '../AssetSymbolLink'
import { formatUSD, formatPnl, formatPctChange, formatDate, formatNumber } from '../../lib/formatters'
import { TYPE_COLORS } from '../../lib/constants'
import { useDeleteTransaction } from '../../hooks/useDeleteTransaction'
import EditTransactionModal from '../EditTransactionModal'

interface Props {
  transactions: Transaction[]
}

export default function TransactionsTable({ transactions }: Props) {
  const [typeFilter, setTypeFilter] = useState<'ALL' | 'BUY' | 'SELL'>('ALL')
  const [symbolFilter, setSymbolFilter] = useState('')
  const [confirmId, setConfirmId] = useState<string | null>(null)
  const [editTx, setEditTx] = useState<Transaction | null>(null)

  const deleteMutation = useDeleteTransaction()

  const filtered = useMemo(() => {
    return transactions.filter((t) => {
      const matchType = typeFilter === 'ALL' || t.type === typeFilter
      const matchSym = !symbolFilter || t.symbol.toLowerCase().includes(symbolFilter.toLowerCase())
      return matchType && matchSym
    })
  }, [transactions, typeFilter, symbolFilter])

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
          {(['ALL', 'BUY', 'SELL'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                typeFilter === t
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-900/50">
            <tr>
              {['Symbol', 'Type', 'Shares', 'Price', 'Trade Date', 'Fees', 'Realized P&L', 'Yield', ''].map((h) => (
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
            {filtered.map((tx) => (
              <tr key={tx.id} className="table-row-hover">
                <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                  <AssetSymbolLink symbol={tx.symbol} className="font-mono font-semibold text-blue-400" />
                </td>
                <td className="px-4 py-3">
                  <span className={`badge ${TYPE_COLORS[tx.type] ?? 'badge-gray'}`}>{tx.type}</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-300 font-mono">
                  {formatNumber(tx.quantity, 0)}
                </td>
                <td className="px-4 py-3 text-right text-gray-300 font-mono">
                  {formatUSD(tx.price_usd ?? tx.price_per_share)}
                </td>
                <td className="px-4 py-3 text-gray-400">{formatDate(tx.trade_date)}</td>
                <td className="px-4 py-3 text-right text-gray-400 font-mono">{formatUSD(tx.fees)}</td>
                <td
                  className={`px-4 py-3 text-right font-mono ${
                    tx.realized_pnl_usd == null
                      ? 'text-gray-600'
                      : tx.realized_pnl_usd >= 0
                      ? 'text-emerald-400'
                      : 'text-red-400'
                  }`}
                >
                  {formatPnl(tx.realized_pnl_usd)}
                </td>
                <td
                  className={`px-4 py-3 text-right font-mono ${
                    tx.realized_pnl_pct == null
                      ? 'text-gray-600'
                      : tx.realized_pnl_pct >= 0
                      ? 'text-emerald-400'
                      : 'text-red-400'
                  }`}
                >
                  {formatPctChange(tx.realized_pnl_pct)}
                </td>
                {/* Actions column */}
                <td className="px-4 py-3 text-right whitespace-nowrap">
                  {confirmId === tx.id ? (
                    <span className="inline-flex items-center gap-1 text-xs">
                      <span className="text-gray-500 mr-1">Delete?</span>
                      <button
                        onClick={() => handleDelete(tx.id)}
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
                        onClick={() => setEditTx(tx)}
                        className="text-gray-600 hover:text-blue-400 transition-colors px-2 py-1 rounded text-xs"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => setConfirmId(tx.id)}
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
                <td colSpan={9} className="px-4 py-8 text-center text-gray-600">
                  No transactions match the current filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="px-4 py-2 border-t border-gray-800 text-xs text-gray-600">
        {filtered.length} of {transactions.length} transactions
      </div>

      {editTx && (
        <EditTransactionModal transaction={editTx} onClose={() => setEditTx(null)} />
      )}
    </div>
  )
}
