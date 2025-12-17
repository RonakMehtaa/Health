import { useState, useEffect } from 'react'
import { healthAPI } from '../api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Activity() {
  const [activityRecords, setActivityRecords] = useState([])
  const [days, setDays] = useState(7)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [days])

  const loadData = async () => {
    try {
      setLoading(true)
      const response = await healthAPI.getActivityRecords(days)
      setActivityRecords(response.data.records)
    } catch (error) {
      console.error('Error loading activity data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data
  const stepsData = activityRecords.map(record => ({
    date: new Date(record.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    steps: record.steps
  })).reverse()

  const caloriesData = activityRecords.map(record => ({
    date: new Date(record.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    calories: record.move_calories
  })).reverse()

  const standHoursData = activityRecords.map(record => ({
    date: new Date(record.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    hours: record.stand_hours
  })).reverse()

  // Calculate averages
  const avgSteps = activityRecords.length > 0 
    ? Math.round(activityRecords.reduce((sum, r) => sum + r.steps, 0) / activityRecords.length)
    : 0
  const avgCalories = activityRecords.length > 0
    ? Math.round(activityRecords.reduce((sum, r) => sum + r.move_calories, 0) / activityRecords.length)
    : 0
  const avgStandHours = activityRecords.length > 0
    ? Math.round(activityRecords.reduce((sum, r) => sum + r.stand_hours, 0) / activityRecords.length)
    : 0

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading activity data...</div>
      </div>
    )
  }

  if (activityRecords.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <p className="text-blue-900 font-medium">No activity data available</p>
        <p className="text-blue-700 text-sm mt-2">
          Upload your Apple Health export from the Dashboard
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with time range selector */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Activity Tracking</h1>
        <div className="flex space-x-2">
          {[7, 14, 30].map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-4 py-2 rounded-lg transition ${
                days === d
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              {d} days
            </button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Average Steps</div>
              <div className="text-3xl font-bold text-gray-900">{avgSteps.toLocaleString()}</div>
            </div>
            <div className="text-4xl">🚶</div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Average Calories</div>
              <div className="text-3xl font-bold text-orange-600">{avgCalories}</div>
            </div>
            <div className="text-4xl">🔥</div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Average Stand Hours</div>
              <div className="text-3xl font-bold text-green-600">{avgStandHours}</div>
            </div>
            <div className="text-4xl">🧍</div>
          </div>
        </div>
      </div>

      {/* Steps Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Daily Steps</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stepsData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Steps', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="steps" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Calories Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Active Calories Burned</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={caloriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Calories', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="calories" stroke="#f97316" strokeWidth={2} name="Calories" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Stand Hours Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Stand Hours per Day</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={standHoursData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="hours" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Activity Records Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Activity Records</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Steps</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Calories</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stand Hours</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {activityRecords.slice(0, 10).map((record, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(record.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {record.steps.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600">
                    {Math.round(record.move_calories)} kcal
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                    {record.stand_hours}h
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
