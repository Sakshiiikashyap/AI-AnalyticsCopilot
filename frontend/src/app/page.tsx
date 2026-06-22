"use client";

import { motion } from "framer-motion";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const features = [
  { title: "Automated Data Profiling", desc: "Missing values, duplicates, outliers, and correlations, computed automatically the moment you upload a file." },
  { title: "AI Chat With Your Data", desc: "Ask questions in plain English. Answers are grounded in real computed results from your actual dataset, not hallucinated guesses." },
  { title: "Built for Real Files", desc: "Upload CSV or Excel files directly. Schema inference, type detection, and data cleaning handled for you." },
  { title: "Outlier and Anomaly Detection", desc: "Statistical and machine learning based detection surfaces unusual records and patterns worth a second look." },
  { title: "Forecasting", desc: "Project future trends from your historical data using real time-series forecasting models." },
  { title: "You Stay in Control", desc: "This is a copilot, not a replacement. Every insight is traceable back to the exact computation behind it." },
];

export default function Home() {
  return (
    <main className="bg-zinc-950 text-white min-h-screen overflow-hidden">
      <nav className="sticky top-0 z-10 backdrop-blur-md bg-zinc-950/70 border-b border-zinc-900">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-5">
          <span className="font-semibold text-lg">AI Analytics Copilot</span>
          <div className="flex gap-3">
            <a href="/login" className="px-4 py-2 text-sm text-zinc-300 hover:text-white transition-colors">Log In</a>
            <a href="/signup" className="px-4 py-2 text-sm rounded-md bg-blue-600 hover:bg-blue-500 transition-all hover:scale-105 active:scale-95 duration-150">Sign Up</a>
          </div>
        </div>
      </nav>

      <div className="relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-blue-950/30 via-zinc-950 to-zinc-950" />

        <motion.section
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto text-center px-6 pt-20 pb-24"
        >
          <p className="text-blue-400 text-sm font-medium mb-4">AN AI COPILOT FOR DATA ANALYSTS, NOT A REPLACEMENT</p>
          <h1 className="text-5xl font-bold leading-tight mb-6">
            Turn raw spreadsheets into real insights, in minutes
          </h1>
          <p className="text-zinc-400 text-lg max-w-2xl mx-auto mb-10">
            Upload a CSV or Excel file and get automated data profiling, anomaly detection,
            and an AI assistant that answers questions about your data in plain English,
            grounded in real computed statistics, not guesses.
          </p>
          <div className="flex gap-4 justify-center">
            <a href="/signup" className="px-6 py-3 rounded-md bg-blue-600 hover:bg-blue-500 font-medium transition-all hover:scale-105 active:scale-95">Get Started Free</a>
            <a href="/login" className="px-6 py-3 rounded-md border border-zinc-700 hover:border-zinc-500 font-medium transition-all hover:scale-105 active:scale-95">Log In</a>
          </div>
        </motion.section>
      </div>

      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-zinc-900">
        <h2 className="text-2xl font-semibold text-center mb-12">Everything an analyst needs, automated</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((item, i) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: false }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 hover:border-zinc-700 hover:-translate-y-1 transition-all"
            >
              <h3 className="font-medium mb-2">{item.title}</h3>
              <p className="text-zinc-400 text-sm">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="max-w-3xl mx-auto text-center px-6 py-20 border-t border-zinc-900">
        <h2 className="text-2xl font-semibold mb-4">Ready to analyze your first dataset?</h2>
        <p className="text-zinc-400 mb-8">No credit card required. Upload a file and get insights in under a minute.</p>
        <a href="/signup" className="px-6 py-3 rounded-md bg-blue-600 hover:bg-blue-500 font-medium inline-block transition-all hover:scale-105 active:scale-95">Get Started Free</a>
      </section>

      <footer className="max-w-6xl mx-auto px-6 py-8 text-center text-zinc-600 text-sm border-t border-zinc-900">
        AI Analytics Copilot
      </footer>
    </main>
  );
}