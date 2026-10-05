import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom, Subject } from 'rxjs';
import { Utilisateur } from '../models/models';
import { API_URL } from '../config/api.config';
import { messageErreur } from './api-error';
@Injectable({providedIn:'root'})
export class AuthService {
  private http = inject(HttpClient);
  utilisateur: Utilisateur | null = null;
  erreur = ''; changements = new Subject<void>();
  async initialiser(): Promise<void> {
    try {
      await firstValueFrom(this.http.get(`${API_URL}/auth/csrf`));
      this.utilisateur = await firstValueFrom(this.http.get<Utilisateur>(`${API_URL}/auth/moi`));
    } catch (e) { this.utilisateur = null; if (!(e instanceof HttpErrorResponse && e.status === 401)) this.erreur = messageErreur(e); }
  }
  async connecter(email: string, motDePasse: string): Promise<void> {
    await firstValueFrom(this.http.get(`${API_URL}/auth/csrf`));
    this.utilisateur = await firstValueFrom(this.http.post<Utilisateur>(`${API_URL}/auth/connexion`, {email:email.trim(),motDePasse}));
    this.erreur = ''; this.changements.next();
  }
  async inscrire(compte: Omit<Utilisateur,'id'>, motDePasse: string): Promise<void> {
    await firstValueFrom(this.http.get(`${API_URL}/auth/csrf`));
    this.utilisateur = await firstValueFrom(this.http.post<Utilisateur>(`${API_URL}/auth/inscription`, {...compte,motDePasse}));
    this.erreur = ''; this.changements.next();
  }
  async modifier(compte: Utilisateur): Promise<void> { this.utilisateur = await firstValueFrom(this.http.put<Utilisateur>(`${API_URL}/utilisateurs/moi`,compte)); }
  async deconnecter(): Promise<void> { await firstValueFrom(this.http.post(`${API_URL}/auth/deconnexion`,{})); this.utilisateur = null; this.changements.next(); }
}
