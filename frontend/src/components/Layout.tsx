import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import PriceRefreshButton from './PriceRefreshButton'

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="h-16 shrink-0 border-b border-gray-800 bg-gray-900 flex items-center justify-between px-6">
          <div />
          <PriceRefreshButton />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
