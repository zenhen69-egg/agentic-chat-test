import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

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
  @Input() isOpen = true;
  @Output() close = new EventEmitter<void>();
  userInput = '';

  messages = [
    {
      role: 'assistant',
      content: 'Hello! I can help you fill out this form. Just tell me what to do.',
    },
  ];

  sendToAgent() {
    if (!this.userInput.trim()) return;

    this.messages.push({ role: 'user', content: this.userInput });
    this.userInput = '';

    // Logic for calling the OpenAI SDK goes here next
  }

  toggleSidebar() {
    this.close.emit();
  }
}
