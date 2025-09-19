import React, { useEffect, useState } from "react";
import api from "../api";

function Notifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const res = await api.get("/notifications");
        setNotifications(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchNotifications();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Notifications</h2>
      {notifications.length === 0 ? (
        <p>No notifications</p>
      ) : (
        <ul>
          {notifications.map((note, idx) => (
            <li key={idx} className="border-b py-2">
              {note.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Notifications;
