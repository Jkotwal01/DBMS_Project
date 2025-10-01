import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api";

export default function FacultyDashboardV2() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    user: null,
    faculty: null,
    assigned_subjects: [],
    recent_attendance: [],
    pending_notifications: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await api.get("/dashboard/faculty");
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
                Faculty Dashboard - {dashboardData.faculty?.designation || 'Faculty Member'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Employee ID: {dashboardData.faculty?.employee_id || 'N/A'}</p>
              <p className="text-sm text-gray-600">Department: {dashboardData.faculty?.dept || 'N/A'}</p>
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
                  <span className="text-blue-600 text-sm">📚</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Assigned Subjects</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.assigned_subjects?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 text-sm">📊</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Students</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.assigned_subjects?.reduce((total, subject) => total + (subject.enrolled_students || 0), 0) || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                  <span className="text-yellow-600 text-sm">📝</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Recent Attendance</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.recent_attendance?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-purple-600 text-sm">🔔</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Notifications</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.pending_notifications?.length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Quick Actions & Subjects */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Link
                    to="/faculty/attendance"
                    className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                      <span className="text-blue-600 text-xl">📝</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">Mark Attendance</span>
                  </Link>

                  <Link
                    to="/faculty/notifications"
                    className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
                      <span className="text-green-600 text-xl">📢</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">Send Notification</span>
                  </Link>

                  <Link
                    to="/faculty/students"
                    className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mb-3">
                      <span className="text-yellow-600 text-xl">👥</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">Manage Students</span>
                  </Link>

                  <Link
                    to="/faculty/profile"
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

            {/* Assigned Subjects */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Assigned Subjects</h3>
              </div>
              <div className="p-6">
                {dashboardData.assigned_subjects?.length > 0 ? (
                  <div className="space-y-4">
                    {dashboardData.assigned_subjects.map((subject, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{subject.subject_name}</h4>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {subject.subject_code}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{subject.description}</p>
                        <div className="flex items-center justify-between text-sm text-gray-500">
                          <span>Credits: {subject.credits}</span>
                          <span>Semester: {subject.semester}</span>
                          <span>Students: {subject.enrolled_students || 0}</span>
                        </div>
                        <div className="mt-3 flex space-x-2">
                          <Link
                            to={`/faculty/attendance?subject=${subject.subject_id}`}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            View Attendance
                          </Link>
                          <Link
                            to={`/faculty/students?subject=${subject.subject_id}`}
                            className="text-green-600 hover:text-green-800 text-sm font-medium"
                          >
                            View Students
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-gray-400 text-2xl">📚</span>
                    </div>
                    <p className="text-gray-500">No subjects assigned yet</p>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Attendance Records */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Recent Attendance Records</h3>
              </div>
              <div className="p-6">
                {dashboardData.recent_attendance?.length > 0 ? (
                  <div className="space-y-4">
                    {dashboardData.recent_attendance.slice(0, 5).map((attendance, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {attendance.student?.user?.name || 'Unknown Student'}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {attendance.subject?.subject_name || 'Unknown Subject'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(attendance.marked_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          attendance.status === 'Present' 
                            ? 'bg-green-100 text-green-800' 
                            : attendance.status === 'Absent'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {attendance.status}
                        </span>
                      </div>
                    ))}
                    <Link
                      to="/faculty/attendance"
                      className="block text-center text-blue-600 hover:text-blue-800 text-sm font-medium mt-4"
                    >
                      View All Attendance Records
                    </Link>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-gray-400 text-2xl">📊</span>
                    </div>
                    <p className="text-gray-500">No recent attendance records</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Notifications & Profile */}
          <div className="space-y-6">
            {/* Recent Notifications */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Recent Notifications</h3>
              </div>
              <div className="p-6">
                {dashboardData.pending_notifications?.length > 0 ? (
                  <div className="space-y-4">
                    {dashboardData.pending_notifications.map((notification, index) => (
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
                      to="/faculty/notifications"
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
                    <span className="text-sm text-gray-600">Employee ID:</span>
                    <span className="text-sm font-medium">{dashboardData.faculty?.employee_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Designation:</span>
                    <span className="text-sm font-medium">{dashboardData.faculty?.designation}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Experience:</span>
                    <span className="text-sm font-medium">{dashboardData.faculty?.experience_years} years</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Specialization:</span>
                    <span className="text-sm font-medium">{dashboardData.faculty?.specialization}</span>
                  </div>
                </div>
                <Link
                  to="/faculty/profile"
                  className="block text-center bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors mt-4"
                >
                  Edit Profile
                </Link>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Quick Stats</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total Subjects:</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {dashboardData.assigned_subjects?.length || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total Students:</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {dashboardData.assigned_subjects?.reduce((total, subject) => total + (subject.enrolled_students || 0), 0) || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">This Month's Records:</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {dashboardData.recent_attendance?.length || 0}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}