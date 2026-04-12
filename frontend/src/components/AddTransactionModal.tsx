import { useState } from 'react'
import Modal from './Modal'
import { useCreateTransaction } from '../hooks/useCreateTransaction'
import type { TransactionCreate } from '../api/types'

interface Props {
  onClose: () => void
}

function extractError(err: unknown): string {
  const detail = (err as any)?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d: any) => d.msg ?? String(d)).join('; ')
  return (err as Error)?.message ?? 'An unexpected error occurred'
}

const FIELD_CLASS =
  'w-full px-3 py-2 text-sm bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500'

const LABEL_CLASS = 'block text-xs font-medium text-gray-400 mb-1'

export default function AddTransactionModal({ onClose }: Props) {
  const mutation = useCreateTransaction()

  const [form, setForm] = useState({
    symbol: '',
    type: 'BUY' as 'BUY' | 'SELL',
    quantity: '',
    price_per_share: '',
    trade_date: '',
    fees: '',
    notes: '',
  })

  const set = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const body: TransactionCreate = {
      symbol: form.symbol.trim().toUpperCase(),
      type: form.type,
      quantity: parseFloat(form.quantity),
      price_per_share: parseFloat(form.price_per_share),
      trade_date: form.trade_date,
      fees: form.fees ? parseFloat(form.fees) : 0,
      notes: form.notes.trim() || null,
    }

    mutation.mutate(body, { onSuccess: onClose })
  }

  const errorMsg = mutation.error ? extractError(mutation.error) : null

  return (
    <Modal title="Add Transaction" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Symbol */}
        <div>
          <label className={LABEL_CLASS}>Symbol *</label>
          <input
            required
            className={FIELD_CLASS}
            placeholder="e.g. AAPL"
            value={form.symbol}
            onChange={(e) => set('symbol', e.target.value)}
          />
        </div>

        {/* Type */}
        <div>
          <label className={LABEL_CLASS}>Type *</label>
          <div className="flex gap-2">
            {(['BUY', 'SELL'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => set('type', t)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                  form.type === t
                    ? t === 'BUY'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : 'bg-red-500/20 text-red-400 border border-red-500/40'
                    : 'bg-gray-800 text-gray-500 border border-gray-700 hover:text-gray-300'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Quantity + Price row */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={LABEL_CLASS}>Shares *</label>
            <input
              required
              type="number"
              min="0.000001"
              step="any"
              className={FIELD_CLASS}
              placeholder="100"
              value={form.quantity}
              onChange={(e) => set('quantity', e.target.value)}
            />
          </div>
          <div>
            <label className={LABEL_CLASS}>Price per Share *</label>
            <input
              required
              type="number"
              min="0.000001"
              step="any"
              className={FIELD_CLASS}
              placeholder="150.00"
              value={form.price_per_share}
              onChange={(e) => set('price_per_share', e.target.value)}
            />
          </div>
        </div>

        {/* Trade date */}
        <div>
          <label className={LABEL_CLASS}>Trade Date *</label>
          <input
            required
            type="date"
            className={FIELD_CLASS}
            value={form.trade_date}
            onChange={(e) => set('trade_date', e.target.value)}
          />
        </div>

        {/* Fees */}
        <div>
          <label className={LABEL_CLASS}>Fees (optional)</label>
          <input
            type="number"
            min="0"
            step="any"
            className={FIELD_CLASS}
            placeholder="0.00"
            value={form.fees}
            onChange={(e) => set('fees', e.target.value)}
          />
        </div>

        {/* Notes */}
        <div>
          <label className={LABEL_CLASS}>Notes (optional)</label>
          <input
            type="text"
            className={FIELD_CLASS}
            placeholder="Optional note"
            value={form.notes}
            onChange={(e) => set('notes', e.target.value)}
          />
        </div>

        {/* Error */}
        {errorMsg && (
          <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
            {errorMsg}
          </p>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="px-5 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white rounded-lg transition-colors"
          >
            {mutation.isPending ? 'Adding…' : 'Add Transaction'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
