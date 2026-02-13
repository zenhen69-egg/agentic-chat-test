import { Component, signal, ViewChild } from '@angular/core';
import { MatTabChangeEvent, MatTabsModule } from '@angular/material/tabs';
import { SortingInputFormComponent } from './features/sorting-input/sorting-input-form';
import { UserProfileFormComponent } from './features/user-profile/user-profile-form';
import { CopilotSidebarComponent } from './shared/copilot-sidebar/copilot-sidebar';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { MatButtonModule, MatFabButton } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FeatureKey } from './shared/models/chat';
import { SortingInput } from './features/sorting-input/models';
import { UserProfile } from './features/user-profile/models';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  imports: [
    MatTabsModule,
    SortingInputFormComponent,
    UserProfileFormComponent,
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
  isSubmittingByFeature = signal<Record<FeatureKey, boolean>>({
    'user-profile': false,
    'sorting-input': false,
  });
  isTesting = environment.copilotTesting ?? false;
  activeTabIndex = 0;
  activeFeature: FeatureKey = 'user-profile';
  userProfile: UserProfile = {
    fullName: '',
    email: '',
    bio: '',
    isComplete: false,
  };
  sortingInput: SortingInput = {
    sorterId: '',
    tagSerialNo: '',
    isComplete: false,
  };

  constructor(private snackBar: MatSnackBar) {}

  handleProfileChange(profile: UserProfile) {
    this.userProfile = { ...profile };
  }

  handleSortingChange(sorting: SortingInput) {
    this.sortingInput = { ...sorting };
  }

  handleProfileUpdate(event: { feature: FeatureKey; profile: UserProfile | SortingInput }) {
    if (event.feature === 'sorting-input') {
      this.sortingInput = { ...(event.profile as SortingInput) };
    } else {
      this.userProfile = { ...(event.profile as UserProfile) };
    }
  }

  async handleSubmitRequest() {
    // Use the chat agent to handle submission validation
    // Send confirmation phrase to auto-confirm
    this.copilotSidebar.sendProgrammaticMessage('submit now');
  }

  onActualSubmit(feature: FeatureKey) {
    this.setSubmitting(feature, true);
    const activeProfile = feature === 'sorting-input' ? this.sortingInput : this.userProfile;
    console.log('✅ Submit request triggered', activeProfile);
    
    // Simulate 2-second delay for long-running request
    setTimeout(() => {
      const details = feature === 'sorting-input'
        ? `Sorter ID: ${this.sortingInput.sorterId}\nTag Serial No.: ${this.sortingInput.tagSerialNo}`
        : `Name: ${this.userProfile.fullName}\nEmail: ${this.userProfile.email}\nBio: ${this.userProfile.bio}`;
      const title = feature === 'sorting-input' ? '✅ Sorting Input Submitted!' : '✅ Profile Submitted!';
      this.snackBar.open(`${title}\n\n${details}`, 'Close', {
        duration: 8000,
        horizontalPosition: 'center',
        verticalPosition: 'top',
        panelClass: ['success-snackbar']
      });
      
      // Clear all fields after submission
      if (feature === 'sorting-input') {
        this.sortingInput = {
          sorterId: '',
          tagSerialNo: '',
          isComplete: false,
        };
      } else {
        this.userProfile = {
          fullName: '',
          email: '',
          bio: '',
          isComplete: false,
        };
      }
      
      // Reset the agent session so it doesn't remember old data
      this.copilotSidebar.resetSession();
      
      this.setSubmitting(feature, false);
    }, 2000);
  }

  onTabChange(event: MatTabChangeEvent) {
    this.activeTabIndex = event.index;
    this.activeFeature = event.index === 1 ? 'sorting-input' : 'user-profile';
  }

  isSubmitting(feature: FeatureKey): boolean {
    return this.isSubmittingByFeature()[feature] ?? false;
  }

  private setSubmitting(feature: FeatureKey, value: boolean) {
    this.isSubmittingByFeature.set({
      ...this.isSubmittingByFeature(),
      [feature]: value,
    });
  }
}
