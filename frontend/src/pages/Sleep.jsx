import { useState, useEffect } from 'react'
import { healthAPI } from '../api'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Sleep() {
  const [sleepRecords, setSleepRecords] = useState([])
  const [derivedMetrics, setDerivedMetrics] = useState([])
  const [days, setDays] = useState(7)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [days])

  const loadData = async () => {
    try {
      setLoading(true)
      const [sleepRes, metricsRes] = await Promise.all([
        healthAPI.getSleepRecords(days),
        healthAPI.getDerivedMetrics(days)
      ])
      setSleepRecords(sleepRes.data.records)
      setDerivedMetrics(metricsRes.data.records)
    } catch (error) {
      console.error('Error loading sleep data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data
  const sleepDurationData = sleepRecords.map(record => ({
    date: new Date(record.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    hours: (record.time_asleep_minutes / 60).toFixed(1),
    awake: (record.awake_minutes / 60).toFixed(1)
  })).reverse()

  const sleepStagesData = sleepRecords.map(record => ({
    date: new Date(record.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    rem: (record.rem_minutes / 60).toFixed(1),
    deep: (record.deep_minutes / 60).toFixed(1),
    core: (record.core_minutes / 60).toFixed(1)
  })).reverse()

  const sleepEfficiencyData = derivedMetrics.map(metric => ({
    date: new Date(metric.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    efficiency: metric.sleep_efficiency?.toFixed(1) || 0,
    fragmentation: metric.sleep_fragmentation_index?.toFixed(1) || 0
  })).reverse()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading sleep data...</div>
      </div>
    )
  }

  if (sleepRecords.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <p className="text-blue-900 font-medium">No sleep data available</p>
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
        <h1 className="text-2xl font-bold text-gray-900">Sleep Analysis</h1>
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

      {/* Sleep Duration Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Sleep Duration</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={sleepDurationData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="hours" stroke="#3b82f6" strokeWidth={2} name="Sleep Duration" />
            <Line type="monotone" dataKey="awake" stroke="#ef4444" strokeWidth={2} name="Awake Time" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Sleep Stages Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Sleep Stages Breakdown</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={sleepStagesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="deep" stackId="a" fill="#3b82f6" name="Deep Sleep" />
            <Bar dataKey="core" stackId="a" fill="#60a5fa" name="Core Sleep" />
            <Bar dataKey="rem" stackId="a" fill="#a78bfa" name="REM Sleep" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Sleep Efficiency Chart */}
      {derivedMetrics.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Sleep Quality Metrics</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={sleepEfficiencyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis label={{ value: 'Percentage', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="efficiency" stroke="#10b981" strokeWidth={2} name="Sleep Efficiency" />
              <Line type="monotone" dataKey="fragmentation" stroke="#f59e0b" strokeWidth={2} name="Fragmentation Index" />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-4 text-sm text-gray-600">
            <p>Sleep Efficiency: Percentage of time asleep while in bed (higher is better)</p>
            <p>Fragmentation Index: Measure of sleep disruption (lower is better)</p>
          </div>
        </div>
      )}

      {/* Recent Sleep Records Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Sleep Records</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">REM</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deep</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Core</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Awake</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sleepRecords.slice(0, 10).map((record, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(record.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {(record.time_asleep_minutes / 60).toFixed(1)}h
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-purple-600">
                    {(record.rem_minutes / 60).toFixed(1)}h
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600">
                    {(record.deep_minutes / 60).toFixed(1)}h
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {(record.core_minutes / 60).toFixed(1)}h
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                    {record.awake_minutes}m
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
