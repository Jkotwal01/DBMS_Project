import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api";

export default function StudentDashboardV2() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    user: null,
    student: null,
    attendance_summary: {},
    recent_notifications: [],
    upcoming_classes: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await api.get("/dashboard/student");
        setDashboardData(response.data);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️ {error}</div>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const attendancePercentage = dashboardData.attendance_summary?.attendance_percentage || 0;
  const attendanceColor = attendancePercentage >= 75 ? 'green' : attendancePercentage >= 50 ? 'yellow' : 'red';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {dashboardData.user?.name || user?.name}!
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Student Dashboard - {dashboardData.student?.class_name || 'N/A'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Roll No: {dashboardData.student?.roll_no || 'N/A'}</p>
              <p className="text-sm text-gray-600">Section: {dashboardData.student?.section || 'N/A'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-sm">📊</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.attendance_summary?.total_sessions || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 text-sm">✅</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Present</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.attendance_summary?.present_count || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                  <span className="text-red-600 text-sm">❌</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Absent</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.attendance_summary?.absent_count || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className={`w-8 h-8 bg-${attendanceColor}-100 rounded-full flex items-center justify-center`}>
                  <span className={`text-${attendanceColor}-600 text-sm`}>📈</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Attendance %</p>
                <p className={`text-2xl font-semibold text-${attendanceColor}-600`}>
                  {attendancePercentage.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Quick Actions */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Link
                    to="/student/attendance"
                    className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                      <span className="text-blue-600 text-xl">📊</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">View Attendance</span>
                  </Link>

                  <Link
                    to="/student/timetable"
                    className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
                      <span className="text-green-600 text-xl">📅</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">Timetable</span>
                  </Link>

                  <Link
                    to="/student/notifications"
                    className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mb-3">
                      <span className="text-yellow-600 text-xl">🔔</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">Notifications</span>
                  </Link>

                  <Link
                    to="/student/profile"
                    className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                      <span className="text-purple-600 text-xl">👤</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">Profile</span>
                  </Link>
                </div>
              </div>
            </div>

            {/* Upcoming Classes */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Today's Classes</h3>
              </div>
              <div className="p-6">
                {dashboardData.upcoming_classes?.length > 0 ? (
                  <div className="space-y-4">
                    {dashboardData.upcoming_classes.map((classItem, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900">{classItem.subject?.subject_name}</h4>
                          <p className="text-sm text-gray-600">
                            {classItem.start_time} - {classItem.end_time}
                          </p>
                          <p className="text-sm text-gray-500">{classItem.class_room}</p>
                        </div>
                        <div className="text-right">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {classItem.day}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-gray-400 text-2xl">📅</span>
                    </div>
                    <p className="text-gray-500">No classes scheduled for today</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Notifications */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Recent Notifications</h3>
              </div>
              <div className="p-6">
                {dashboardData.recent_notifications?.length > 0 ? (
                  <div className="space-y-4">
                    {dashboardData.recent_notifications.map((notification, index) => (
                      <div key={index} className="border-l-4 border-blue-400 pl-4">
                        <h4 className="font-medium text-gray-900 text-sm">{notification.title}</h4>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-400 mt-2">
                          {new Date(notification.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                    <Link
                      to="/student/notifications"
                      className="block text-center text-blue-600 hover:text-blue-800 text-sm font-medium mt-4"
                    >
                      View All Notifications
                    </Link>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-gray-400 text-2xl">🔔</span>
                    </div>
                    <p className="text-gray-500">No recent notifications</p>
                  </div>
                )}
              </div>
            </div>

            {/* Profile Summary */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Profile Summary</h3>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Name:</span>
                    <span className="text-sm font-medium">{dashboardData.user?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Roll No:</span>
                    <span className="text-sm font-medium">{dashboardData.student?.roll_no}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Class:</span>
                    <span className="text-sm font-medium">{dashboardData.student?.class_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Section:</span>
                    <span className="text-sm font-medium">{dashboardData.student?.section}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Batch:</span>
                    <span className="text-sm font-medium">{dashboardData.student?.batch}</span>
                  </div>
                </div>
                <Link
                  to="/student/profile"
                  className="block text-center bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors mt-4"
                >
                  Edit Profile
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}