import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Sleep from './pages/Sleep'
import Activity from './pages/Activity'
import Insights from './pages/Insights'

function Navigation() {
  const location = useLocation()
  
  const isActive = (path) => location.pathname === path
  
  const navClass = (path) => 
    `px-4 py-2 rounded-lg transition-colors ${
      isActive(path) 
        ? 'bg-blue-600 text-white' 
        : 'text-gray-600 hover:bg-gray-200'
    }`
  
  return (
    <nav className="bg-white shadow-sm mb-6">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-2xl font-bold text-gray-900">HealthStats</h1>
            <div className="flex space-x-2">
              <Link to="/" className={navClass('/')}>
                Dashboard
              </Link>
              <Link to="/sleep" className={navClass('/sleep')}>
                Sleep
              </Link>
              <Link to="/activity" className={navClass('/activity')}>
                Activity
              </Link>
              <Link to="/insights" className={navClass('/insights')}>
                Insights
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sleep" element={<Sleep />} />
            <Route path="/activity" element={<Activity />} />
            <Route path="/insights" element={<Insights />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
