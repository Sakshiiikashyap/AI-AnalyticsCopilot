"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { createChatSession, listChatMessages, sendChatMessage } from "@/lib/chat";
import type { ChatMessageResponse } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";

export default function DatasetChatPage() {
  const params = useParams();
  const router = useRouter();
  const datasetId = params.id as string;

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageResponse[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function init() {
      try {
        const session = await createChatSession(datasetId);
        setSessionId(session.id);
        const existing = await listChatMessages(session.id);
        setMessages(existing);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/login");
        } else {
          setError(err instanceof ApiError ? err.message : "Failed to start chat session.");
        }
      }
    }
    init();
  }, [datasetId, router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || !sessionId || sending) return;

    const question = input.trim();
    setInput("");
    setSending(true);
    setError(null);

    try {
      const reply = await sendChatMessage(sessionId, question);
      setMessages((prev) => [
        ...prev,
        { id: "u-" + reply.id, role: "user", content: question, computed_context: null, created_at: reply.created_at },
        reply,
      ]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to get a response.");
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      handleSend();
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white flex flex-col">
      <div className="max-w-3xl mx-auto w-full flex flex-col flex-1 px-6 py-6">
        <button
          onClick={() => router.push("/dashboard/datasets/" + datasetId)}
          className="text-zinc-400 hover:text-white mb-4 text-left"
        >
          Back to dataset
        </button>

        <h1 className="text-2xl font-semibold mb-4">Chat with your data</h1>

        <div className="flex-1 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-900 p-4 space-y-4 mb-4 min-h-[400px] max-h-[60vh]">
          {messages.length === 0 && (
            <p className="text-zinc-500 text-sm">
              Ask something like: which category generates the most revenue, or are there any outliers.
            </p>
          )}

          {messages.map((m) => (
            <div key={m.id} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={
                  m.role === "user"
                    ? "max-w-[80%] rounded-lg bg-blue-600 px-4 py-2 text-sm"
                    : "max-w-[80%] rounded-lg bg-zinc-800 px-4 py-2 text-sm whitespace-pre-wrap"
                }
              >
                {m.content}
              </div>
            </div>
          ))}

          {sending && <p className="text-zinc-500 text-sm">Thinking...</p>}

          <div ref={bottomRef} />
        </div>

        {error && <p className="text-red-400 text-sm mb-2">{error}</p>}

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about this dataset..."
            disabled={!sessionId || sending}
            className="flex-1 rounded-md bg-zinc-900 border border-zinc-700 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={!sessionId || sending || !input.trim()}
            className="rounded-md bg-blue-600 px-4 py-2 hover:bg-blue-500 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </main>
  );
}