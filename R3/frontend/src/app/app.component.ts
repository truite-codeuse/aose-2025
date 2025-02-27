import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar'; // Import MatToolbarModule
import { MatInputModule } from '@angular/material/input';
import {MatMenuModule} from '@angular/material/menu';
import { GoogleMapsModule } from '@angular/google-maps';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';

import { MatSidenavModule } from '@angular/material/sidenav';

import { MatListModule } from '@angular/material/list';

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [
    CommonModule,
    RouterOutlet,
    RouterModule,
    MatToolbarModule, // Add MatToolbarModule here
    MatInputModule, 
    MatMenuModule, 
    GoogleMapsModule, 
    RouterModule, 
    MatButtonModule, MatIconModule,
    MatSidenavModule,
   
    MatListModule,
    
    



    
    
      // Add MatInputModule

  ],

})
export class AppComponent {
  title = 'My Angular App';
}