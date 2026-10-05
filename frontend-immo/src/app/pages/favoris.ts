import { Component, inject, OnInit } from '@angular/core';
import { EtatRequete } from '../components/etat-requete';
import { messageErreur } from '../services/api-error';
import { RouterLink } from '@angular/router';
import { CarteLogement } from '../components/carte-logement';
import { AuthService } from '../services/auth.service';
import { LogementService } from '../services/logement.service';
import { FavorisService } from '../services/favoris.service';
@Component({ imports: [RouterLink, CarteLogement, EtatRequete], template: `<section class="container section"><p class="eyebrow">ESPACE LOCATAIRE</p><h1>Mes coups de cœur</h1><p class="subtitle">Les adresses que vous avez envie de retrouver.</p><app-etat-requete [chargement]="chargement || favoris.chargement" [erreur]="erreur || favoris.erreur" />@if (!chargement && !favoris.chargement && !erreur && !favoris.erreur) { <div class="cards">@for (l of liste; track l.id) { <app-carte-logement [logement]="l" /> } @empty { <div class="empty"><h2>Votre sélection commence ici</h2><p>Appuyez sur le cœur d'une annonce pour la retrouver dans vos favoris.</p><a class="button" routerLink="/logements">Explorer les logements ↗</a></div> }</div> }</section>` })
export class Favoris implements OnInit { chargement = true; erreur = ''; async ngOnInit(): Promise<void> { try { await Promise.all([this.biens.charger(), this.favoris.charger()]); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } } auth = inject(AuthService); biens = inject(LogementService); favoris = inject(FavorisService); get liste() { return this.biens.logements.filter(l => !l.archive && !!this.auth.utilisateur && this.favoris.contient(this.auth.utilisateur.id, l.id)); } }
