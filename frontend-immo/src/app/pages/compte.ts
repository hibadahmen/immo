import { Component, inject, OnInit } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { messageErreur } from '../services/api-error';
import { Utilisateur } from '../models/models';
@Component({ imports: [FormsModule, RouterLink], template: `
  <section class="container section auth-layout"><div class="auth-intro"><p class="eyebrow">BIENVENUE CHEZ DARNA</p><h1>{{mode === 'profil' ? 'Votre espace, vos informations.' : 'Votre nouvelle histoire commence ici.'}}</h1><p>Retrouvez vos logements préférés et gérez vos projets de location simplement.</p><img src="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=900&q=85" alt="Intérieur accueillant"></div>
  <div class="panel"><h2>{{mode === 'connexion' ? 'Heureux de vous retrouver' : mode === 'inscription' ? 'Créer mon compte' : 'Mon profil'}}</h2>
  <p class="notice">Votre compte est enregistré sur le serveur. La connexion utilise une session ; aucun mot de passe ne reste dans le navigateur.</p>
  @if (erreur) { <p class="error" role="alert">{{erreur}}</p> } @if (succes) { <p class="success" role="status">{{succes}}</p> }
  <form #form="ngForm" (ngSubmit)="envoyer(form)" novalidate>
  @if (mode !== 'connexion') { <div class="form-grid"><label>Prénom<input name="prenom" [(ngModel)]="compte.prenom" required maxlength="60"></label><label>Nom<input name="nom" [(ngModel)]="compte.nom" required maxlength="60"></label></div> }
  <label>Email<input type="email" name="email" [(ngModel)]="compte.email" required email autocomplete="email"></label>
  @if (mode !== 'connexion') { <label>Téléphone<input type="tel" name="telephone" [(ngModel)]="compte.telephone" required pattern="[+0-9 ()-]{8,20}" autocomplete="tel"></label> }
  @if (mode !== 'profil') { <label>Mot de passe<input type="password" name="motDePasse" [(ngModel)]="motDePasse" required [minlength]="mode === 'inscription' ? 6 : 1" autocomplete="off"></label> }
  @if (mode === 'inscription') { <label>Je suis<select name="role" [(ngModel)]="compte.role" required><option value="locataire">Locataire</option><option value="proprietaire">Propriétaire</option></select></label> }
  @if (form.submitted && form.invalid) { <p class="error" role="alert">Vérifiez les champs : email valide, téléphone de 8 à 20 caractères et, à l'inscription, mot de passe de 6 caractères minimum.</p> }
  <button class="button full" type="submit" [disabled]="envoi">{{mode === 'connexion' ? 'Se connecter' : mode === 'inscription' ? "S'inscrire" : 'Enregistrer les modifications'}} ↗</button>@if (envoi) { <p class="notice" role="status">Enregistrement en cours…</p> }</form>
  @if (mode === 'connexion') { <p>Pas encore de compte ? <a class="text-link" routerLink="/inscription">S'inscrire</a></p> }
  @if (mode === 'inscription') { <p>Déjà un compte ? <a class="text-link" routerLink="/connexion">Se connecter</a></p> }
  @if (mode === 'profil') { <p class="notice">Rôle : {{compte.role === 'proprietaire' ? 'Propriétaire' : 'Locataire'}}. La modification du mot de passe nécessite un parcours dédié et reste indisponible.</p> }
  </div></section>` })
export class Compte implements OnInit {
  auth = inject(AuthService); route = inject(ActivatedRoute); router = inject(Router);
  envoi = false; mode = 'connexion'; erreur = ''; succes = ''; motDePasse = '';
  compte: Utilisateur = { id: 0, nom: '', prenom: '', email: '', telephone: '', role: 'locataire' };
  ngOnInit(): void { this.mode = this.route.snapshot.data['mode']; if (this.mode === 'profil' && this.auth.utilisateur) this.compte = { ...this.auth.utilisateur }; }
  async envoyer(form: NgForm): Promise<void> {
    this.erreur = this.succes = ''; if (form.invalid) return;
    if (this.mode !== 'connexion' && (!this.compte.nom.trim() || !this.compte.prenom.trim())) { this.erreur = 'Le nom et le prénom ne peuvent pas être vides.'; return; }
    if (this.envoi) return; this.envoi = true;
    try {
    if (this.mode === 'profil') { await this.auth.modifier(this.compte); this.succes = 'Votre profil a été enregistré.'; return; }
    if (this.mode === 'connexion') await this.auth.connecter(this.compte.email, this.motDePasse);
    else await this.auth.inscrire(this.compte, this.motDePasse);
    this.motDePasse = '';
    const retour = this.route.snapshot.queryParamMap.get('retour');
    if (retour?.startsWith('/') && !retour.startsWith('//')) this.router.navigateByUrl(retour);
    else this.router.navigate([this.auth.utilisateur?.role === 'proprietaire' ? '/proprietaire' : '/reservations']);
    } catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; this.motDePasse = ''; }
  }
}
