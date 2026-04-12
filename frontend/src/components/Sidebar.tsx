import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  PieChart,
  ArrowLeftRight,
  Camera,
  TrendingUp,
} from 'lucide-react'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/allocation', icon: PieChart, label: 'Allocation' },
  { to: '/transactions', icon: ArrowLeftRight, label: 'Transactions' },
  { to: '/snapshots', icon: Camera, label: 'Snapshots' },
  { to: '/options', icon: TrendingUp, label: 'Options' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-5 border-b border-gray-800">
        <span className="text-blue-400 font-bold text-lg tracking-tight">
          Portfolio
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-500/10 text-blue-400'
                  : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
