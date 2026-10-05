import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { API_URL } from '../config/api.config';
import { AuthService } from './auth.service';
import { messageErreur } from './api-error';
@Injectable({providedIn:'root'})
export class FavorisService {
  private http = inject(HttpClient); private auth = inject(AuthService);
  ids: number[] = []; chargement = false; envoi = false; erreur = '';
  constructor() {
    this.auth.changements.subscribe(() => { this.ids = []; this.erreur = ''; if (this.auth.utilisateur?.role === 'locataire') this.charger(); });
    if (this.auth.utilisateur?.role === 'locataire') this.charger();
  }
  contient(utilisateurId: number, logementId: number): boolean { return this.auth.utilisateur?.id === utilisateurId && this.ids.includes(logementId); }
  async charger(): Promise<void> {
    this.chargement = true; this.erreur = '';
    try { this.ids = await firstValueFrom(this.http.get<number[]>(`${API_URL}/favoris`)); }
    catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; }
  }
  async basculer(utilisateurId: number, logementId: number): Promise<void> {
    if (this.auth.utilisateur?.id !== utilisateurId || this.envoi) return;
    this.erreur = ''; this.envoi = true;
    try { const requete = this.ids.includes(logementId) ? this.http.delete<number[]>(`${API_URL}/favoris/${logementId}`) : this.http.put<number[]>(`${API_URL}/favoris/${logementId}`,{}); this.ids = await firstValueFrom(requete); }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }
}
