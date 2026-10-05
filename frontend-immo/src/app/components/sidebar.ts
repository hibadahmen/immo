import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-sidebar',
  imports: [RouterLink, RouterLinkActive],
  template: `
    <aside class="sidebar">
      <div class="sidebar-person"><span class="avatar">{{auth.utilisateur?.prenom?.charAt(0)}}</span>
        <strong>{{auth.utilisateur?.prenom}} {{auth.utilisateur?.nom}}</strong>
        <small>{{auth.utilisateur?.role === 'proprietaire' ? 'Propriétaire' : 'Locataire'}}</small>
      </div>
      <nav aria-label="Navigation de votre espace">
        @if (auth.utilisateur?.role === 'proprietaire') {
          <a routerLink="/proprietaire" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">▦ Mes propriétés</a>
          <a routerLink="/proprietaire/ajouter" routerLinkActive="active">＋ Ajouter un bien</a>
          <a routerLink="/proprietaire/demandes" routerLinkActive="active">▤ Demandes reçues</a>
        } @else {
          <a routerLink="/reservations" routerLinkActive="active">▤ Mes réservations</a>
          <a routerLink="/favoris" routerLinkActive="active">♡ Mes favoris</a>
        }
        <a routerLink="/profil" routerLinkActive="active">◎ Mon profil</a>
        <a routerLink="/logements">⌕ Explorer les logements</a>
      </nav>
      <p class="sidebar-note">Un espace pour vos prochaines étapes.</p>
    </aside>`
})
export class Sidebar { auth = inject(AuthService); }
