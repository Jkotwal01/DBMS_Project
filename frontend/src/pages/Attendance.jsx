import React, { useEffect, useState } from "react";
import api from "../api";

function Attendance() {
  const [attendance, setAttendance] = useState([]);
  const [stats, setStats] = useState({});

  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        const res = await api.get("/student/attendance");
        setAttendance(res.data);

        // Calculate stats
        const statsBySubject = res.data.reduce((acc, curr) => {
          if (!acc[curr.subject_id]) {
            acc[curr.subject_id] = { total: 0, present: 0 };
          }
          acc[curr.subject_id].total++;
          if (curr.status === "Present") {
            acc[curr.subject_id].present++;
          }
          return acc;
        }, {});

        setStats(statsBySubject);
      } catch (err) {
        console.error(err);
      }
    };
    fetchAttendance();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Attendance Report</h2>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {Object.entries(stats).map(([subjectId, stat]) => (
          <div key={subjectId} className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold">Subject {subjectId}</h3>
            <p className="text-lg">
              {((stat.present / stat.total) * 100).toFixed(1)}% ({stat.present}/
              {stat.total} classes)
            </p>
          </div>
        ))}
      </div>

      {/* Detailed Records */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left">Date</th>
              <th className="p-3 text-left">Subject</th>
              <th className="p-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {attendance.map((record, idx) => (
              <tr key={idx} className="border-t">
                <td className="p-3">
                  {new Date(record.date).toLocaleDateString()}
                </td>
                <td className="p-3">Subject {record.subject_id}</td>
                <td className="p-3">
                  <span
                    className={`px-2 py-1 rounded text-sm ${
                      record.status === "Present"
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {record.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Attendance;
