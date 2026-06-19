"use client";

import { useEffect, useState } from "react";
import { apiClient, HealthResponse, ApiError } from "@/lib/api-client";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white px-4">
      <h1 className="text-4xl font-semibold mb-4">AI Analytics Copilot</h1>
      <p className="text-zinc-400 mb-8 text-center max-w-md">
        An AI copilot for data analysts — not a replacement.
      </p>
      <div className="flex gap-4">
        <a href="/login" className="rounded-md bg-zinc-800 px-5 py-2 hover:bg-zinc-700">
          Log In
        </a>
        <a href="/signup" className="rounded-md bg-blue-600 px-5 py-2 hover:bg-blue-500">
          Sign Up
        </a>
      </div>
    </main>
  );
}