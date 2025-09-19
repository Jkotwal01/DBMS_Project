import React, { useEffect, useState } from "react";
import api from "../api";

function Timetable() {
  const [timetable, setTimetable] = useState([]);
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const timeSlots = [
    "9:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-1:00",
    "2:00-3:00",
    "3:00-4:00",
  ];

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        const res = await api.get("/student/timetable");
        setTimetable(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchTimetable();
  }, []);

  const getSubjectForSlot = (day, timeSlot) => {
    const entry = timetable.find(
      (t) => t.day === day && t.time_slot === timeSlot
    );
    return entry ? entry.subject_name : "-";
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Timetable</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border">
          <thead>
            <tr>
              <th className="border p-2">Time/Day</th>
              {days.map((day) => (
                <th key={day} className="border p-2">
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {timeSlots.map((slot) => (
              <tr key={slot}>
                <td className="border p-2 font-medium">{slot}</td>
                {days.map((day) => (
                  <td key={`${day}-${slot}`} className="border p-2">
                    {getSubjectForSlot(day, slot)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Timetable;
