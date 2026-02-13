import { Component, signal, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainFormComponent } from './layout/mainform/mainform';
import { CopilotSidebarComponent } from './shared/copilot-sidebar/copilot-sidebar';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { MatButtonModule, MatFabButton } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { UserProfile } from './shared/models/profile';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  imports: [
    MainFormComponent,
    CopilotSidebarComponent,
    MatIcon,
    MatFabButton,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  @ViewChild(CopilotSidebarComponent) copilotSidebar!: CopilotSidebarComponent;
  
  isChatOpen = false; // Default state
  isSubmitting = signal(false);
  isTesting = environment.copilotTesting ?? false;
  profile: UserProfile = {
    fullName: '',
    email: '',
    bio: '',
    isComplete: false,
  };

  constructor(private snackBar: MatSnackBar) {}

  handleProfileChange(profile: UserProfile) {
    this.profile = { ...profile };
  }

  handleProfileUpdate(profile: UserProfile) {
    this.profile = { ...profile };
  }

  async handleSubmitRequest() {
    // Use the chat agent to handle submission validation
    // Send confirmation phrase to auto-confirm
    this.copilotSidebar.sendProgrammaticMessage('submit now');
  }

  onActualSubmit() {
    this.isSubmitting.set(true);
    console.log('✅ Submit request triggered', this.profile);
    
    // Simulate 2-second delay for long-running request
    setTimeout(() => {
      const details = `Name: ${this.profile.fullName}\nEmail: ${this.profile.email}\nBio: ${this.profile.bio}`;
      this.snackBar.open(`✅ Profile Submitted!\n\n${details}`, 'Close', {
        duration: 8000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
        panelClass: ['success-snackbar']
      });
      
      // Clear all fields after submission
      this.profile = {
        fullName: '',
        email: '',
        bio: '',
        isComplete: false,
      };
      
      // Reset the agent session so it doesn't remember old data
      this.copilotSidebar.resetSession();
      
      this.isSubmitting.set(false);
    }, 2000);
  }
}
