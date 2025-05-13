import { Component, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';  // Importar CommonModule
import { FormsModule } from '@angular/forms';    // Importar FormsModule
import { HttpClient } from '@angular/common/http';  // Adicione esta linha


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
  standalone: true,  // Para indicar que o componente é autônomo
  imports: [CommonModule, FormsModule],  // Adicionar os módulos necessários aqui
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
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
        setTimeout(() => this.scrollToBottom(), 0);
      },
      error: (err: any) => {
        this.messages.push({ text: 'Erro: ' + err.message, type: 'chat-msg error' });
        this.scrollToBottom();
      }
    });
  }

  scrollToBottom() {
    this.chatlog.nativeElement.scrollTop = this.chatlog.nativeElement.scrollHeight;
  }
}
