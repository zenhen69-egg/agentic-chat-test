import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SortingChatRequest, SortingChatResponse } from '../../features/sorting-input/types';
import { UserProfileChatRequest, UserProfileChatResponse } from '../../features/user-profile/types';

@Injectable({ providedIn: 'root' })
export class AgentApiService {
  private readonly baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  sendProfileMessage(payload: UserProfileChatRequest): Observable<UserProfileChatResponse> {
    return this.http.post<UserProfileChatResponse>(`${this.baseUrl}/chat/profile`, payload);
  }

  sendSortingMessage(payload: SortingChatRequest): Observable<SortingChatResponse> {
    return this.http.post<SortingChatResponse>(`${this.baseUrl}/chat/sorting`, payload);
  }
}
