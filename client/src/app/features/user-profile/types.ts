import { AgentMessage } from '../../shared/models/chat';
import { UserProfilePayload } from './models';

export interface UserProfileChatRequest {
  message: string;
  history: AgentMessage[];
  profile: UserProfilePayload;
  session_id?: string;
}

export interface UserProfileChatResponse {
  message: string;
  action: string;
  missing_fields: string[];
  profile: UserProfilePayload;
  is_complete: boolean;
  session_id: string;
}
