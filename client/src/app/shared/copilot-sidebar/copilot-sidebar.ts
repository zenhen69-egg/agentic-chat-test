import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  NgZone,
  OnChanges,
  OnDestroy,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { FeatureKey, AgentMessage } from '../models/chat';
import { SortingInput, SortingInputPayload } from '../../features/sorting-input/models';
import { SortingChatRequest, SortingChatResponse } from '../../features/sorting-input/types';
import { UserProfile, UserProfilePayload } from '../../features/user-profile/models';
import { UserProfileChatRequest, UserProfileChatResponse } from '../../features/user-profile/types';
import { AgentApiService } from '../services/agent-api.service';

@Component({
  selector: 'app-copilot-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './copilot-sidebar.html',
  styleUrls: ['./copilot-sidebar.css'],
})
export class CopilotSidebarComponent implements OnInit, OnChanges, OnDestroy {
  @ViewChild('chatMessages') chatMessages!: ElementRef<HTMLDivElement>;
  @Input() isOpen = true;
  @Input() showKeyboard = false;
  @Input() autoListen = true;
  @Input() allowVoiceInTesting = false;
  @Input() feature: FeatureKey = 'user-profile';
  @Input() profile: UserProfile | SortingInput = {
    fullName: '',
    email: '',
    bio: '',
    isComplete: false,
  };
  @Output() close = new EventEmitter<void>();
  @Output() profileUpdate = new EventEmitter<{ feature: FeatureKey; profile: UserProfile | SortingInput }>();
  @Output() submitRequest = new EventEmitter<FeatureKey>();
  userInput = '';
  isSending = false;
  sessionId = '';
  currentAction = '';
  isListening = false;
  speechSupported = false;
  liveTranscript = '';
  speechError = '';
  private recognition: any = null;
  private shouldRestart = false;
  voiceEnabled = true;

  messages: AgentMessage[] = [];

  private featureState: Record<FeatureKey, { sessionId: string; currentAction: string; messages: AgentMessage[] }>;

  constructor(private agentApi: AgentApiService, private ngZone: NgZone) {
    this.featureState = {
      'user-profile': {
        sessionId: '',
        currentAction: '',
        messages: [
          {
            role: 'assistant',
            content: this.getWelcomeMessage('user-profile'),
          },
        ],
      },
      'sorting-input': {
        sessionId: '',
        currentAction: '',
        messages: [
          {
            role: 'assistant',
            content: this.getWelcomeMessage('sorting-input'),
          },
        ],
      },
    };
    this.syncFeatureState();
  }

  ngOnInit() {
    this.setupSpeechRecognition();
    this.voiceEnabled = this.autoListen;
    if (this.isOpen && this.canListen()) {
      this.startListening();
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['feature']) {
      this.syncFeatureState();
      this.scrollToBottom();
    }
    if (changes['isOpen']) {
      if (this.isOpen) {
        if (this.canListen()) {
          this.startListening();
        }
      } else {
        this.stopListening();
      }
    }
    if (changes['autoListen'] && this.isOpen) {
      this.voiceEnabled = this.autoListen;
      if (this.canListen()) {
        this.startListening();
      } else {
        this.stopListening();
      }
    }
  }

  get featureTitle(): string {
    return this.feature === 'sorting-input' ? 'Sorting Input' : 'User Profile';
  }

  get voicePlaceholder(): string {
    return this.feature === 'sorting-input'
      ? 'Speak your sorter ID and tag serial number.'
      : 'Speak your details to update the profile.';
  }

  ngOnDestroy() {
    this.stopListening();
  }

  private scrollToBottom() {
    setTimeout(() => {
      if (this.chatMessages?.nativeElement) {
        this.chatMessages.nativeElement.scrollTop = this.chatMessages.nativeElement.scrollHeight;
      }
    }, 100);
  }

  private setupSpeechRecognition() {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      this.speechSupported = false;
      this.speechError = 'Voice input is not supported in this browser.';
      return;
    }

    this.speechSupported = true;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    this.recognition.onresult = (event: any) => {
      this.ngZone.run(() => {
        this.speechError = '';
        let interimText = '';
        let finalText = '';

        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const result = event.results[i];
          if (result.isFinal) {
            finalText += result[0].transcript;
          } else {
            interimText += result[0].transcript;
          }
        }

        if (interimText.trim()) {
          this.liveTranscript = interimText.trim();
        }

        if (finalText.trim()) {
          const cleaned = finalText.trim();
          const normalized = this.normalizeVoiceInput(cleaned);
          this.liveTranscript = normalized;
          this.sendProgrammaticMessage(normalized);
        }
      });
    };

    this.recognition.onerror = () => {
      this.ngZone.run(() => {
        this.isListening = false;
        this.speechError = 'Microphone access is blocked. Please enable it for this site.';
        if (this.shouldRestart && this.isOpen && !this.isSending) {
          setTimeout(() => this.startListening(), 500);
        }
      });
    };

    this.recognition.onend = () => {
      this.ngZone.run(() => {
        const restart = this.shouldRestart && this.isOpen && !this.isSending;
        this.isListening = false;
        if (restart) {
          this.startListening();
        }
      });
    };
  }

  startListening() {
    if (!this.canListen() || !this.speechSupported || this.isListening || this.isSending) {
      return;
    }

    this.shouldRestart = true;
    this.liveTranscript = '';
    this.speechError = '';
    try {
      this.recognition?.start();
      this.isListening = true;
    } catch {
      this.speechError = 'Unable to start microphone. Check browser permissions.';
      this.isListening = false;
    }
  }

  stopListening() {
    this.shouldRestart = false;
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
    this.isListening = false;
  }

  toggleVoiceEnabled() {
    if (!this.allowVoiceInTesting) {
      return;
    }
    this.voiceEnabled = !this.voiceEnabled;
    if (this.voiceEnabled && this.isOpen && !this.isSending) {
      this.startListening();
    } else {
      this.stopListening();
    }
  }

  // Public method to programmatically send messages
  sendProgrammaticMessage(message: string) {
    this.userInput = message;
    this.sendToAgent();
  }

  // Public method to reset the session
  resetSession() {
    this.ngZone.run(() => {
      this.stopListening();
      this.sessionId = '';
      this.currentAction = '';
      this.liveTranscript = '';
      this.speechError = '';
      this.userInput = '';
      this.isSending = false;
      this.profileUpdate.emit({
        feature: this.feature,
        profile: this.getEmptyProfile(),
      });
      this.messages = [
        {
          role: 'assistant',
          content: this.getWelcomeMessage(this.feature),
        },
      ];
      this.updateFeatureState();
      this.scrollToBottom();
      if (this.isOpen && this.canListen()) {
        this.startListening();
      }
    });
  }

  sendToAgent() {
    if (!this.userInput.trim() || this.isSending) return;

    const userMessage = this.userInput.trim();
    if (userMessage.toLowerCase() === 'cancel') {
      this.messages.push({ role: 'user', content: userMessage });
      this.resetSession();
      this.messages.push({
        role: 'assistant',
        content: 'All set. I started a new session. What would you like to do next?',
      });
      this.scrollToBottom();
      if (this.isOpen && this.canListen()) {
        this.startListening();
      }
      return;
    }
    this.isSending = true;

    if (this.isListening) {
      this.stopListening();
    }

    this.messages.push({ role: 'user', content: userMessage });
    this.userInput = '';
    this.scrollToBottom();

    if (this.feature === 'sorting-input') {
      const payload: SortingChatRequest = {
        message: userMessage,
        history: this.messages,
        sorting: this.toApiSorting(this.profile as SortingInput),
        session_id: this.sessionId || undefined,
      };
      this.agentApi.sendSortingMessage(payload).subscribe({
        next: (response: SortingChatResponse) => {
          this.handleAgentResponse(response.action, response.message);
          const updatedSorting = this.fromApiSorting(response.sorting);
          this.profileUpdate.emit({ feature: this.feature, profile: updatedSorting });
          this.sessionId = response.session_id;
          this.currentAction = response.action;
          this.updateFeatureState();
        },
        error: () => {
          this.handleAgentError();
        },
      });
    } else {
      const payload: UserProfileChatRequest = {
        message: userMessage,
        history: this.messages,
        profile: this.toApiProfile(this.profile as UserProfile),
        session_id: this.sessionId || undefined,
      };
      this.agentApi.sendProfileMessage(payload).subscribe({
        next: (response: UserProfileChatResponse) => {
          this.handleAgentResponse(response.action, response.message);
          const updatedProfile = this.fromApiProfile(response.profile);
          this.profileUpdate.emit({ feature: this.feature, profile: updatedProfile });
          this.sessionId = response.session_id;
          this.currentAction = response.action;
          this.updateFeatureState();
        },
        error: () => {
          this.handleAgentError();
        },
      });
    }
  }

  toggleSidebar() {
    this.close.emit();
  }

  private toApiProfile(profile: UserProfile): UserProfilePayload {
    return {
      full_name: profile.fullName,
      email: profile.email,
      bio: profile.bio,
      is_complete: profile.isComplete,
    };
  }

  private fromApiProfile(profile: UserProfilePayload): UserProfile {
    return {
      fullName: profile.full_name || '',
      email: profile.email || '',
      bio: profile.bio || '',
      isComplete: profile.is_complete ?? false,
    };
  }

  private toApiSorting(sorting: SortingInput): SortingInputPayload {
    return {
      sorter_id: sorting.sorterId,
      tag_serial_no: sorting.tagSerialNo,
      is_complete: sorting.isComplete,
    };
  }

  private fromApiSorting(sorting: SortingInputPayload): SortingInput {
    return {
      sorterId: sorting.sorter_id || '',
      tagSerialNo: sorting.tag_serial_no || '',
      isComplete: sorting.is_complete ?? false,
    };
  }

  private handleAgentResponse(action: string, message: string) {
    let displayMessage = message;
    if (action === 'submit_request') {
      displayMessage += '\n\n✅ **[SUBMITTED]** Your request has been successfully submitted!';
      this.submitRequest.emit(this.feature);
    } else if (action === 'request_confirmation') {
      displayMessage += '\n\n⏳ **[AWAITING CONFIRMATION]** Please confirm to proceed.';
    }

    this.messages.push({ role: 'assistant', content: displayMessage });
    this.isSending = false;
    this.scrollToBottom();

    if (this.isOpen && this.canListen()) {
      this.startListening();
    }
  }

  private handleAgentError() {
    this.messages.push({
      role: 'assistant',
      content: 'Sorry, I ran into an error. Please try again.',
    });
    this.isSending = false;
    this.scrollToBottom();

    if (this.isOpen && this.canListen()) {
      this.startListening();
    }
  }

  private getWelcomeMessage(feature: FeatureKey): string {
    return feature === 'sorting-input'
      ? 'Hi! Share the sorter ID and tag serial number, and I will fill those in for you.'
      : 'Hello! I can help you fill out this form. Just tell me what to do.';
  }

  private getEmptyProfile(): UserProfile | SortingInput {
    if (this.feature === 'sorting-input') {
      return { sorterId: '', tagSerialNo: '', isComplete: false };
    }
    return { fullName: '', email: '', bio: '', isComplete: false };
  }

  private syncFeatureState() {
    const state = this.featureState[this.feature];
    this.sessionId = state.sessionId;
    this.currentAction = state.currentAction;
    this.messages = state.messages;
  }

  private updateFeatureState() {
    const state = this.featureState[this.feature];
    state.sessionId = this.sessionId;
    state.currentAction = this.currentAction;
    state.messages = this.messages;
  }

  private canListen(): boolean {
    return this.autoListen || (this.allowVoiceInTesting && this.voiceEnabled);
  }

  private normalizeVoiceInput(text: string): string {
    let normalized = text;

    normalized = normalized.replace(/\s+(equals|=)\s+/gi, ' = ');
    normalized = normalized.replace(/\s*:\s*/g, ' : ');
    normalized = normalized.replace(/\s+at\s+/gi, '@');
    normalized = normalized.replace(/\s+dot\s+/gi, '.');
    normalized = normalized.replace(/\s+underscore\s+/gi, '_');
    normalized = normalized.replace(/\s+dash\s+/gi, '-');

    normalized = this.collapseSpelledSequences(normalized);
    normalized = this.collapseValueAfterKeyword(normalized);
    if (this.feature === 'sorting-input') {
      normalized = this.collapseSortingValues(normalized);
    }

    normalized = normalized.replace(/\s{2,}/g, ' ').trim();

    return normalized;
  }

  private collapseSpelledSequences(text: string): string {
    const sequencePattern = /(?:\b[A-Za-z0-9]{1,2}\b\s+){2,}\b[A-Za-z0-9]{1,2}\b/g;
    return text.replace(sequencePattern, (match) => {
      const parts = match.trim().split(/\s+/);
      const hasSingleChar = parts.some((part) => part.length === 1);
      if (!hasSingleChar) {
        return match;
      }
      return parts.join('');
    });
  }

  private collapseValueAfterKeyword(text: string): string {
    const valuePattern = /(\b(?:is|equals|=|to|:)\b\s+)([A-Za-z0-9@._-]+(?:\s+[A-Za-z0-9@._-]+)+)/gi;
    return text.replace(valuePattern, (_match, prefix: string, value: string) => {
      const collapsed = value.replace(/\s+/g, '');
      return `${prefix}${collapsed}`;
    });
  }

  private collapseSortingValues(text: string): string {
    const tokens = text.trim().split(/\s+/);
    const stopwords = new Set([
      'sorter',
      'id',
      'tag',
      'serial',
      'no',
      'number',
      'is',
      'equals',
      '=',
      'to',
      ':',
    ]);
    const result: string[] = [];
    let buffer: string[] = [];

    const flush = () => {
      if (buffer.length) {
        result.push(buffer.join(''));
        buffer = [];
      }
    };

    for (const token of tokens) {
      const lower = token.toLowerCase();
      const isValueToken = /^[A-Za-z0-9@._-]+$/.test(token) && !stopwords.has(lower);
      if (isValueToken) {
        buffer.push(token);
      } else {
        flush();
        result.push(token);
      }
    }
    flush();

    return result.join(' ');
  }
}
