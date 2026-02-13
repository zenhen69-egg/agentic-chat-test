import { AgentMessage } from '../../shared/models/chat';
import { SortingInputPayload } from './models';

export interface SortingChatRequest {
  message: string;
  history: AgentMessage[];
  sorting: SortingInputPayload;
  session_id?: string;
}

export interface SortingChatResponse {
  message: string;
  action: string;
  missing_fields: string[];
  sorting: SortingInputPayload;
  is_complete: boolean;
  session_id: string;
}
