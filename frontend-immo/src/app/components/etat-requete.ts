import { Component, Input } from '@angular/core';
@Component({selector:'app-etat-requete', template:`
  @if (chargement) { <p class="notice" role="status">Chargement…</p> }
  @if (erreur) { <p class="error" role="alert">{{erreur}}</p> }
`})
export class EtatRequete { @Input() chargement = false; @Input() erreur = ''; }
