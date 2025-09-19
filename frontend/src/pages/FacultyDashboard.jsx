import React, { useEffect, useState } from "react";
import api from "../api";
import { Link } from "react-router-dom";

function FacultyDashboard() {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const res = await api.get("/faculty/classes");
        setClasses(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchClasses();
  }, []);

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Faculty Dashboard</h2>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <Link
          to="/faculty/attendance"
          className="bg-blue-100 p-4 rounded-lg shadow hover:shadow-md"
        >
          <h3 className="font-semibold">Mark Attendance</h3>
        </Link>
        <Link
          to="/faculty/notifications"
          className="bg-green-100 p-4 rounded-lg shadow hover:shadow-md"
        >
          <h3 className="font-semibold">Send Notification</h3>
        </Link>
        <Link
          to="/faculty/profile"
          className="bg-yellow-100 p-4 rounded-lg shadow hover:shadow-md"
        >
          <h3 className="font-semibold">View Profile</h3>
        </Link>
      </div>

      {/* Classes List */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-4">Your Classes</h3>
        {classes.length === 0 ? (
          <p>No classes assigned yet</p>
        ) : (
          <div className="grid gap-4">
            {classes.map((cls, idx) => (
              <div key={idx} className="border p-4 rounded">
                <h4 className="font-medium">{cls.subject_name}</h4>
                <p className="text-sm text-gray-600">
                  Semester: {cls.semester}
                </p>
                <div className="mt-2">
                  <p className="text-sm font-medium">Timetable:</p>
                  {cls.timetable_entries.map((entry, i) => (
                    <p key={i} className="text-sm text-gray-600">
                      {entry.day} - {entry.time_slot}
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default FacultyDashboard;
