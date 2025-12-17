import { useState, useEffect } from 'react'
import { healthAPI } from '../api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [sleepSummary, setSleepSummary] = useState(null)
  const [activitySummary, setActivitySummary] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [sleepRes, activityRes, statsRes] = await Promise.all([
        healthAPI.getSleepSummary(7),
        healthAPI.getActivitySummary(7),
        healthAPI.getStats()
      ])
      setSleepSummary(sleepRes.data)
      setActivitySummary(activityRes.data)
      setStats(statsRes.data)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    try {
      setUploading(true)
      setUploadStatus(null)
      const response = await healthAPI.uploadFile(file)
      setUploadStatus({ type: 'success', message: 'Data uploaded successfully!', data: response.data })
      // Reload data after upload
      setTimeout(() => loadData(), 1000)
    } catch (error) {
      setUploadStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Upload failed. Please try again.' 
      })
    } finally {
      setUploading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Upload Apple Health Data</h2>
        <div className="flex items-center space-x-4">
          <label className="cursor-pointer bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
            {uploading ? 'Uploading...' : 'Choose File'}
            <input
              type="file"
              accept=".xml,.zip"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
          <span className="text-sm text-gray-600">
            Upload export.xml or export.zip from Apple Health
          </span>
        </div>
        {uploadStatus && (
          <div className={`mt-4 p-4 rounded-lg ${
            uploadStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}>
            <p className="font-medium">{uploadStatus.message}</p>
            {uploadStatus.data?.records_added && (
              <p className="text-sm mt-2">
                Sleep: {uploadStatus.data.records_added.sleep} | 
                Activity: {uploadStatus.data.records_added.activity} | 
                Vitals: {uploadStatus.data.records_added.vitals}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Total Sleep Records</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total_records.sleep}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Total Activity Records</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total_records.activity}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Date Range</div>
            <div className="text-lg font-semibold text-gray-900">
              {stats.date_range.first_date ? (
                <span className="text-sm">
                  {new Date(stats.date_range.first_date).toLocaleDateString()} - {' '}
                  {new Date(stats.date_range.last_date).toLocaleDateString()}
                </span>
              ) : 'No data'}
            </div>
          </div>
        </div>
      )}

      {/* Last Night Summary */}
      {sleepSummary?.last_night && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Last Night</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-600">Total Sleep</div>
              <div className="text-2xl font-bold text-gray-900">
                {sleepSummary.last_night.time_asleep_hours}h
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">REM Sleep</div>
              <div className="text-2xl font-bold text-purple-600">
                {sleepSummary.last_night.rem_percentage}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Deep Sleep</div>
              <div className="text-2xl font-bold text-blue-600">
                {sleepSummary.last_night.deep_percentage}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Awake Time</div>
              <div className="text-2xl font-bold text-gray-600">
                {sleepSummary.last_night.awake_minutes}m
              </div>
            </div>
          </div>
          {sleepSummary.last_night.bedtime && (
            <div className="mt-4 text-sm text-gray-600">
              Bedtime: {sleepSummary.last_night.bedtime} | Wake: {sleepSummary.last_night.wake_time}
            </div>
          )}
        </div>
      )}

      {/* 7-Day Trends */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Sleep Trend */}
        {sleepSummary && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">7-Day Sleep Average</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Duration</span>
                <span className="font-semibold">{sleepSummary['7_day_average'].time_asleep_hours}h</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">REM</span>
                <span className="font-semibold text-purple-600">
                  {sleepSummary['7_day_average'].rem_percentage}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Deep</span>
                <span className="font-semibold text-blue-600">
                  {sleepSummary['7_day_average'].deep_percentage}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Activity Trend */}
        {activitySummary && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">7-Day Activity Average</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Steps</span>
                <span className="font-semibold">{activitySummary['7_day_average'].steps.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Calories</span>
                <span className="font-semibold text-orange-600">
                  {activitySummary['7_day_average'].move_calories} kcal
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Stand Hours</span>
                <span className="font-semibold text-green-600">
                  {activitySummary['7_day_average'].stand_hours}h
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {!sleepSummary && !loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <p className="text-blue-900 font-medium">No data available yet</p>
          <p className="text-blue-700 text-sm mt-2">
            Upload your Apple Health export to get started
          </p>
        </div>
      )}
    </div>
  )
}
