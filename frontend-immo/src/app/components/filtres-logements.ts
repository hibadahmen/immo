import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { Bouton } from './bouton';

export interface CriteresLogements {
  ville: string; type: string; min: number | null; max: number | null; pieces: number | null;
}
export const criteresVides = (): CriteresLogements => ({ville: '', type: '', min: null, max: null, pieces: null});

@Component({
  selector: 'app-filtres-logements',
  imports: [FormsModule, Bouton],
  template: `
    <form [class]="compact ? 'search-bar' : 'filters'" #form="ngForm" (ngSubmit)="appliquer(form)" novalidate>
      <label><span>Ville</span><input name="ville" [(ngModel)]="criteres.ville" placeholder="Où souhaitez-vous vivre ?"></label>
      <label><span>Type de logement</span><select name="type" [(ngModel)]="criteres.type"><option value="">Tous les types</option><option>Appartement</option><option>Maison</option><option>Studio</option><option>Villa</option></select></label>
      @if (!compact) { <label><span>Budget minimum (DT)</span><input type="number" name="min" min="0" [(ngModel)]="criteres.min" placeholder="Sans minimum"></label> }
      <label><span>Budget maximum (DT)</span><input type="number" name="max" min="0" [(ngModel)]="criteres.max" placeholder="Sans maximum"></label>
      @if (!compact) { <label><span>Nombre de pièces</span><select name="pieces" [(ngModel)]="criteres.pieces"><option [ngValue]="null">Toutes</option>@for (n of [1,2,3,4,5,6]; track n) { <option [ngValue]="n">{{n}}</option> }</select></label> }
      <button appBouton type="submit"><span aria-hidden="true">⌕</span> {{compact ? 'Rechercher' : 'Filtrer'}}</button>
      @if (!compact) { <button appBouton [secondaire]="true" type="button" (click)="reinitialiser(form)">Réinitialiser</button> }
      @if (erreur) { <p class="error filter-error" role="alert">{{erreur}}</p> }
    </form>`
})
export class FiltresLogements {
  @Input() compact = false;
  @Input() criteres: CriteresLogements = criteresVides();
  @Output() recherche = new EventEmitter<CriteresLogements>();
  erreur = '';
  appliquer(form: NgForm): void {
    this.erreur = '';
    if (form.invalid) { this.erreur = 'Les budgets doivent être des nombres positifs.'; return; }
    if (this.criteres.min !== null && this.criteres.max !== null && this.criteres.min > this.criteres.max) {
      this.erreur = 'Le budget minimum doit être inférieur au budget maximum.'; return;
    }
    this.recherche.emit({...this.criteres, ville: this.criteres.ville.trim()});
  }
  reinitialiser(form: NgForm): void {
    this.criteres = criteresVides(); this.erreur = ''; form.resetForm(this.criteres);
    this.recherche.emit({...this.criteres});
  }
}
