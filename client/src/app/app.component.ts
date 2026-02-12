import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainFormComponent } from './layout/mainform/mainform';
import { CopilotSidebarComponent } from './shared/copilot-sidebar/copilot-sidebar';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { MatButtonModule, MatFabButton } from '@angular/material/button';

@Component({
  selector: 'app-root',
  imports: [
    MainFormComponent,
    CopilotSidebarComponent,
    MatIcon,
    MatFabButton,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  isChatOpen = true; // Default state
}
