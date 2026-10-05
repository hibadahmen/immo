import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
@Component({ selector: 'app-footer', imports: [RouterLink], template: `
  <footer><div><a class="brand" routerLink="/">⌂ Darna.</a><p>Un lieu à vous. Une nouvelle histoire.<br>La location immobilière, simplement.</p></div>
  <nav aria-label="Navigation du pied de page"><a routerLink="/">Accueil</a><a routerLink="/logements">Trouver un logement</a><a routerLink="/" fragment="comment-ca-marche">Comment ça marche</a><a routerLink="/proprietaire/ajouter">Publier un bien</a></nav>
  <div class="footer-note">© 2026 Darna · Plateforme de location immobilière<br>Propriétaires et locataires, réunis.</div></footer>` })
export class Footer {}
