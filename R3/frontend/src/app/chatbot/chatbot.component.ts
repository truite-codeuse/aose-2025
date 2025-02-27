import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chatbot',
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.component.html',
  styleUrl: './chatbot.component.css'
})
export class ChatbotComponent {
  messages: { text: string, type: string }[] = [];
  userMessage: string = "";
  isLoading: boolean = false;

  constructor(private http: HttpClient) {}

  sendMessage() {
    if (this.userMessage.trim() === "" || this.isLoading) return;

    // Add user message to chat
    this.messages.push({ text: this.userMessage, type: "user" });

    // API payload
    const payload = {
      session_id: "user_session_123",
      user_input: this.userMessage
    };

    // Set loading state
    this.isLoading = true;

    // Send request directly to chatbot service
    this.http.post<{ response: string }>("http://localhost:8010/pipeline", payload)
      .subscribe(response => {
        // Add chatbot response to chat
        this.messages.push({ text: response.response, type: "bot" });
        this.isLoading = false;
      }, error => {
        console.error("Error communicating with chatbot:", error);
        this.messages.push({ text: "Error: Could not connect to chatbot service.", type: "bot" });
        this.isLoading = false;
      });

    this.userMessage = ""; // Clear input field
  }
}
