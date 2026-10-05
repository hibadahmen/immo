import { Directive, Input } from '@angular/core';

// S'utilise sur un vrai bouton ou lien pour conserver le comportement du clavier.
@Directive({ selector: '[appBouton]', host: { class: 'button', '[class.secondary]': 'secondaire' } })
export class Bouton { @Input() secondaire = false; }
