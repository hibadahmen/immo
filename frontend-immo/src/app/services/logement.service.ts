import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Logement } from '../models/models';
import { API_URL } from '../config/api.config';
@Injectable({providedIn:'root'})
export class LogementService {
  private http = inject(HttpClient);
  logements: Logement[] = [];
  private normaliser(l: Logement): Logement {
    return {...l,titre:l.titre || 'Logement',description:l.description || '',type:l.type || '',ville:l.ville || '',adresse:l.adresse || '',images:l.images || [],equipements:l.equipements || [],disponibleDebut:l.disponibleDebut || '',disponibleFin:l.disponibleFin || ''};
  }
  async charger(criteres: Record<string,string | number> = {}): Promise<Logement[]> {
    this.logements = (await firstValueFrom(this.http.get<Logement[]>(`${API_URL}/logements`,{params:criteres}))).map(l => this.normaliser(l)); return this.logements;
  }
  async chargerMesBiens(): Promise<Logement[]> {
    this.logements = (await firstValueFrom(this.http.get<Logement[]>(`${API_URL}/logements/mes-biens`))).map(l => this.normaliser(l)); return this.logements;
  }
  async consulter(id: number): Promise<Logement> {
    const l = this.normaliser(await firstValueFrom(this.http.get<Logement>(`${API_URL}/logements/${id}`)));
    this.logements = [...this.logements.filter(item => item.id !== id),l]; return l;
  }
  trouver(id: number | null): Logement | undefined { return this.logements.find(l => l.id === id); }
  async enregistrer(logement: Logement, proprietaireId: number): Promise<void> {
    const corps = {...logement,proprietaireId};
    const requete = logement.id ? this.http.put<Logement>(`${API_URL}/logements/${logement.id}`,corps) : this.http.post<Logement>(`${API_URL}/logements`,corps);
    const l = this.normaliser(await firstValueFrom(requete)); this.logements = [...this.logements.filter(item => item.id !== l.id),l];
  }
  async archiver(id: number, archive: boolean): Promise<void> {
    const l = this.normaliser(await firstValueFrom(this.http.patch<Logement>(`${API_URL}/logements/${id}/archivage`,{archive})));
    this.logements = this.logements.map(item => item.id === id ? l : item);
  }
}
