import { Component, inject } from '@angular/core';
import { NavigationStart, NavigationEnd, NavigationCancel, NavigationError, Router, RouterOutlet } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Navbar } from './components/navbar';
import { Footer } from './components/footer';
import { Sidebar } from './components/sidebar';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Navbar, Footer, Sidebar],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  auth = inject(AuthService);
  router = inject(Router);
  chargement = false;
  get espacePersonnel(): boolean {
    return !!this.auth.utilisateur && /^\/(proprietaire|reservations|favoris|profil|reserver)(\/|\?|$)/.test(this.router.url);
  }
  constructor() {
    this.router.events.pipe(takeUntilDestroyed()).subscribe(event => {
      if (event instanceof NavigationStart) this.chargement = true;
      if (event instanceof NavigationEnd || event instanceof NavigationCancel || event instanceof NavigationError) this.chargement = false;
    });
  }
}
