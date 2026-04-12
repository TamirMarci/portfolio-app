import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Allocation from './pages/Allocation'
import Transactions from './pages/Transactions'
import Snapshots from './pages/Snapshots'
import Options from './pages/Options'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="allocation" element={<Allocation />} />
          <Route path="transactions" element={<Transactions />} />
          <Route path="snapshots" element={<Snapshots />} />
          <Route path="options" element={<Options />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
