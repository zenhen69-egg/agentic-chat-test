export type FeatureKey = 'user-profile' | 'sorting-input';

export interface AgentMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}
