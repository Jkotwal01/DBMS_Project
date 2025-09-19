import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";

function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchProfile();
  }, [user]);

  const fetchProfile = async () => {
    try {
      const baseUrl = user?.role === "Student" ? "/student" : "/faculty";
      const res = await api.get(`${baseUrl}/profile`);
      setProfile(res.data);
      setFormData(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load profile");
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const baseUrl = user?.role === "Student" ? "/student" : "/faculty";
      await api.put(`${baseUrl}/profile`, formData);
      setIsEditing(false);
      fetchProfile(); // Refresh data
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update profile");
    }
  };

  if (!profile) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Profile</h2>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Edit Profile
            </button>
          )}
        </div>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}

        {isEditing ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full p-2 border rounded"
                disabled
              />
            </div>
            {user?.role === "Student" && (
              <>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Roll Number
                  </label>
                  <input
                    type="text"
                    name="roll_no"
                    value={formData.roll_no || ""}
                    onChange={handleChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Class
                  </label>
                  <input
                    type="text"
                    name="class_name"
                    value={formData.class_name || ""}
                    onChange={handleChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
              </>
            )}
            {user?.role === "Faculty" && (
              <>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Designation
                  </label>
                  <input
                    type="text"
                    name="designation"
                    value={formData.designation || ""}
                    onChange={handleChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    name="department"
                    value={formData.department || ""}
                    onChange={handleChange}
                    className="w-full p-2 border rounded"
                  />
                </div>
              </>
            )}
            <div className="flex gap-4">
              <button
                type="submit"
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              >
                Save Changes
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  setFormData(profile);
                }}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <p>
              <span className="font-semibold">Name:</span> {profile.name}
            </p>
            <p>
              <span className="font-semibold">Email:</span> {profile.email}
            </p>
            <p>
              <span className="font-semibold">Role:</span> {profile.role}
            </p>
            {user?.role === "Student" && (
              <>
                <p>
                  <span className="font-semibold">Roll Number:</span>{" "}
                  {profile.roll_no || "Not set"}
                </p>
                <p>
                  <span className="font-semibold">Class:</span>{" "}
                  {profile.class_name || "Not set"}
                </p>
              </>
            )}
            {user?.role === "Faculty" && (
              <>
                <p>
                  <span className="font-semibold">Designation:</span>{" "}
                  {profile.designation || "Not set"}
                </p>
                <p>
                  <span className="font-semibold">Department:</span>{" "}
                  {profile.department || "Not set"}
                </p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;
