import { Component, Input, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { Logement } from '../models/models';
import { AuthService } from '../services/auth.service';
import { FavorisService } from '../services/favoris.service';
@Component({ selector: 'app-carte-logement', imports: [RouterLink, DecimalPipe], template: `
  <article class="property-card"><div class="card-image"><a [routerLink]="['/logements', logement.id]"><img [src]="logement.images[0] || '/images/logement-placeholder.svg'" [alt]="logement.titre" loading="lazy"></a><span class="tag">{{logement.type}}</span>
  @if (auth.utilisateur?.role !== 'proprietaire') { <button class="heart" [class.selected]="estFavori()" [attr.aria-label]="estFavori() ? 'Retirer des favoris' : 'Ajouter aux favoris'" [attr.aria-pressed]="estFavori()" [disabled]="favoris.envoi || favoris.chargement" (click)="favori()">{{estFavori() ? '♥' : '♡'}}</button> }</div>
  <div class="card-content"><p class="location">⌖ {{logement.ville}} · {{logement.adresse}}</p><h3><a [routerLink]="['/logements', logement.id]">{{logement.titre}}</a></h3><p class="features"><span>▦ {{logement.pieces}} pièces</span><span>↔ {{logement.superficie}} m²</span></p><div class="card-bottom"><p><strong>{{logement.prix | number:'1.0-0'}} DT</strong><span> / mois</span></p><a [routerLink]="['/logements', logement.id]" [attr.aria-label]="'Voir les détails : ' + logement.titre">Voir les détails ↗</a></div>@if (favoris.erreur) { <p class="error" role="alert">{{favoris.erreur}}</p> }</div></article>` })
export class CarteLogement {
  @Input({required: true}) logement!: Logement;
  auth = inject(AuthService); favoris = inject(FavorisService); router = inject(Router);
  estFavori(): boolean { return !!this.auth.utilisateur && this.favoris.contient(this.auth.utilisateur.id, this.logement.id); }
  favori(): void { if (!this.auth.utilisateur) { this.router.navigate(['/connexion']); return; } if (this.auth.utilisateur.role === 'locataire') this.favoris.basculer(this.auth.utilisateur.id, this.logement.id); }
}
