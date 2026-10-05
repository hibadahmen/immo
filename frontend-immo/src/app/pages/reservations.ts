import { Component, inject, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { EtatRequete } from '../components/etat-requete';
import { messageErreur } from '../services/api-error';
import { AuthService } from '../services/auth.service';
import { LogementService } from '../services/logement.service';
import { ReservationService } from '../services/reservation.service';

@Component({
  imports: [RouterLink, DatePipe, EtatRequete],
  template: `
    <section class="container section">
      <p class="eyebrow">{{proprietaire ? 'ESPACE PROPRIÉTAIRE' : 'ESPACE LOCATAIRE'}}</p>
      <h1>{{proprietaire ? 'Demandes reçues' : 'Mes réservations'}}</h1>
      <p class="subtitle">{{proprietaire ? 'Accompagnez les futurs locataires dans leur projet.' : 'Suivez vos demandes et préparez votre prochain chapitre.'}}</p>
      <div class="stats"><div><span>Total des demandes</span><strong>{{liste.length}}</strong></div><div><span>En attente</span><strong>{{attente}}</strong></div><div><span>Acceptées</span><strong>{{acceptees}}</strong></div></div>
      @if (succes) { <p class="success" role="status">{{succes}}</p> }
      @if (erreur) { <p class="error" role="alert">{{erreur}}</p> }
      <app-etat-requete [chargement]="chargement" />@if (!chargement && !erreur) { @if (liste.length) {
        <div class="table-scroll" tabindex="0" role="region" aria-label="Tableau des réservations, défilement horizontal disponible">
          <table><caption>{{proprietaire ? 'Les demandes pour vos logements' : 'Vos projets de location'}}</caption><thead><tr><th scope="col">Logement {{proprietaire ? 'et locataire' : 'et message'}}</th><th scope="col">Période</th><th scope="col">Statut</th><th scope="col">Actions</th></tr></thead>
            <tbody>@for (r of liste; track r.id) {
              <tr><td><h3>{{biens.trouver(r.logementId)?.titre || 'Logement indisponible'}}</h3>
                @if (proprietaire) { <p>{{r.locataireNom}}</p> }
                <span class="table-message">{{r.message || 'Aucun message.'}}</span>
              </td><td class="date-cell">Du {{r.debut | date:'dd/MM/yyyy'}}<br>au {{r.fin | date:'dd/MM/yyyy'}}</td>
                <td><span class="badge" [class.accepted]="r.statut === 'Acceptée'" [class.refused]="r.statut === 'Refusée'" [class.cancelled]="r.statut === 'Annulée'">{{r.statut}}</span></td>
                <td>@if (r.statut === 'En attente') {
                  <div class="actions">@if (proprietaire) {
                    <button class="button small" [disabled]="envoi" (click)="decider(r.id, true)" [attr.aria-label]="'Accepter la demande de ' + r.locataireNom">Accepter</button>
                    <button class="button secondary small" [disabled]="envoi" (click)="decider(r.id, false)" [attr.aria-label]="'Refuser la demande de ' + r.locataireNom">Refuser</button>
                  } @else { <button class="button secondary small" [disabled]="envoi" (click)="annuler(r.id)">Annuler la demande</button> }</div>
                } @else { <small>Demande traitée</small> }</td>
              </tr>
            }</tbody>
          </table>
        </div>
      } @else { <div class="empty"><h2>Aucune demande pour le moment</h2>@if (!proprietaire) { <a class="button" routerLink="/logements">Découvrir les logements</a> }</div> } }
    </section>`
})
export class Reservations implements OnInit {
  auth = inject(AuthService); biens = inject(LogementService); demandes = inject(ReservationService); route = inject(ActivatedRoute);
  proprietaire = !!this.route.snapshot.data['proprietaire'];
  succes = this.route.snapshot.queryParamMap.get('envoyee') === '1' ? 'Votre demande a été envoyée au propriétaire.' : '';
  erreur = ''; chargement = true; envoi = false;
  async ngOnInit(): Promise<void> { try { await Promise.all([this.proprietaire ? this.biens.chargerMesBiens() : this.biens.charger(), this.demandes.charger()]); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } }
  get liste() { return this.demandes.reservations.filter(r => this.proprietaire ? this.biens.trouver(r.logementId)?.proprietaireId === this.auth.utilisateur?.id : r.locataireId === this.auth.utilisateur?.id).slice().reverse(); }
  get attente() { return this.liste.filter(r => r.statut === 'En attente').length; }
  get acceptees() { return this.liste.filter(r => r.statut === 'Acceptée').length; }
  async decider(id: number, accepter: boolean): Promise<void> {
    if (this.envoi) return; this.envoi = true; this.erreur = ''; this.succes = '';
    try { await this.demandes.decider(id, accepter); this.succes = accepter ? 'La demande a été acceptée.' : 'La demande a été refusée.'; }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }
  async annuler(id: number): Promise<void> {
    if (this.envoi) return; this.envoi = true; this.erreur = ''; this.succes = '';
    try { await this.demandes.annuler(id); this.succes = 'Votre demande a été annulée.'; }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }
}
