import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Unauthorized() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
      <div className="max-w-md w-full bg-gray-800 p-8 rounded-lg shadow-lg text-center">
        <h2 className="text-3xl font-bold text-red-500 mb-4">403 - Unauthorized</h2>
        <p className="text-gray-300 mb-6">
          You do not have permission to access this page. Please contact your system administrator if you believe this is an error.
        </p>
        <button 
          onClick={() => navigate(-1)} 
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
        >
          Go Back
        </button>
      </div>
    </div>
  );
}
