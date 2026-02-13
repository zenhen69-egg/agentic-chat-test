import { Component, EventEmitter, Input, Output, ViewChild, ElementRef } from '@angular/core';
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
export class CopilotSidebarComponent {
  @ViewChild('chatInput') chatInput!: ElementRef<HTMLInputElement>;
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

  messages: AgentMessage[] = [
    {
      role: 'assistant',
      content: 'Hello! I can help you fill out this form. Just tell me what to do.',
    },
  ];

  constructor(private agentApi: AgentApiService) {}

  private scrollToBottom() {
    setTimeout(() => {
      if (this.chatMessages?.nativeElement) {
        this.chatMessages.nativeElement.scrollTop = this.chatMessages.nativeElement.scrollHeight;
      }
    }, 100);
  }

  // Public method to programmatically send messages
  sendProgrammaticMessage(message: string) {
    this.userInput = message;
    this.sendToAgent();
  }

  // Public method to reset the session
  resetSession() {
    this.sessionId = '';
    this.currentAction = '';
    this.messages = [
      {
        role: 'assistant',
        content: 'Hello! I can help you fill out this form. Just tell me what to do.',
      },
    ];
  }

  sendToAgent() {
    if (!this.userInput.trim() || this.isSending) return;

    const userMessage = this.userInput.trim();
    this.isSending = true;

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
        
        // Refocus the input after request completes
        setTimeout(() => {
          this.chatInput?.nativeElement?.focus();
        }, 0);
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          content: 'Sorry, I ran into an error. Please try again.',
        });
        this.isSending = false;
        this.scrollToBottom();
        
        // Refocus the input after error
        setTimeout(() => {
          this.chatInput?.nativeElement?.focus();
        }, 0);
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
