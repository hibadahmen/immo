import { Component, inject, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CarteLogement } from '../components/carte-logement';
import { CriteresLogements, FiltresLogements } from '../components/filtres-logements';
import { Bouton } from '../components/bouton';
import { LogementService } from '../services/logement.service';
import { AuthService } from '../services/auth.service';
import { BackendService } from '../services/backend.service';
import { firstValueFrom } from 'rxjs';
import { messageErreur } from '../services/api-error';
import { EtatRequete } from '../components/etat-requete';

@Component({
  imports: [RouterLink, CarteLogement, FiltresLogements, Bouton, EtatRequete],
  templateUrl: './accueil.html'
})
export class Accueil implements OnInit {
  chargement = true; erreur = ''; statistiques: {valeur:number; libelle:string}[] = [];
  biens = inject(LogementService);
  auth = inject(AuthService);
  backend = inject(BackendService);
  router = inject(Router);
  categories = [
    {titre: 'Appartements', type: 'Appartement', image: 'photo-1600210492486-724fe5c67fb0'},
    {titre: 'Maisons', type: 'Maison', image: 'photo-1600607687920-4e2a09cf159d'},
    {titre: 'Studios', type: 'Studio', image: 'photo-1522708323590-d24dbb6b0267'},
    {titre: 'Villas', type: 'Villa', image: 'photo-1600607687939-ce8a6c25118c'}
  ];
  get annonces() { return this.biens.logements.filter(l => !l.archive); }
  get recents() { return this.annonces.slice(-3).reverse(); }
  async ngOnInit(): Promise<void> {
    try { await this.biens.charger(); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; }
    try {
      const s = await firstValueFrom(this.backend.statistiques());
      this.statistiques = [{valeur:s.logements,libelle:'Logements publiés'},{valeur:s.proprietaires,libelle:'Propriétaires inscrits'},{valeur:s.villes,libelle:'Villes couvertes'},{valeur:s.reservations,libelle:'Réservations acceptées'}];
    } catch { this.statistiques = []; }
  }
  chercher(criteres: CriteresLogements): void {
    this.router.navigate(['/logements'], {queryParams: {ville: criteres.ville || null, type: criteres.type || null, max: criteres.max}});
  }
}
