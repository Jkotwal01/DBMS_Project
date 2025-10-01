import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRouteV2({ 
  children, 
  allowedRoles = [], 
  requiredPermissions = [],
  fallbackPath = "/unauthorized" 
}) {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role-based access
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role?.toLowerCase())) {
    return <Navigate to={fallbackPath} replace />;
  }

  // Check permission-based access (if implemented)
  if (requiredPermissions.length > 0) {
    const userPermissions = getUserPermissions(user.role);
    const hasRequiredPermissions = requiredPermissions.every(permission =>
      userPermissions.includes(permission)
    );

    if (!hasRequiredPermissions) {
      return <Navigate to={fallbackPath} replace />;
    }
  }

  // If all checks pass, render the protected component
  return children;
}

// Helper function to get user permissions based on role
function getUserPermissions(role) {
  const rolePermissions = {
    student: [
      'read_own_profile',
      'update_own_profile',
      'read_own_attendance',
      'read_timetable',
      'read_notifications'
    ],
    faculty: [
      'read_own_profile',
      'update_own_profile',
      'read_student_profiles',
      'update_student_profiles',
      'mark_attendance',
      'read_attendance',
      'create_notifications',
      'read_notifications',
      'manage_timetable',
      'upload_student_data',
      'read_departments',
      'read_subjects'
    ],
    admin: [
      'read_all_profiles',
      'update_all_profiles',
      'create_users',
      'delete_users',
      'manage_departments',
      'manage_subjects',
      'manage_academic_years',
      'manage_semesters',
      'read_audit_logs',
      'system_settings',
      'bulk_operations'
    ],
    parent: [
      'read_child_profile',
      'read_child_attendance',
      'read_child_timetable',
      'read_notifications'
    ],
    management: [
      'read_all_profiles',
      'read_reports',
      'read_analytics',
      'read_departments',
      'read_financial_data'
    ]
  };

  return rolePermissions[role?.toLowerCase()] || [];
}

// Higher-order component for role-based routing
export function withRoleProtection(WrappedComponent, allowedRoles = [], requiredPermissions = []) {
  return function RoleProtectedComponent(props) {
    return (
      <ProtectedRouteV2 allowedRoles={allowedRoles} requiredPermissions={requiredPermissions}>
        <WrappedComponent {...props} />
      </ProtectedRouteV2>
    );
  };
}

// Specific role protection components
export function StudentRoute({ children }) {
  return <ProtectedRouteV2 allowedRoles={['student']}>{children}</ProtectedRouteV2>;
}

export function FacultyRoute({ children }) {
  return <ProtectedRouteV2 allowedRoles={['faculty']}>{children}</ProtectedRouteV2>;
}

export function AdminRoute({ children }) {
  return <ProtectedRouteV2 allowedRoles={['admin']}>{children}</ProtectedRouteV2>;
}

export function ParentRoute({ children }) {
  return <ProtectedRouteV2 allowedRoles={['parent']}>{children}</ProtectedRouteV2>;
}

export function ManagementRoute({ children }) {
  return <ProtectedRouteV2 allowedRoles={['management']}>{children}</ProtectedRouteV2>;
}

// Multi-role protection
export function FacultyAdminRoute({ children }) {
  return <ProtectedRouteV2 allowedRoles={['faculty', 'admin']}>{children}</ProtectedRouteV2>;
}

export function AdminManagementRoute({ children }) {
  return <ProtectedRouteV2 allowedRoles={['admin', 'management']}>{children}</ProtectedRouteV2>;
}