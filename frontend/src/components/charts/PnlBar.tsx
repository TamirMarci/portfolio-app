import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { formatUSD } from '../../lib/formatters'

interface BarEntry {
  symbol: string
  net_pnl: number
}

interface Props {
  data: BarEntry[]
  title: string
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  const value = payload[0].value as number
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm shadow-lg">
      <p className="font-medium text-gray-100 mb-1">{label}</p>
      <p className={value >= 0 ? 'text-emerald-400' : 'text-red-400'}>
        {formatUSD(value)}
      </p>
    </div>
  )
}

export default function PnlBar({ data, title }: Props) {
  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
          <XAxis
            dataKey="symbol"
            tick={{ fontSize: 12, fill: '#9ca3af' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v) => `$${v}`}
            tick={{ fontSize: 11, fill: '#9ca3af' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
          <Bar dataKey="net_pnl" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.net_pnl >= 0 ? '#10b981' : '#ef4444'}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
