import { Component, inject, OnInit } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { messageErreur } from '../services/api-error';
import { Logement } from '../models/models';
import { AuthService } from '../services/auth.service';
import { LogementService } from '../services/logement.service';
@Component({ imports: [FormsModule, RouterLink], template: `
  <section class="container section narrow"><a class="text-link" routerLink="/proprietaire">← Mes propriétés</a><p class="eyebrow detail-eyebrow">ESPACE PROPRIÉTAIRE</p><h1>{{edition ? 'Modifier votre bien' : 'Une nouvelle adresse à partager'}}</h1>
  @if (chargement) { <p class="notice" role="status">Chargement du bien…</p> } @else if (introuvable) { <div class="empty">{{erreur || 'Ce bien n’existe pas ou ne vous appartient pas.'}}</div> } @else {
  <form class="panel" #form="ngForm" (ngSubmit)="enregistrer(form)" novalidate><fieldset><legend>1. Présentez votre logement</legend><label>Titre<input name="titre" [(ngModel)]="logement.titre" required maxlength="120"></label><label>Description<textarea name="description" [(ngModel)]="logement.description" required rows="4"></textarea></label>
  <div class="form-grid"><label>Type<select name="type" [(ngModel)]="logement.type" required><option>Appartement</option><option>Maison</option><option>Studio</option><option>Villa</option></select></label><label>Ville<input name="ville" [(ngModel)]="logement.ville" required></label></div><label>Adresse<input name="adresse" [(ngModel)]="logement.adresse" required></label></fieldset><fieldset><legend>2. Loyer et caractéristiques</legend>
  <div class="form-grid"><label>Prix (DT / mois)<input type="number" name="prix" [(ngModel)]="logement.prix" min="1" required></label><label>Superficie (m²)<input type="number" name="superficie" [(ngModel)]="logement.superficie" min="1" required></label><label>Nombre de pièces<input type="number" name="pieces" [(ngModel)]="logement.pieces" min="1" step="1" pattern="[0-9]+" required></label><label>Équipements, séparés par des virgules<input name="equipements" [(ngModel)]="equipements" placeholder="Wi-Fi, Parking, Terrasse"></label></div>
  </fieldset><fieldset><legend>3. Photo du logement</legend><label>URL ou chemin de l'image principale<input name="image" [(ngModel)]="image" (ngModelChange)="photoChargee = false; photoErreur = false" required placeholder="https://… ou /images/logement.jpg"></label><small>Utilisez une adresse HTTPS ou un fichier présent dans le dossier public.</small>
  @if (image.trim()) { <img class="photo-preview" [src]="image" alt="Aperçu de la photo principale du logement" (load)="photoChargee = true" (error)="photoErreur = true" [hidden]="photoErreur">@if (photoErreur) { <p class="error" role="alert">Impossible de charger cette photo. Vérifiez son adresse.</p> } @else if (!photoChargee) { <p class="notice" role="status">Chargement de l'aperçu…</p> } }
  </fieldset><fieldset><legend>4. Dates de disponibilité</legend>
  <div class="form-grid"><label>Disponible à partir du<input type="date" name="debut" [(ngModel)]="logement.disponibleDebut" required></label><label>Disponible jusqu'au<input type="date" name="fin" [(ngModel)]="logement.disponibleFin" [min]="logement.disponibleDebut" required></label></div>
  </fieldset>@if (form.submitted && form.invalid) { <p class="error" role="alert">Complétez les champs obligatoires avec des valeurs valides et positives.</p> } @if (erreur) { <p class="error" role="alert">{{erreur}}</p> }
  <div class="actions"><button class="button" type="submit" [disabled]="envoi">{{edition ? 'Enregistrer' : 'Publier le bien'}} ↗</button><a class="button secondary" routerLink="/proprietaire">Annuler</a></div></form> }</section>` })
export class FormulairePropriete implements OnInit {
  auth = inject(AuthService); biens = inject(LogementService); route = inject(ActivatedRoute); router = inject(Router);
  edition = false; introuvable = false; erreur = ''; image = ''; equipements = '';
  photoChargee = false; photoErreur = false; chargement = false; envoi = false;
  logement: Logement = { id: 0, proprietaireId: 0, titre: '', description: '', type: 'Appartement', ville: '', adresse: '', prix: 0, superficie: 0, pieces: 1, equipements: [], images: [], disponibleDebut: '', disponibleFin: '', archive: false };
  async ngOnInit(): Promise<void> {
    const id = this.route.snapshot.paramMap.get('id'); this.edition = id !== null;
    if (id) { this.chargement = true; try { const l = await this.biens.consulter(Number(id)); if (l.proprietaireId !== this.auth.utilisateur?.id) { this.introuvable = true; return; } this.logement = {...l,images:[...l.images],equipements:[...l.equipements]}; this.image = l.images[0] || ''; this.equipements = l.equipements.join(', '); } catch (e) { this.introuvable = true; this.erreur = messageErreur(e); } finally { this.chargement = false; } }
  }
  async enregistrer(form: NgForm): Promise<void> {
    this.erreur = ''; if (form.invalid || !this.auth.utilisateur) return;
    if ([this.logement.titre, this.logement.description, this.logement.ville, this.logement.adresse, this.image].some(v => !v.trim())) { this.erreur = 'Les champs ne peuvent pas contenir seulement des espaces.'; return; }
    if (!Number.isInteger(this.logement.pieces)) { this.erreur = 'Le nombre de pièces doit être entier.'; return; }
    if (this.logement.disponibleFin <= this.logement.disponibleDebut) { this.erreur = 'La fin de disponibilité doit être postérieure au début.'; return; }
    if (!/^(https?:\/\/|\/|[a-zA-Z0-9_-])/.test(this.image.trim()) || /^(javascript|data):/i.test(this.image.trim())) { this.erreur = "Utilisez une URL HTTP(S) ou un chemin d'image."; return; }
    this.logement.images = [this.image.trim(), ...this.logement.images.slice(1)]; this.logement.equipements = this.equipements.split(',').map(e => e.trim()).filter(Boolean);
    if (this.envoi) return; this.envoi = true;
    try { await this.biens.enregistrer(this.logement, this.auth.utilisateur.id); this.router.navigate(['/proprietaire'], {queryParams:{enregistre:'1'}}); }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }
}
