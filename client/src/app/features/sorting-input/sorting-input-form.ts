import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { ReactiveFormsModule, FormGroup, FormControl } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { SortingInput } from './models';

@Component({
  selector: 'app-sorting-input-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './sorting-input-form.html',
})
export class SortingInputFormComponent implements OnChanges {
  @Input() sorting: SortingInput = {
    sorterId: '',
    tagSerialNo: '',
    isComplete: false,
  };
  @Input() isSubmitting = false;
  @Output() sortingChange = new EventEmitter<SortingInput>();
  @Output() submitForm = new EventEmitter<void>();

  sortingForm = new FormGroup({
    sorterId: new FormControl(''),
    tagSerialNo: new FormControl(''),
  });

  constructor() {
    this.sortingForm.valueChanges.subscribe((value) => {
      this.sortingChange.emit({
        sorterId: value.sorterId || '',
        tagSerialNo: value.tagSerialNo || '',
        isComplete: this.sorting.isComplete,
      });
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['sorting'] && this.sorting) {
      this.sortingForm.patchValue(
        {
          sorterId: this.sorting.sorterId,
          tagSerialNo: this.sorting.tagSerialNo,
        },
        { emitEvent: false }
      );
    }
  }

  onSubmit() {
    this.submitForm.emit();
  }
}
