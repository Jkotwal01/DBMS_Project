import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

export default function StudentDashboard() {
  const [stats, setStats] = useState({
    totalClasses: 0,
    attendance: 0,
    subjects: [],
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [attendanceRes, timetableRes] = await Promise.all([
          api.get("/student/attendance"),
          api.get("/student/timetable"),
        ]);

        setStats({
          totalClasses: timetableRes.data.length,
          attendance: attendanceRes.data.length,
          subjects: timetableRes.data,
        });
      } catch (err) {
        console.error(err);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Student Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-100 p-4 rounded-lg shadow">
          <h3 className="font-semibold">Total Classes</h3>
          <p className="text-2xl">{stats.totalClasses}</p>
        </div>
        <div className="bg-green-100 p-4 rounded-lg shadow">
          <h3 className="font-semibold">Attendance</h3>
          <p className="text-2xl">{stats.attendance}</p>
        </div>
        <div className="bg-yellow-100 p-4 rounded-lg shadow">
          <h3 className="font-semibold">Subjects</h3>
          <p className="text-2xl">{stats.subjects.length}</p>
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link
          to="/student/attendance"
          className="bg-white p-4 rounded-lg shadow hover:shadow-md"
        >
          <h3 className="font-semibold flex items-center">📊 Attendance</h3>
        </Link>
        <Link
          to="/student/timetable"
          className="bg-white p-4 rounded-lg shadow hover:shadow-md"
        >
          <h3 className="font-semibold flex items-center">📅 Timetable</h3>
        </Link>
        <Link
          to="/student/notifications"
          className="bg-white p-4 rounded-lg shadow hover:shadow-md"
        >
          <h3 className="font-semibold flex items-center">🔔 Notifications</h3>
        </Link>
        <Link
          to="/student/profile"
          className="bg-white p-4 rounded-lg shadow hover:shadow-md"
        >
          <h3 className="font-semibold flex items-center">👤 Profile</h3>
        </Link>
      </div>
    </div>
  );
}
