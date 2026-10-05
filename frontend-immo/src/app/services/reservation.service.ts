import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Reservation } from '../models/models';
import { API_URL } from '../config/api.config';
@Injectable({providedIn:'root'})
export class ReservationService {
  private http = inject(HttpClient);
  reservations: Reservation[] = [];
  async charger(): Promise<void> { this.reservations = await firstValueFrom(this.http.get<Reservation[]>(`${API_URL}/demandes`)); }
  async demander(logementId: number, debut: string, fin: string, message: string): Promise<void> { const r = await firstValueFrom(this.http.post<Reservation>(`${API_URL}/demandes`,{logementId,debut,fin,message})); this.reservations.push(r); }
  async decider(id: number, accepter: boolean): Promise<void> { const r = await firstValueFrom(this.http.put<Reservation>(`${API_URL}/demandes/${id}/${accepter ? 'accepter' : 'refuser'}`,{})); this.reservations = this.reservations.map(item => item.id === id ? r : item); }
  async annuler(id: number): Promise<void> { const r = await firstValueFrom(this.http.put<Reservation>(`${API_URL}/demandes/${id}/annuler`,{})); this.reservations = this.reservations.map(item => item.id === id ? r : item); }
}
