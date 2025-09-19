import React from "react";
import { Link } from "react-router-dom";

function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-red-600 mb-4">
          Unauthorized Access
        </h1>
        <p className="text-gray-600 mb-4">
          You don't have permission to access this page.
        </p>
        <Link to="/login" className="text-blue-600 hover:underline">
          Return to Login
        </Link>
      </div>
    </div>
  );
}

export default UnauthorizedPage;
