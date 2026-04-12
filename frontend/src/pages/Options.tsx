import { useEffect, useState } from 'react'
import { useOptions, useProcessExpiredOptions } from '../hooks/useOptions'
import OptionsTable from '../components/tables/OptionsTable'
import AddOptionTradeModal from '../components/AddOptionTradeModal'
import PnlBar from '../components/charts/PnlBar'
import StatCard from '../components/StatCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { formatUSD, formatPct } from '../lib/formatters'
import type { ProcessExpiredResult } from '../api/types'

export default function Options() {
  const { data, isLoading, isError, error } = useOptions()
  const processExpired = useProcessExpiredOptions()
  const [showModal, setShowModal] = useState(false)
  const [expiredResult, setExpiredResult] = useState<ProcessExpiredResult | null>(null)

  // Run expired option processing once on mount
  useEffect(() => {
    processExpired.mutate(undefined, {
      onSuccess: (result) => {
        if (result.processed > 0) {
          setExpiredResult(result)
        }
      },
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (isLoading) return <LoadingSpinner message="Loading options data…" />
  if (isError) return <ErrorMessage message={(error as Error).message} />
  if (!data) return null

  const {
    trades,
    total_net_pnl,
    trade_count,
    closed_count,
    expired_count,
    open_count,
    win_rate,
    pnl_by_underlying,
  } = data

  const pnlPositive = total_net_pnl >= 0

  const barData = pnl_by_underlying.map((u) => ({
    symbol: u.symbol,
    net_pnl: u.total_net_pnl,
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-100">Options</h1>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
        >
          + Add Trade
        </button>
      </div>

      {/* Expired option processing result banner */}
      {expiredResult && expiredResult.processed > 0 && (
        <div className="card px-5 py-4 border border-amber-500/20 bg-amber-500/5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-amber-400 mb-1">
                {expiredResult.processed} expired option{expiredResult.processed !== 1 ? 's' : ''} processed
              </p>
              <div className="space-y-1">
                {expiredResult.details.map((d) => (
                  <p key={d.option_id} className="text-xs text-gray-400">
                    <span className="font-mono text-blue-400">{d.symbol}</span>{' '}
                    {d.action} {d.option_type} @ {formatUSD(d.strike)} exp {d.expiration_date}
                    {' — '}
                    {d.itm ? (
                      <span className="text-amber-300">
                        ITM: {d.shares_delivered} shares delivered,{' '}
                        {d.cash_delta >= 0 ? '+' : ''}{formatUSD(d.cash_delta)} cash
                      </span>
                    ) : (
                      <span className="text-gray-500">OTM — expired worthless</span>
                    )}
                  </p>
                ))}
              </div>
            </div>
            <button
              onClick={() => setExpiredResult(null)}
              className="text-gray-600 hover:text-gray-400 text-xs shrink-0"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          label="Total Net P&L"
          value={formatUSD(total_net_pnl)}
          valueClass={pnlPositive ? 'text-emerald-400' : 'text-red-400'}
        />
        <StatCard label="Trades" value={String(trade_count)} />
        <StatCard label="Open" value={String(open_count)} valueClass="text-blue-400" />
        <StatCard
          label="Closed / Expired"
          value={`${closed_count} / ${expired_count}`}
          valueClass="text-gray-300"
        />
        <StatCard
          label="Win Rate"
          value={formatPct(win_rate)}
          sub="Closed + expired"
          valueClass={win_rate >= 0.5 ? 'text-emerald-400' : 'text-amber-400'}
        />
      </div>

      {/* Per-underlying summary table */}
      {pnl_by_underlying.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PnlBar data={barData} title="P&L by Underlying" />

          <div className="card overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-800">
              <h3 className="text-sm font-semibold text-gray-300">By Underlying</h3>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-gray-900/50">
                <tr>
                  {['Symbol', 'Trades', 'Open', 'Closed', 'Expired', 'Win Rate', 'Net P&L'].map((h) => (
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
                {pnl_by_underlying.map((u) => {
                  const pos = u.total_net_pnl >= 0
                  return (
                    <tr key={u.symbol} className="table-row-hover">
                      <td className="px-4 py-3 font-mono font-semibold text-blue-400">{u.symbol}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{u.trade_count}</td>
                      <td className="px-4 py-3 text-right text-blue-400">{u.open_count}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{u.closed_count}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{u.expired_count}</td>
                      <td className="px-4 py-3 text-right text-gray-300">
                        {formatPct(u.win_rate)}
                      </td>
                      <td className={`px-4 py-3 text-right font-semibold font-mono ${pos ? 'text-emerald-400' : 'text-red-400'}`}>
                        {formatUSD(u.total_net_pnl)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Full trades table */}
      <div>
        <h2 className="text-lg font-semibold text-gray-200 mb-3">All Trades</h2>
        {trade_count === 0 ? (
          <div className="card p-8 text-center text-gray-500 text-sm">
            No option trades recorded. Add one manually or run the Excel import.
          </div>
        ) : (
          <OptionsTable trades={trades} />
        )}
      </div>

      {showModal && <AddOptionTradeModal onClose={() => setShowModal(false)} />}
    </div>
  )
}
