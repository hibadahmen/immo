import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from '../config/api.config';
export interface Statistiques { logements: number; proprietaires: number; villes: number; reservations: number; }

// Statistiques calculées par Spring Boot, sans données fictives dans les pages.
@Injectable({providedIn: 'root'})
export class BackendService {
  private http = inject(HttpClient);
  statistiques() { return this.http.get<Statistiques>(`${API_URL}/statistiques`); }
}
