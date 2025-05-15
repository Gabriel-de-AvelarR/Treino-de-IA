import { Component, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface ChatResponse {
  status: string;
  message: string;
  response?: string;
  questions?: string;
  intent?: string;
  current_entities?: any;
  missing_entities?: any;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements AfterViewChecked {
  userInput = '';
  messages: { text: string; type: string }[] = [];
  currentState: any = null;

  @ViewChild('chatlog') chatlog!: ElementRef;

  constructor(private http: HttpClient) {}

  sendMessage() {
    if (!this.userInput.trim()) return;

    const input = this.userInput;
    this.messages.push({ text: input, type: 'user-msg' });
    this.userInput = '';

    this.http.post<any>('/api/chat', {
      message: input,
      state: this.currentState
    }).subscribe({
      next: (data: ChatResponse) => {
        if (data.status === 'missing_info') {
          this.currentState = {
            intent: data.intent,
            entities: data.current_entities,
            missing: data.missing_entities
          };
          this.messages.push({ text: data.questions ?? 'Sem resposta.', type: 'chat-msg' });
        } else if (data.status === 'sucess') {
          this.messages.push({ text: data.response ?? 'Sem resposta.', type: 'chat-msg' });
          this.currentState = null;
        } else {
          this.messages.push({ text: data.message, type: 'chat-msg error' });
        }
      },
      error: (err: any) => {
        this.messages.push({ text: 'Erro: ' + err.message, type: 'chat-msg error' });
      }
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom() {
    try {
      this.chatlog.nativeElement.scrollTop = this.chatlog.nativeElement.scrollHeight;
    } catch (err) {
      // falha silenciosa caso o elemento ainda não esteja disponível
    }
  }
}
