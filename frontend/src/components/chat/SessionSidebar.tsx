"use client";

import clsx from "clsx";
import { Plus, Trash2 } from "lucide-react";
import type { Session } from "@/types";

interface Props {
  sessions: Session[];
  activeSessionId: string | null;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
}

export function SessionSidebar({
  sessions,
  activeSessionId,
  onSelect,
  onCreate,
  onDelete,
}: Props) {
  return (
    <aside className="flex flex-col w-64 h-full bg-gray-900 text-white">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-semibold">ChatBot RAG</h1>
      </div>

      <button
        onClick={onCreate}
        className="flex items-center gap-2 mx-3 mt-3 px-3 py-2 rounded-lg border border-gray-600 text-sm hover:bg-gray-700 transition-colors"
      >
        <Plus size={16} />
        Nova conversa
      </button>

      <nav className="flex-1 overflow-y-auto mt-2 px-3 space-y-1">
        {sessions.map((s) => (
          <div
            key={s.id}
            className={clsx(
              "group flex items-center justify-between rounded-lg px-3 py-2 text-sm cursor-pointer transition-colors",
              s.id === activeSessionId ? "bg-gray-700" : "hover:bg-gray-800"
            )}
            onClick={() => onSelect(s.id)}
          >
            <span className="truncate flex-1">{s.title}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(s.id);
              }}
              className="opacity-0 group-hover:opacity-100 ml-2 text-gray-400 hover:text-red-400 transition-opacity"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </nav>
    </aside>
  );
}
