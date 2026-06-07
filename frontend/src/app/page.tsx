"use client";

import { useEffect, useState } from "react";
import { chatApi, sessionApi } from "@/services/api";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { SessionSidebar } from "@/components/chat/SessionSidebar";
import type { Session } from "@/types";

export default function Home() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  useEffect(() => {
    sessionApi.list().then((res) => {
      setSessions(res.sessions);
      if (res.sessions.length > 0) setActiveId(res.sessions[0].id);
    });
  }, []);

  async function handleCreate() {
    const session = await sessionApi.create();
    setSessions((prev) => [session, ...prev]);
    setActiveId(session.id);
  }

  async function handleDelete(id: string) {
    await sessionApi.delete(id);
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (activeId === id) {
      const remaining = sessions.filter((s) => s.id !== id);
      setActiveId(remaining.length > 0 ? remaining[0].id : null);
    }
  }

  return (
    <div className="flex h-full">
      <SessionSidebar
        sessions={sessions}
        activeSessionId={activeId}
        onSelect={setActiveId}
        onCreate={handleCreate}
        onDelete={handleDelete}
      />
      <main className="flex-1 flex flex-col bg-white overflow-hidden">
        {activeId ? (
          <ChatWindow sessionId={activeId} />
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <p className="text-lg font-medium">Nenhuma conversa selecionada</p>
              <p className="text-sm mt-1">Clique em &quot;Nova conversa&quot; para começar</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
