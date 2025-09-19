import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isStudent = user?.role === "Student";
  const basePath = isStudent ? "/student" : "/faculty";

  return (
    <nav className="bg-blue-600 text-white px-6 py-4 flex justify-between items-center">
      <div className="text-xl font-bold">Attendance App</div>
      <div className="space-x-4">
        <Link to={`${basePath}/dashboard`} className="hover:underline">
          Dashboard
        </Link>
        <Link to={`${basePath}/profile`} className="hover:underline">
          Profile
        </Link>
        {isStudent && (
          <>
            <Link to={`${basePath}/attendance`} className="hover:underline">
              Attendance
            </Link>
            <Link to={`${basePath}/timetable`} className="hover:underline">
              Timetable
            </Link>
          </>
        )}
        <Link to={`${basePath}/notifications`} className="hover:underline">
          Notifications
        </Link>
        <button
          onClick={handleLogout}
          className="bg-red-500 px-3 py-1 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
