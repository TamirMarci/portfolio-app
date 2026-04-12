import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { CHART_COLORS } from '../../lib/constants'
import { formatPct, formatUSD } from '../../lib/formatters'

interface Slice {
  name: string
  value: number
}

interface Props {
  data: Slice[]
  title: string
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0].payload
  const total = payload[0].payload.__total ?? 0
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm shadow-lg">
      <p className="font-medium text-gray-100">{name}</p>
      <p className="text-gray-400">{formatUSD(value)}</p>
      {total > 0 && (
        <p className="text-gray-500">{formatPct(value / total)}</p>
      )}
    </div>
  )
}

export default function AllocationPie({ data, title }: Props) {
  const total = data.reduce((s, d) => s + d.value, 0)
  const enriched = data.map((d) => ({ ...d, __total: total }))

  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={enriched}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            innerRadius={55}
            paddingAngle={2}
          >
            {enriched.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={(value) => (
              <span className="text-xs text-gray-400">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
