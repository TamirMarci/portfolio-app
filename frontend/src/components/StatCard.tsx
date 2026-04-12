interface StatCardProps {
  label: string
  value: string
  sub?: string
  valueClass?: string
}

export default function StatCard({ label, value, sub, valueClass }: StatCardProps) {
  return (
    <div className="stat-card">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
        {label}
      </p>
      <p className={`text-2xl font-semibold ${valueClass ?? 'text-gray-100'}`}>{value}</p>
      {sub && <p className="text-sm text-gray-500 mt-0.5">{sub}</p>}
    </div>
  )
}
