import { Component, inject, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { CarteLogement } from '../components/carte-logement';
import { CriteresLogements, FiltresLogements, criteresVides } from '../components/filtres-logements';
import { EtatRequete } from '../components/etat-requete';
import { messageErreur } from '../services/api-error';
import { LogementService } from '../services/logement.service';

@Component({
  imports: [FiltresLogements, CarteLogement, EtatRequete],
  template: `
    <section class="container section"><p class="eyebrow">FAITES PLACE À VOS ENVIES</p><h1>Votre prochain chez-vous</h1><p class="subtitle">Explorez nos logements disponibles à la location.</p>
      <app-filtres-logements [criteres]="saisie" (recherche)="appliquer($event)" />
      <app-etat-requete [chargement]="chargement" [erreur]="erreur" />
      @if (!chargement && !erreur) { <p class="result-count" role="status">{{resultats.length}} logement(s) disponible(s)</p>
      <div class="cards">@for (logement of resultats; track logement.id) { <app-carte-logement [logement]="logement" /> } @empty { <div class="empty"><h2>Aucun logement ne correspond</h2><p>Essayez une autre ville ou élargissez votre budget.</p></div> }</div> }
    </section>`
})
export class Logements implements OnInit {
  biens = inject(LogementService);
  route = inject(ActivatedRoute);
  chargement = false; erreur = '';
  saisie = criteresVides();
  filtres = criteresVides();
  private parametres = this.route.queryParamMap.pipe(takeUntilDestroyed());
  ngOnInit(): void {
    this.parametres.subscribe(p => {
      const budget = p.get('max');
      const max = budget !== null && budget.trim() !== '' && Number.isFinite(Number(budget)) && Number(budget) >= 0 ? Number(budget) : null;
      this.saisie = {...criteresVides(), ville: p.get('ville') || '', type: p.get('type') || '', max};
      this.appliquer(this.saisie);
    });
  }
  async appliquer(criteres: CriteresLogements): Promise<void> {
    this.filtres = {...criteres}; this.chargement = true; this.erreur = '';
    const params: Record<string,string | number> = {};
    for (const [cle, valeur] of Object.entries(criteres)) if (valeur !== null && valeur !== '') params[cle] = valeur;
    try { await this.biens.charger(params); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; }
  }
  get resultats() {
    const f = this.filtres;
    return this.biens.logements.filter(l => !l.archive && l.ville.toLowerCase().includes(f.ville.toLowerCase()) && (f.min === null || l.prix >= f.min) && (f.max === null || l.prix <= f.max) && (!f.type || l.type === f.type) && (f.pieces === null || l.pieces === f.pieces));
  }
}
