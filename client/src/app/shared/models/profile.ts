export interface UserProfile {
  fullName: string;
  email: string;
  bio: string;
  isComplete: boolean;
}

export interface AgentMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AgentProfilePayload {
  full_name: string;
  email: string;
  bio: string;
  is_complete: boolean;
}

export interface AgentChatRequest {
  message: string;
  history: AgentMessage[];
  profile: AgentProfilePayload;
  session_id?: string;
}

export interface AgentChatResponse {
  message: string;
  action: string;
  missing_fields: string[];
  profile: AgentProfilePayload;
  is_complete: boolean;
  session_id: string;
}
