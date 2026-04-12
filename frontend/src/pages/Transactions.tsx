import { useState } from 'react'
import { useTransactions } from '../hooks/useTransactions'
import TransactionsTable from '../components/tables/TransactionsTable'
import AddTransactionModal from '../components/AddTransactionModal'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function Transactions() {
  const { data, isLoading, isError, error } = useTransactions()
  const [showModal, setShowModal] = useState(false)

  if (isLoading) return <LoadingSpinner message="Loading transactions…" />
  if (isError) return <ErrorMessage message={(error as Error).message} />
  if (!data) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Transactions</h1>
          <p className="text-sm text-gray-500 mt-1">
            {data.total_count} transaction{data.total_count !== 1 ? 's' : ''} recorded
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
        >
          + Add Transaction
        </button>
      </div>

      {data.total_count === 0 ? (
        <div className="card p-8 text-center text-gray-500 text-sm">
          No transactions found. Add one manually or run the Excel import.
        </div>
      ) : (
        <TransactionsTable transactions={data.transactions} />
      )}

      {showModal && <AddTransactionModal onClose={() => setShowModal(false)} />}
    </div>
  )
}
