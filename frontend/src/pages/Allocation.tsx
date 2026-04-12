import { useMemo } from 'react'
import { useHoldings } from '../hooks/useHoldings'
import AllocationPie from '../components/charts/AllocationPie'
import AssetSymbolLink from '../components/AssetSymbolLink'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { formatUSD, formatPct } from '../lib/formatters'

export default function Allocation() {
  const { data, isLoading, isError, error } = useHoldings()

  const bySymbol = useMemo(() => {
    if (!data) return []
    return data.holdings
      .filter((h) => h.current_value_usd != null)
      .sort((a, b) => (b.current_value_usd ?? 0) - (a.current_value_usd ?? 0))
      .map((h) => ({ name: h.symbol, value: h.current_value_usd! }))
  }, [data])

  const byType = useMemo(() => {
    if (!data) return []
    const map: Record<string, number> = {}
    data.holdings.forEach((h) => {
      if (h.current_value_usd != null) {
        map[h.asset_type] = (map[h.asset_type] ?? 0) + h.current_value_usd
      }
    })
    return Object.entries(map).map(([name, value]) => ({ name, value }))
  }, [data])

  if (isLoading) return <LoadingSpinner message="Loading allocation data…" />
  if (isError) return <ErrorMessage message={(error as Error).message} />
  if (!data) return null

  const hasValues = bySymbol.length > 0

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-100">Allocation</h1>

      {!hasValues && (
        <p className="text-gray-500 text-sm">
          No current prices loaded. Refresh prices to see allocation charts.
        </p>
      )}

      {hasValues && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AllocationPie data={bySymbol} title="By Position" />
            <AllocationPie data={byType} title="By Asset Type" />
          </div>

          {/* Breakdown table */}
          <div className="card overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-800">
              <h3 className="text-sm font-semibold text-gray-300">Position Breakdown</h3>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-gray-900/50">
                <tr>
                  {['Symbol', 'Name', 'Type', 'Market Value', 'Allocation', 'Cost Basis', 'Weight by Cost'].map((h) => (
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
                {data.holdings
                  .filter((h) => h.current_value_usd != null)
                  .sort((a, b) => (b.current_value_usd ?? 0) - (a.current_value_usd ?? 0))
                  .map((h) => (
                    <tr key={h.id} className="table-row-hover">
                      <td className="px-4 py-3 font-mono font-semibold text-blue-400">
                        <AssetSymbolLink symbol={h.symbol} className="font-mono font-semibold text-blue-400" />
                      </td>
                      <td className="px-4 py-3 text-gray-300 max-w-[200px] truncate">{h.name}</td>
                      <td className="px-4 py-3 text-gray-500">{h.asset_type}</td>
                      <td className="px-4 py-3 text-right font-semibold text-gray-100 font-mono">
                        {formatUSD(h.current_value_usd)}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-300 font-mono">
                        {formatPct(h.allocation_pct)}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-400 font-mono">
                        {formatUSD(h.cost_basis_usd)}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-400 font-mono">
                        {data.total_cost_usd > 0
                          ? formatPct(h.cost_basis_usd / data.total_cost_usd)
                          : '—'}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
