export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatResponse {
  session_id: string;
  user_message: Message;
  assistant_message: Message;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: Message[];
}

export interface SessionListResponse {
  sessions: Session[];
  total: number;
}
