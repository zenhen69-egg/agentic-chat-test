import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { ReactiveFormsModule, FormGroup, FormControl } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { UserProfile } from './models';

@Component({
  selector: 'app-user-profile-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './user-profile-form.html',
})
export class UserProfileFormComponent implements OnChanges {
  @Input() profile: UserProfile = {
    fullName: '',
    email: '',
    bio: '',
    isComplete: false,
  };
  @Input() isSubmitting = false;
  @Output() profileChange = new EventEmitter<UserProfile>();
  @Output() submitForm = new EventEmitter<void>();

  profileForm = new FormGroup({
    fullName: new FormControl(''),
    email: new FormControl(''),
    bio: new FormControl(''),
  });

  constructor() {
    this.profileForm.valueChanges.subscribe((value) => {
      this.profileChange.emit({
        fullName: value.fullName || '',
        email: value.email || '',
        bio: value.bio || '',
        isComplete: this.profile.isComplete,
      });
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['profile'] && this.profile) {
      this.profileForm.patchValue(
        {
          fullName: this.profile.fullName,
          email: this.profile.email,
          bio: this.profile.bio,
        },
        { emitEvent: false }
      );
    }
  }

  onSubmit() {
    this.submitForm.emit();
  }
}
