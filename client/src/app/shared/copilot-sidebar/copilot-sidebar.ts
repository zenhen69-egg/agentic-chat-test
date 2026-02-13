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
import {
  AgentChatRequest,
  AgentChatResponse,
  AgentMessage,
  AgentProfilePayload,
  UserProfile,
} from '../models/profile';
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
  @Input() profile: UserProfile = {
    fullName: '',
    email: '',
    bio: '',
    isComplete: false,
  };
  @Output() close = new EventEmitter<void>();
  @Output() profileUpdate = new EventEmitter<UserProfile>();
  @Output() submitRequest = new EventEmitter<void>();
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

  messages: AgentMessage[] = [
    {
      role: 'assistant',
      content: 'Hello! I can help you fill out this form. Just tell me what to do.',
    },
  ];

  constructor(private agentApi: AgentApiService, private ngZone: NgZone) {}

  ngOnInit() {
    this.setupSpeechRecognition();
    if (this.isOpen) {
      this.startListening();
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['isOpen']) {
      if (this.isOpen) {
        this.startListening();
      } else {
        this.stopListening();
      }
    }
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
          this.liveTranscript = cleaned;
          this.sendProgrammaticMessage(cleaned);
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
    if (!this.speechSupported || this.isListening || this.isSending) {
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
        fullName: '',
        email: '',
        bio: '',
        isComplete: false,
      });
      this.messages = [
        {
          role: 'assistant',
          content: 'Hello! I can help you fill out this form. Just tell me what to do.',
        },
      ];
      this.scrollToBottom();
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
      if (this.isOpen) {
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

    const payload: AgentChatRequest = {
      message: userMessage,
      history: this.messages,
      profile: this.toApiProfile(this.profile),
      session_id: this.sessionId || undefined,
    };

    this.agentApi.sendMessage(payload).subscribe({
      next: (response: AgentChatResponse) => {
        this.sessionId = response.session_id;
        this.currentAction = response.action;
        
        let displayMessage = response.message;
        if (response.action === 'submit_request') {
          displayMessage += '\n\n✅ **[SUBMITTED]** Your request has been successfully submitted!';
          this.submitRequest.emit();
        } else if (response.action === 'request_confirmation') {
          displayMessage += '\n\n⏳ **[AWAITING CONFIRMATION]** Please confirm to proceed.';
        }
        
        this.messages.push({ role: 'assistant', content: displayMessage });
        const updatedProfile = this.fromApiProfile(response.profile);
        this.profileUpdate.emit(updatedProfile);
        this.isSending = false;
        this.scrollToBottom();

        if (this.isOpen) {
          this.startListening();
        }
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          content: 'Sorry, I ran into an error. Please try again.',
        });
        this.isSending = false;
        this.scrollToBottom();

        if (this.isOpen) {
          this.startListening();
        }
      },
    });
  }

  toggleSidebar() {
    this.close.emit();
  }

  private toApiProfile(profile: UserProfile): AgentProfilePayload {
    return {
      full_name: profile.fullName,
      email: profile.email,
      bio: profile.bio,
      is_complete: profile.isComplete,
    };
  }

  private fromApiProfile(profile: AgentProfilePayload): UserProfile {
    return {
      fullName: profile.full_name || '',
      email: profile.email || '',
      bio: profile.bio || '',
      isComplete: profile.is_complete ?? false,
    };
  }
}
