import { useState } from 'react'
import Modal from './Modal'
import { useCreateOptionTrade } from '../hooks/useCreateOptionTrade'
import type { OptionTradeCreate } from '../api/types'

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

type ToggleOption = { label: string; value: string; activeClass: string }

function ToggleGroup({
  options,
  value,
  onChange,
}: {
  options: ToggleOption[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="flex gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
            value === opt.value
              ? opt.activeClass
              : 'bg-gray-800 text-gray-500 border border-gray-700 hover:text-gray-300'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

export default function AddOptionTradeModal({ onClose }: Props) {
  const mutation = useCreateOptionTrade()

  const [form, setForm] = useState({
    underlying_symbol: '',
    option_type: 'CALL' as 'CALL' | 'PUT',
    action: 'BUY' as 'BUY' | 'SELL',
    strike: '',
    expiration_date: '',
    quantity: '',
    open_date: '',
    open_price: '',
    open_commission: '',
    status: 'OPEN' as 'OPEN' | 'CLOSED' | 'EXPIRED',
    exit_date: '',
    exit_price: '',
    close_commission: '',
    notes: '',
  })

  const set = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const body: OptionTradeCreate = {
      underlying_symbol: form.underlying_symbol.trim().toUpperCase(),
      option_type: form.option_type,
      action: form.action,
      strike: parseFloat(form.strike),
      expiration_date: form.expiration_date,
      quantity: parseInt(form.quantity, 10),
      open_date: form.open_date,
      open_price: parseFloat(form.open_price),
      open_commission: form.open_commission ? parseFloat(form.open_commission) : 0,
      status: form.status,
      exit_date: form.exit_date || null,
      exit_price: form.exit_price ? parseFloat(form.exit_price) : null,
      close_commission: form.close_commission ? parseFloat(form.close_commission) : 0,
      notes: form.notes.trim() || null,
    }

    mutation.mutate(body, { onSuccess: onClose })
  }

  const errorMsg = mutation.error ? extractError(mutation.error) : null
  const isClosedOrExpired = form.status === 'CLOSED' || form.status === 'EXPIRED'

  return (
    <Modal title="Add Option Trade" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Underlying symbol */}
        <div>
          <label className={LABEL_CLASS}>Underlying Symbol *</label>
          <input
            required
            className={FIELD_CLASS}
            placeholder="e.g. AAPL"
            value={form.underlying_symbol}
            onChange={(e) => set('underlying_symbol', e.target.value)}
          />
        </div>

        {/* Type + Action row */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={LABEL_CLASS}>Option Type *</label>
            <ToggleGroup
              value={form.option_type}
              onChange={(v) => set('option_type', v)}
              options={[
                { label: 'CALL', value: 'CALL', activeClass: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' },
                { label: 'PUT', value: 'PUT', activeClass: 'bg-amber-500/20 text-amber-400 border border-amber-500/40' },
              ]}
            />
          </div>
          <div>
            <label className={LABEL_CLASS}>Action *</label>
            <ToggleGroup
              value={form.action}
              onChange={(v) => set('action', v)}
              options={[
                { label: 'BUY', value: 'BUY', activeClass: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' },
                { label: 'SELL', value: 'SELL', activeClass: 'bg-red-500/20 text-red-400 border border-red-500/40' },
              ]}
            />
          </div>
        </div>

        {/* Strike + Contracts row */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={LABEL_CLASS}>Strike *</label>
            <input
              required
              type="number"
              min="0.01"
              step="any"
              className={FIELD_CLASS}
              placeholder="150.00"
              value={form.strike}
              onChange={(e) => set('strike', e.target.value)}
            />
          </div>
          <div>
            <label className={LABEL_CLASS}>Contracts *</label>
            <input
              required
              type="number"
              min="1"
              step="1"
              className={FIELD_CLASS}
              placeholder="1"
              value={form.quantity}
              onChange={(e) => set('quantity', e.target.value)}
            />
          </div>
        </div>

        {/* Open date + Expiry row */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={LABEL_CLASS}>Open Date *</label>
            <input
              required
              type="date"
              className={FIELD_CLASS}
              value={form.open_date}
              onChange={(e) => set('open_date', e.target.value)}
            />
          </div>
          <div>
            <label className={LABEL_CLASS}>Expiration Date *</label>
            <input
              required
              type="date"
              className={FIELD_CLASS}
              value={form.expiration_date}
              onChange={(e) => set('expiration_date', e.target.value)}
            />
          </div>
        </div>

        {/* Open price + Commission row */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={LABEL_CLASS}>Open Price (per share) *</label>
            <input
              required
              type="number"
              min="0.0001"
              step="any"
              className={FIELD_CLASS}
              placeholder="2.50"
              value={form.open_price}
              onChange={(e) => set('open_price', e.target.value)}
            />
          </div>
          <div>
            <label className={LABEL_CLASS}>Open Commission</label>
            <input
              type="number"
              min="0"
              step="any"
              className={FIELD_CLASS}
              placeholder="0.00"
              value={form.open_commission}
              onChange={(e) => set('open_commission', e.target.value)}
            />
          </div>
        </div>

        {/* Status */}
        <div>
          <label className={LABEL_CLASS}>Status *</label>
          <ToggleGroup
            value={form.status}
            onChange={(v) => set('status', v)}
            options={[
              { label: 'OPEN', value: 'OPEN', activeClass: 'bg-blue-500/20 text-blue-400 border border-blue-500/40' },
              { label: 'CLOSED', value: 'CLOSED', activeClass: 'bg-gray-500/20 text-gray-300 border border-gray-500/40' },
              { label: 'EXPIRED', value: 'EXPIRED', activeClass: 'bg-gray-500/20 text-gray-400 border border-gray-500/40' },
            ]}
          />
        </div>

        {/* Close details — only shown when closed/expired */}
        {isClosedOrExpired && (
          <>
            <div className="border-t border-gray-800 pt-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Close Details</p>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className={LABEL_CLASS}>Exit Date</label>
                    <input
                      type="date"
                      className={FIELD_CLASS}
                      value={form.exit_date}
                      onChange={(e) => set('exit_date', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={LABEL_CLASS}>Exit Price</label>
                    <input
                      type="number"
                      min="0"
                      step="any"
                      className={FIELD_CLASS}
                      placeholder="0.00"
                      value={form.exit_price}
                      onChange={(e) => set('exit_price', e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label className={LABEL_CLASS}>Close Commission</label>
                  <input
                    type="number"
                    min="0"
                    step="any"
                    className={FIELD_CLASS}
                    placeholder="0.00"
                    value={form.close_commission}
                    onChange={(e) => set('close_commission', e.target.value)}
                  />
                </div>
              </div>
            </div>
          </>
        )}

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
            {mutation.isPending ? 'Adding…' : 'Add Trade'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
