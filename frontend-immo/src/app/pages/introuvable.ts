import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
@Component({ imports: [RouterLink], template: `<section class="container section empty"><p class="eyebrow">404</p><h1>Cette page est introuvable</h1><a class="button" routerLink="/">Retour à l'accueil</a></section>` })
export class Introuvable {}
