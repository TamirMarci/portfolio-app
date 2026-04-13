import { useState } from 'react'
import { useTransactions } from '../hooks/useTransactions'
import TransactionsTable from '../components/tables/TransactionsTable'
import AddTransactionModal from '../components/AddTransactionModal'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import type { TransactionDateFilter } from '../api/transactions'

type Preset = 'ALL' | 'WEEK' | 'MONTH' | 'YEAR' | 'YTD' | 'CUSTOM'

function toISO(d: Date): string {
  return d.toISOString().slice(0, 10)
}

function presetToFilter(preset: Preset): TransactionDateFilter {
  const today = new Date()
  if (preset === 'WEEK') {
    const d = new Date(today); d.setDate(d.getDate() - 7)
    return { start_date: toISO(d), end_date: toISO(today) }
  }
  if (preset === 'MONTH') {
    const d = new Date(today); d.setMonth(d.getMonth() - 1)
    return { start_date: toISO(d), end_date: toISO(today) }
  }
  if (preset === 'YEAR') {
    const d = new Date(today); d.setFullYear(d.getFullYear() - 1)
    return { start_date: toISO(d), end_date: toISO(today) }
  }
  if (preset === 'YTD') {
    return { start_date: `${today.getFullYear()}-01-01`, end_date: toISO(today) }
  }
  return {}
}

const PRESETS: { key: Preset; label: string }[] = [
  { key: 'ALL',   label: 'All' },
  { key: 'WEEK',  label: 'Past week' },
  { key: 'MONTH', label: 'Past month' },
  { key: 'YEAR',  label: 'Past year' },
  { key: 'YTD',   label: 'YTD' },
  { key: 'CUSTOM', label: 'Custom' },
]

export default function Transactions() {
  const [preset, setPreset] = useState<Preset>('ALL')
  const [customStart, setCustomStart] = useState('')
  const [customEnd, setCustomEnd] = useState('')
  const [showModal, setShowModal] = useState(false)

  const filter: TransactionDateFilter =
    preset === 'CUSTOM'
      ? { start_date: customStart || undefined, end_date: customEnd || undefined }
      : presetToFilter(preset)

  const { data, isLoading, isError, error } = useTransactions(filter)

  const handlePreset = (p: Preset) => {
    setPreset(p)
    if (p !== 'CUSTOM') { setCustomStart(''); setCustomEnd('') }
  }

  if (isLoading) return <LoadingSpinner message="Loading transactions…" />
  if (isError) return <ErrorMessage message={(error as Error).message} />
  if (!data) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Transactions</h1>
          <p className="text-sm text-gray-500 mt-1">
            {data.total_count} transaction{data.total_count !== 1 ? 's' : ''}
            {preset !== 'ALL' && ' in selected range'}
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
        >
          + Add Transaction
        </button>
      </div>

      {/* Date range filter */}
      <div className="flex flex-wrap items-center gap-2">
        {PRESETS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => handlePreset(key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              preset === key
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
            }`}
          >
            {label}
          </button>
        ))}

        {preset === 'CUSTOM' && (
          <div className="flex items-center gap-2 ml-1">
            <input
              type="date"
              value={customStart}
              onChange={(e) => setCustomStart(e.target.value)}
              className="px-2 py-1.5 text-xs bg-gray-800 border border-gray-700 rounded-lg text-gray-300 focus:outline-none focus:border-blue-500 [color-scheme:dark]"
            />
            <span className="text-gray-600 text-xs">—</span>
            <input
              type="date"
              value={customEnd}
              onChange={(e) => setCustomEnd(e.target.value)}
              className="px-2 py-1.5 text-xs bg-gray-800 border border-gray-700 rounded-lg text-gray-300 focus:outline-none focus:border-blue-500 [color-scheme:dark]"
            />
          </div>
        )}
      </div>

      {data.total_count === 0 ? (
        <div className="card p-8 text-center text-gray-500 text-sm">
          {preset === 'ALL'
            ? 'No transactions found. Add one manually or run the Excel import.'
            : 'No transactions in the selected date range.'}
        </div>
      ) : (
        <TransactionsTable transactions={data.transactions} />
      )}

      {showModal && <AddTransactionModal onClose={() => setShowModal(false)} />}
    </div>
  )
}
