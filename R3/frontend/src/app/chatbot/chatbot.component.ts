import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chatbot',
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent {
  messages: { text: string, type: string }[] = [];
  userMessage: string = "";
  isLoading: boolean = false;

  constructor(private http: HttpClient) {}

  sendMessage() {
    if (this.userMessage.trim() === "" || this.isLoading) return;

    // Ajout du message utilisateur dans le chat
    this.messages.push({ text: this.userMessage, type: "user" });

    // Payload pour l'API
    const payload = {
      session_id: "user_session_123",
      user_input: this.userMessage
    };

    // Définition des en-têtes HTTP
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    // Passage en mode chargement
    this.isLoading = true;

    // Envoi de la requête HTTP avec réponse attendue en texte
    this.http.post("http://localhost:8010/pipeline", payload, { headers, responseType: 'text' })
      .subscribe({
        next: (response: string) => {
          console.log("API Response:", response);

          // Prétraitement de la réponse
          let processedResponse = response.trim();

          // Suppression des guillemets en début et fin, s'ils existent
          if (processedResponse.startsWith('"') && processedResponse.endsWith('"')) {
            processedResponse = processedResponse.substring(1, processedResponse.length - 1);
          }

          // Remplacement des "\n" littéraux par de véritables retours à la ligne
          processedResponse = processedResponse.replace(/\\n/g, '\n');

          // Ajout du message du bot dans le chat
          this.messages.push({ text: processedResponse, type: "bot" });
          this.isLoading = false;
        },
        error: (error) => {
          console.error("API Error:", error);
          this.messages.push({ text: "Error: Could not connect to chatbot service.", type: "bot" });
          this.isLoading = false;
        }
      });

    // Réinitialisation du champ de saisie
    this.userMessage = "";
  }
}
