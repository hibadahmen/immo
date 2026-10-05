import { Component, inject, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule, NgForm } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { messageErreur } from '../services/api-error';
import { Logement } from '../models/models';
import { LogementService } from '../services/logement.service';
import { ReservationService } from '../services/reservation.service';
@Component({ imports: [FormsModule, RouterLink, DatePipe], template: `
  <section class="container section narrow"><p class="eyebrow">ESPACE LOCATAIRE</p><h1>Préparez votre prochaine arrivée</h1>
  @if (chargement) { <p class="notice" role="status">Chargement du logement…</p> } @if (logement; as l) { <div class="panel"><h2>{{l.titre}}</h2><p>{{l.ville}} · {{l.prix}} DT / mois</p><p>Disponible du {{l.disponibleDebut | date:'dd/MM/yyyy'}} au {{l.disponibleFin | date:'dd/MM/yyyy'}}</p><form #form="ngForm" (ngSubmit)="envoyer(form)" novalidate><div class="form-grid"><label>Date de début<input type="date" name="debut" [(ngModel)]="debut" [min]="l.disponibleDebut" [max]="l.disponibleFin" required></label><label>Date de fin<input type="date" name="fin" [(ngModel)]="fin" [min]="debut || l.disponibleDebut" [max]="l.disponibleFin" required></label></div><label>Message au propriétaire<textarea name="message" [(ngModel)]="message" rows="4" maxlength="1500" placeholder="Présentez votre projet de location…"></textarea></label>@if (form.submitted && form.invalid) { <p class="error" role="alert">Renseignez les deux dates.</p> } @if (erreur) { <p class="error" role="alert">{{erreur}}</p> }<div class="actions"><button class="button" type="submit" [disabled]="envoi">Envoyer ma demande ↗</button><a class="button secondary" [routerLink]="['/logements',l.id]">Annuler</a></div></form><p class="notice">La demande sera ajoutée avec le statut « En attente ».</p></div> } @else if (!chargement) { <div class="empty"><p>{{erreur || 'Ce logement n’est plus disponible.'}}</p><a routerLink="/logements">Voir les logements</a></div> }</section>` })
export class Reserver implements OnInit {
  route = inject(ActivatedRoute); router = inject(Router); biens = inject(LogementService); demandes = inject(ReservationService);
  logement?: Logement; debut = ''; fin = ''; message = ''; erreur = '';
  chargement = true; envoi = false;
  async ngOnInit(): Promise<void> { try { const l = await this.biens.consulter(Number(this.route.snapshot.paramMap.get('id'))); this.logement = !l.archive ? l : undefined; } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } }
  async envoyer(form: NgForm): Promise<void> {
    if (form.invalid || !this.logement || this.envoi) return;
    if (this.fin <= this.debut) { this.erreur = 'La fin doit être postérieure au début.'; return; }
    this.envoi = true; this.erreur = '';
    try { await this.demandes.demander(this.logement.id, this.debut, this.fin, this.message); this.router.navigate(['/reservations'], {queryParams:{envoyee:'1'}}); }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }
}
