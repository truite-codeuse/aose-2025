import { Routes } from '@angular/router';
import { ChatbotComponent } from './chatbot/chatbot.component';

export const routes: Routes = [

  {
    path: 'chatbot', // Route for Optimal Assignment
    component: ChatbotComponent,
  },
  {
    path: '**', // Wildcard route for 404 page
    component : ChatbotComponent, // Redirects to the default path
  },
];