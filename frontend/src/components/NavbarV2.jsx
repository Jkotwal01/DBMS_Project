import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function NavbarV2() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const getRoleBasedNavItems = () => {
    if (!user) return [];

    switch (user.role?.toLowerCase()) {
      case 'student':
        return [
          { path: '/student/dashboard', label: 'Dashboard', icon: '🏠' },
          { path: '/student/attendance', label: 'Attendance', icon: '📊' },
          { path: '/student/timetable', label: 'Timetable', icon: '📅' },
          { path: '/student/notifications', label: 'Notifications', icon: '🔔' },
          { path: '/student/profile', label: 'Profile', icon: '👤' }
        ];
      case 'faculty':
        return [
          { path: '/faculty/dashboard', label: 'Dashboard', icon: '🏠' },
          { path: '/faculty/attendance', label: 'Attendance', icon: '📝' },
          { path: '/faculty/students', label: 'Students', icon: '👥' },
          { path: '/faculty/notifications', label: 'Notifications', icon: '📢' },
          { path: '/faculty/timetable', label: 'Timetable', icon: '📅' },
          { path: '/faculty/profile', label: 'Profile', icon: '👤' }
        ];
      case 'admin':
        return [
          { path: '/admin/dashboard', label: 'Dashboard', icon: '🏠' },
          { path: '/admin/users', label: 'Users', icon: '👥' },
          { path: '/admin/students', label: 'Students', icon: '🎓' },
          { path: '/admin/faculty', label: 'Faculty', icon: '👨‍🏫' },
          { path: '/admin/departments', label: 'Departments', icon: '🏢' },
          { path: '/admin/subjects', label: 'Subjects', icon: '📚' },
          { path: '/admin/reports', label: 'Reports', icon: '📊' },
          { path: '/admin/settings', label: 'Settings', icon: '⚙️' }
        ];
      case 'parent':
        return [
          { path: '/parent/dashboard', label: 'Dashboard', icon: '🏠' },
          { path: '/parent/children', label: 'Children', icon: '👶' },
          { path: '/parent/attendance', label: 'Attendance', icon: '📊' },
          { path: '/parent/notifications', label: 'Notifications', icon: '🔔' },
          { path: '/parent/profile', label: 'Profile', icon: '👤' }
        ];
      case 'management':
        return [
          { path: '/management/dashboard', label: 'Dashboard', icon: '🏠' },
          { path: '/management/analytics', label: 'Analytics', icon: '📈' },
          { path: '/management/reports', label: 'Reports', icon: '📊' },
          { path: '/management/departments', label: 'Departments', icon: '🏢' },
          { path: '/management/finance', label: 'Finance', icon: '💰' },
          { path: '/management/profile', label: 'Profile', icon: '👤' }
        ];
      default:
        return [];
    }
  };

  const navItems = getRoleBasedNavItems();

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link to={`/${user?.role?.toLowerCase() || 'student'}/dashboard`} className="flex-shrink-0">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-sm">ERP</span>
                </div>
                <span className="text-xl font-bold text-gray-900">
                  Attendance ERP
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors">
              <span className="sr-only">View notifications</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>

            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className="flex items-center space-x-2 text-sm rounded-md text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-gray-600 font-medium text-sm">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </span>
                </div>
                <span className="hidden md:block font-medium">{user?.name}</span>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Profile Dropdown Menu */}
              {isProfileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                  <div className="px-4 py-2 border-b border-gray-200">
                    <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                    <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                  </div>
                  <Link
                    to={`/${user?.role?.toLowerCase()}/profile`}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setIsProfileMenuOpen(false)}
                  >
                    Your Profile
                  </Link>
                  <Link
                    to={`/${user?.role?.toLowerCase()}/settings`}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setIsProfileMenuOpen(false)}
                  >
                    Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              <span className="sr-only">Open main menu</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-gray-50 border-t border-gray-200">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    isActive(item.path)
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Click outside to close dropdowns */}
      {(isProfileMenuOpen || isMobileMenuOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setIsProfileMenuOpen(false);
            setIsMobileMenuOpen(false);
          }}
        />
      )}
    </nav>
  );
}