import { Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';
import { AuthService } from '../services/auth.service';
import { LogementService } from '../services/logement.service';
import { ReservationService } from '../services/reservation.service';
import { ActivatedRoute } from '@angular/router';
import { EtatRequete } from '../components/etat-requete';
import { messageErreur } from '../services/api-error';
import { Bouton } from '../components/bouton';

@Component({
  imports: [RouterLink, DecimalPipe, Bouton, EtatRequete],
  template: `
    <section class="container section">
      <p class="eyebrow">ESPACE PROPRIÉTAIRE</p>
      <div class="section-heading"><div><h1>Bonjour, {{auth.utilisateur?.prenom}}.</h1><p class="subtitle">Vos biens et vos projets, en un coup d'œil.</p></div><a appBouton routerLink="/proprietaire/ajouter">＋ Ajouter un bien</a></div>
      <div class="stats"><div><span>Mes biens</span><strong>{{mesBiens.length}}</strong></div><div><span>Annonces actives</span><strong>{{actives}}</strong></div><div><span>Demandes en attente</span><strong>{{attente}}</strong></div></div>
      @if (succes) { <p class="success" role="status">{{succes}}</p> }
      <app-etat-requete [chargement]="chargement" [erreur]="erreur" />@if (!chargement && !erreur) { @if (mesBiens.length) {
        <div class="table-scroll" tabindex="0" role="region" aria-label="Tableau des propriétés, défilement horizontal disponible">
          <table><caption>Mes propriétés</caption><thead><tr><th scope="col">Logement</th><th scope="col">Loyer mensuel</th><th scope="col">Statut</th><th scope="col">Actions</th></tr></thead>
            <tbody>@for (l of mesBiens; track l.id) {
              <tr><td><div class="table-property"><img [src]="l.images[0]" [alt]="l.titre" loading="lazy"><div><h3>{{l.titre}}</h3><p>{{l.ville}} · {{l.pieces}} pièces · {{l.superficie}} m²</p></div></div></td>
                <td>{{l.prix | number:'1.0-0'}} DT</td><td><span class="badge" [class.muted]="l.archive" [class.active-badge]="!l.archive">{{l.archive ? 'Archivée' : 'Active'}}</span></td>
                <td><div class="actions"><a class="button secondary small" [routerLink]="['/proprietaire/modifier', l.id]" [attr.aria-label]="'Modifier ' + l.titre">Modifier</a><button class="button secondary small" [disabled]="envoi" (click)="archiver(l.id)" [attr.aria-label]="(l.archive ? 'Réactiver ' : 'Archiver ') + l.titre">{{l.archive ? 'Réactiver' : 'Archiver'}}</button></div></td>
              </tr>
            }</tbody>
          </table>
        </div>
      } @else { <div class="empty"><h3>Votre première annonce vous attend</h3><p>Ajoutez un bien pour commencer.</p><a appBouton routerLink="/proprietaire/ajouter">Publier mon premier bien</a></div> } }
    </section>`
})
export class Proprietaire implements OnInit {
  auth = inject(AuthService); biens = inject(LogementService); demandes = inject(ReservationService);
  route = inject(ActivatedRoute); chargement = true; envoi = false; erreur = '';
  succes = this.route.snapshot.queryParamMap.get('enregistre') ? 'Le bien a été enregistré.' : '';
  async ngOnInit(): Promise<void> { try { await Promise.all([this.biens.chargerMesBiens(), this.demandes.charger()]); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } }
  get mesBiens() { return this.biens.logements.filter(l => l.proprietaireId === this.auth.utilisateur?.id); }
  get actives() { return this.mesBiens.filter(l => !l.archive).length; }
  get attente() { return this.demandes.reservations.filter(r => r.statut === 'En attente' && this.mesBiens.some(l => l.id === r.logementId)).length; }
  async archiver(id: number): Promise<void> {
    if (!this.auth.utilisateur) return;
    if (this.envoi) return; this.envoi = true; this.erreur = '';
    try { await this.biens.archiver(id, !this.biens.trouver(id)?.archive); this.succes = this.biens.trouver(id)?.archive ? 'Annonce archivée.' : 'Annonce réactivée.'; }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }
}
