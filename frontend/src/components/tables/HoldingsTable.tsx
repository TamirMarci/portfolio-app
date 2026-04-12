import { useState, useMemo } from 'react'
import { ArrowUpDown, ArrowUp, ArrowDown, AlertTriangle } from 'lucide-react'
import type { Holding } from '../../api/types'
import AssetSymbolLink from '../AssetSymbolLink'
import {
  formatUSD,
  formatPct,
  formatPctChange,
  formatPnl,
  formatNumber,
} from '../../lib/formatters'
import { TYPE_COLORS } from '../../lib/constants'

type SortKey = keyof Holding
type SortDir = 'asc' | 'desc'

interface Props {
  holdings: Holding[]
}

function SortIcon({ col, active, dir }: { col: string; active: string; dir: SortDir }) {
  if (col !== active) return <ArrowUpDown size={13} className="text-gray-600" />
  return dir === 'asc'
    ? <ArrowUp size={13} className="text-blue-400" />
    : <ArrowDown size={13} className="text-blue-400" />
}

function Th({
  label,
  col,
  active,
  dir,
  onSort,
  right,
}: {
  label: string
  col: string
  active: string
  dir: SortDir
  onSort: (c: string) => void
  right?: boolean
}) {
  return (
    <th
      onClick={() => onSort(col)}
      className={`px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer select-none hover:text-gray-300 whitespace-nowrap ${right ? 'text-right' : 'text-left'}`}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        <SortIcon col={col} active={active} dir={dir} />
      </span>
    </th>
  )
}

export default function HoldingsTable({ holdings }: Props) {
  const [sortKey, setSortKey] = useState<string>('current_value_usd')
  const [sortDir, setSortDir] = useState<SortDir>('desc')
  const [filter, setFilter] = useState('')

  function handleSort(col: string) {
    if (col === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(col)
      setSortDir('desc')
    }
  }

  const filtered = useMemo(() => {
    const q = filter.toLowerCase()
    return holdings.filter(
      (h) =>
        h.symbol.toLowerCase().includes(q) ||
        h.name.toLowerCase().includes(q) ||
        h.asset_type.toLowerCase().includes(q)
    )
  }, [holdings, filter])

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      const av = (a as any)[sortKey] ?? -Infinity
      const bv = (b as any)[sortKey] ?? -Infinity
      return sortDir === 'asc' ? (av > bv ? 1 : -1) : av < bv ? 1 : -1
    })
  }, [filtered, sortKey, sortDir])

  return (
    <div className="card overflow-hidden">
      {/* Filter */}
      <div className="p-4 border-b border-gray-800">
        <input
          type="text"
          placeholder="Filter by symbol or name…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-64 px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-900/50">
            <tr>
              <Th label="Symbol" col="symbol" active={sortKey} dir={sortDir} onSort={handleSort} />
              <Th label="Name" col="name" active={sortKey} dir={sortDir} onSort={handleSort} />
              <Th label="Type" col="asset_type" active={sortKey} dir={sortDir} onSort={handleSort} />
              <Th label="Shares" col="quantity" active={sortKey} dir={sortDir} onSort={handleSort} right />
              <Th label="Avg Cost" col="avg_cost_usd" active={sortKey} dir={sortDir} onSort={handleSort} right />
              <Th label="Current Price" col="current_price_usd" active={sortKey} dir={sortDir} onSort={handleSort} right />
              <Th label="Market Value" col="current_value_usd" active={sortKey} dir={sortDir} onSort={handleSort} right />
              <Th label="Unreal. P&L" col="unrealized_pnl_usd" active={sortKey} dir={sortDir} onSort={handleSort} right />
              <Th label="P&L %" col="unrealized_pnl_pct" active={sortKey} dir={sortDir} onSort={handleSort} right />
              <Th label="Alloc." col="allocation_pct" active={sortKey} dir={sortDir} onSort={handleSort} right />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {sorted.map((h) => {
              const pnlPositive = (h.unrealized_pnl_usd ?? 0) >= 0
              return (
                <tr key={h.id} className="table-row-hover">
                  <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                    <div className="flex items-center gap-1.5">
                      <AssetSymbolLink symbol={h.symbol} className="font-mono font-semibold text-blue-400" />
                      {h.price_stale && (
                        <AlertTriangle size={12} className="text-amber-400" aria-label="Price may be outdated" />
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-300 max-w-[200px] truncate">{h.name}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${TYPE_COLORS[h.asset_type] ?? 'badge-gray'}`}>
                      {h.asset_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right text-gray-300 font-mono">
                    {formatNumber(h.quantity, 0)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-400 font-mono">
                    {formatUSD(h.avg_cost_usd)}
                    {h.currency !== 'USD' && (
                      <span className="text-gray-600 text-xs ml-1">({h.currency})</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-300 font-mono">
                    {h.current_price_usd != null ? formatUSD(h.current_price_usd) : '—'}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-gray-100 font-mono">
                    {formatUSD(h.current_value_usd)}
                  </td>
                  <td className={`px-4 py-3 text-right font-mono ${pnlPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                    {formatPnl(h.unrealized_pnl_usd)}
                  </td>
                  <td className={`px-4 py-3 text-right font-mono ${pnlPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                    {formatPctChange(h.unrealized_pnl_pct)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-400 font-mono">
                    {formatPct(h.allocation_pct)}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="px-4 py-2 border-t border-gray-800 text-xs text-gray-600">
        {sorted.length} of {holdings.length} holdings
      </div>
    </div>
  )
}
