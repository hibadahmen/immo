import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { messageErreur } from '../services/api-error';
import { Bouton } from './bouton';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, RouterLinkActive, Bouton],
  template: `
    <header class="navbar">
      <a class="brand" routerLink="/" (click)="fermer()"><span class="brand-icon" aria-hidden="true">⌂</span> Darna<span class="brand-dot">.</span></a>
      <button class="menu-toggle" type="button" [attr.aria-expanded]="menuOuvert" aria-controls="navigation" (click)="menuOuvert = !menuOuvert">{{menuOuvert ? 'Fermer ×' : 'Menu ☰'}}</button>
      <nav id="navigation" [class.open]="menuOuvert" aria-label="Navigation principale">
        <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}" (click)="fermer()">Accueil</a>
        <a routerLink="/logements" routerLinkActive="active" (click)="fermer()">Logements</a>
        <a routerLink="/" fragment="comment-ca-marche" (click)="fermer()">Comment ça marche</a>
        <div class="nav-actions">
          @if (auth.utilisateur; as utilisateur) {
            <details class="profile-menu" #profil><summary><span class="avatar small-avatar">{{utilisateur.prenom.charAt(0)}}</span>{{utilisateur.prenom}} <span aria-hidden="true">⌄</span></summary>
              <div class="profile-dropdown">
                <a [routerLink]="utilisateur.role === 'proprietaire' ? '/proprietaire' : '/reservations'" (click)="profil.open = false; fermer()">Mon espace {{utilisateur.role === 'proprietaire' ? 'propriétaire' : 'locataire'}}</a>
                @if (utilisateur.role === 'locataire') { <a routerLink="/favoris" (click)="profil.open = false; fermer()">Mes favoris</a> }
                <a routerLink="/profil" (click)="profil.open = false; fermer()">Mon profil</a>
                <button type="button" (click)="deconnecter(); profil.open = false">Déconnexion</button>
              </div>
            </details>
          } @else { <a routerLink="/connexion" (click)="fermer()">Se connecter</a> }
          <a appBouton routerLink="/proprietaire/ajouter" (click)="fermer()">Publier un bien <span aria-hidden="true">↗</span></a>
        </div>
      </nav>
    <p class="error" role="alert" [hidden]="!erreur">{{erreur}}</p></header>`
})
export class Navbar {
  auth = inject(AuthService);
  router = inject(Router);
  menuOuvert = false; erreur = '';
  fermer(): void { this.menuOuvert = false; this.erreur = ''; }
  async deconnecter(): Promise<void> { try { await this.auth.deconnecter(); this.fermer(); this.router.navigate(['/']); } catch (e) { this.erreur = messageErreur(e); } }
}
