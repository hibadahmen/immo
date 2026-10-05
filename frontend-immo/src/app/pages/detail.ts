import { Component, inject, OnInit } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { EtatRequete } from '../components/etat-requete';
import { messageErreur } from '../services/api-error';
import { Logement } from '../models/models';
import { LogementService } from '../services/logement.service';
@Component({ imports: [RouterLink, DecimalPipe, DatePipe, EtatRequete], template: `
  <section class="container section"><a class="text-link" routerLink="/logements">← Tous les logements</a>
  <app-etat-requete [chargement]="chargement" [erreur]="erreur" />@if (logement; as l) { <p class="eyebrow detail-eyebrow">{{l.type}} · {{l.ville}}</p><h1>{{l.titre}}</h1><p class="subtitle">⌖ {{l.adresse}}, {{l.ville}}</p><div class="gallery">@for (photo of l.images; track $index) { <img [src]="photo" [alt]="l.titre + ' — photo ' + ($index + 1)"> }</div>
  <div class="detail-grid"><div><div class="detail-facts"><span>{{l.superficie}} m²</span><span>{{l.pieces}} pièces</span><span>{{l.type}}</span></div><h2>Un endroit où se sentir bien</h2><p class="description">{{l.description}}</p><h2>Les petits plus</h2><div class="chips">@for (e of l.equipements; track $index) { <span>✓ {{e}}</span> }</div></div><aside class="panel"><p><strong class="price">{{l.prix | number:'1.0-0'}} DT</strong> / mois</p><p>Disponible du {{l.disponibleDebut | date:'dd/MM/yyyy'}} au {{l.disponibleFin | date:'dd/MM/yyyy'}}</p>@if (l.disponibleDebut && l.disponibleFin) { <a class="button full" [routerLink]="['/reserver', l.id]">Demander une réservation ↗</a> } @else { <p class="notice">Le propriétaire doit renseigner les disponibilités avant toute réservation.</p> }<small>Votre demande sera examinée par le propriétaire.</small></aside></div>
  } @else if (!chargement && !erreur) { <div class="empty"><h1>Logement introuvable</h1><p>Cette annonce n'existe pas ou a été archivée.</p></div> }</section>` })
export class Detail implements OnInit {
  route = inject(ActivatedRoute); biens = inject(LogementService); logement?: Logement; chargement = true; erreur = '';
  ngOnInit(): void { this.route.paramMap.subscribe(async p => {
    this.chargement = true; this.erreur = ''; this.logement = undefined;
    try { this.logement = await this.biens.consulter(Number(p.get('id'))); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; }
  }); }
}
