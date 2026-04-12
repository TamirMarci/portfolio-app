import { useState } from 'react'
import { RefreshCw, CheckCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { useRefreshPrices } from '../hooks/useRefreshPrices'
import { formatDateTime } from '../lib/formatters'
import type { SymbolRefreshDetail } from '../api/types'

function FailureList({ failures }: { failures: SymbolRefreshDetail[] }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="text-xs">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-1 text-amber-400 hover:text-amber-300 transition-colors"
      >
        <AlertCircle size={12} />
        <span>{failures.length} symbol{failures.length !== 1 ? 's' : ''} failed</span>
        {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {open && (
        <ul className="mt-1.5 space-y-1 max-w-xs">
          {failures.map(f => (
            <li key={f.symbol} className="rounded bg-gray-800 px-2 py-1">
              <span className="font-medium text-gray-200">{f.symbol}</span>
              <span className="text-gray-500 ml-1">({f.currency})</span>
              {f.error && (
                <p className="text-red-400 mt-0.5 leading-tight">{f.error}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function PriceRefreshButton() {
  const { mutate, isPending, isSuccess, isError, data } = useRefreshPrices()

  // Use ?. throughout so a stale/mismatched backend response never crashes the component.
  // If per_symbol is absent (old backend still running), failures defaults to [].
  const failures = data?.per_symbol?.filter(s => s.status === 'failed') ?? []
  const succeeded = data?.succeeded ?? 0
  const total = data?.total_attempted ?? 0
  const allFailed = total > 0 && succeeded === 0

  return (
    <div className="flex flex-col items-end gap-1.5">
      <div className="flex items-center gap-3">
        {/* Success status — shown when at least one symbol refreshed */}
        {isSuccess && data && !allFailed && (
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <CheckCircle size={13} className="text-emerald-500" />
            <span>
              {succeeded}/{total} updated · {formatDateTime(data.fetched_at)}
            </span>
          </div>
        )}

        {/* All-failed state — show count and timestamp so there is always feedback */}
        {isSuccess && data && allFailed && (
          <div className="flex items-center gap-1.5 text-xs text-amber-400">
            <AlertCircle size={13} />
            <span>All {total} symbols failed · {formatDateTime(data.fetched_at)}</span>
          </div>
        )}

        {/* Network / server error (the mutation request itself failed) */}
        {isError && (
          <div className="flex items-center gap-1 text-xs text-red-400">
            <AlertCircle size={13} />
            <span>Request failed — check backend logs</span>
          </div>
        )}

        <button
          onClick={() => mutate()}
          disabled={isPending}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
        >
          <RefreshCw size={14} className={isPending ? 'animate-spin' : ''} />
          {isPending ? 'Refreshing…' : 'Refresh Prices'}
        </button>
      </div>

      {/* Per-symbol failure list — shown below the button row when failures exist */}
      {isSuccess && failures.length > 0 && (
        <FailureList failures={failures} />
      )}
    </div>
  )
}
