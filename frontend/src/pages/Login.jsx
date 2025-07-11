import React from "react";
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

const Login = () => (
  <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white">
    <img src="/logo.png" className="h-24 w-24 rounded-full" alt="gitRAG" />
    <h1 className="text-4xl font-bold my-4">gitRAG</h1>
    <div className="flex flex-col gap-4">
      <a href={`${BACKEND_URL}/api/login/google`} className="flex gap-2 items-center bg-gray-800 px-4 py-2 rounded-md hover:bg-gray-700">
        <img src="/google-logo.png" alt="Google" className="h-6 w-6" /> Sign in with Google
      </a>
      <a href={`${BACKEND_URL}/api/login/github`} className="flex gap-2 items-center bg-gray-800 px-4 py-2 rounded-md hover:bg-gray-700">
        <img src="/github-logo.png" alt="GitHub" className="h-6 w-6" /> Sign in with GitHub
      </a>
    </div>
  </div>
);

export default Login;
