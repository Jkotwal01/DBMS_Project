import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Register from "./pages/Register";
import StudentDashboard from "./pages/StudentDashboard";
import FacultyDashboard from "./pages/FacultyDashboard";
import Profile from "./pages/Profile";
import Attendance from "./pages/Attendance";
import Timetable from "./pages/Timetable";
import Notifications from "./pages/Notifications";
import UnauthorizedPage from "./pages/UnauthorizedPage";

function AppContent() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Prevent accessing login/register when authenticated
    if (
      user &&
      (location.pathname === "/login" ||
        location.pathname === "/register" ||
        location.pathname === "/")
    ) {
      const role = user.role.toLowerCase();
      navigate(`/${role}/dashboard`, { replace: true });
    }
  }, [user, location, navigate]);

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* Student routes */}
      <Route
        path="/student/*"
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <div>
              <Navbar />
              <Routes>
                <Route path="dashboard" element={<StudentDashboard />} />
                <Route path="attendance" element={<Attendance />} />
                <Route path="timetable" element={<Timetable />} />
                <Route path="profile" element={<Profile />} />
                <Route path="notifications" element={<Notifications />} />
              </Routes>
            </div>
          </ProtectedRoute>
        }
      />

      {/* Faculty routes */}
      <Route
        path="/faculty/*"
        element={
          <ProtectedRoute allowedRoles={["faculty"]}>
            <div>
              <Navbar />
              <Routes>
                <Route path="dashboard" element={<FacultyDashboard />} />
                <Route path="attendance" element={<Attendance />} />
                <Route path="profile" element={<Profile />} />
                <Route path="notifications" element={<Notifications />} />
              </Routes>
            </div>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
