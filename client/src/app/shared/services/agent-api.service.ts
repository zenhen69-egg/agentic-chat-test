import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AgentChatRequest, AgentChatResponse } from '../models/profile';

@Injectable({ providedIn: 'root' })
export class AgentApiService {
  private readonly baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  sendMessage(payload: AgentChatRequest): Observable<AgentChatResponse> {
    return this.http.post<AgentChatResponse>(`${this.baseUrl}/chat`, payload);
  }
}
