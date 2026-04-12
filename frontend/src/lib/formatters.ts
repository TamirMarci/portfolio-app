const usdFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const compactUsdFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
})

export function formatUSD(value: number | null | undefined): string {
  if (value == null) return '—'
  return usdFormatter.format(value)
}

export function formatUSDCompact(value: number | null | undefined): string {
  if (value == null) return '—'
  return compactUsdFormatter.format(value)
}

export function formatPct(value: number | null | undefined, digits = 2): string {
  if (value == null) return '—'
  return `${(value * 100).toFixed(digits)}%`
}

/** Shows sign prefix: +12.34% or -5.67% */
export function formatPctChange(value: number | null | undefined, digits = 2): string {
  if (value == null) return '—'
  const pct = (value * 100).toFixed(digits)
  return value >= 0 ? `+${pct}%` : `${pct}%`
}

/** Shows sign prefix: +$1,234.56 or -$234.56 */
export function formatPnl(value: number | null | undefined): string {
  if (value == null) return '—'
  const abs = usdFormatter.format(Math.abs(value))
  return value >= 0 ? `+${abs}` : `-${abs}`
}

export function formatNumber(value: number | null | undefined, digits = 2): string {
  if (value == null) return '—'
  return value.toLocaleString('en-US', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  // ISO date string: YYYY-MM-DD
  const [year, month, day] = iso.split('-')
  return `${day}/${month}/${year}`
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
