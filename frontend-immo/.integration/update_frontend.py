from pathlib import Path
base = Path('src/app')
def edit(path, changes):
    p = base / path
    s = p.read_text(encoding='utf-8')
    for old, new in changes:
        if old not in s: raise Exception(f'Motif absent : {path} : {old[:70]}')
        s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')

edit('components/navbar.ts', [
    ("import { Bouton }", "import { messageErreur } from '../services/api-error';\nimport { Bouton }"),
    ('</header>`', '<p class="error" role="alert" [hidden]="!erreur">{{erreur}}</p></header>`'),
    ("menuOuvert = false;", "menuOuvert = false; erreur = '';"),
    ("deconnecter(): void { this.auth.deconnecter(); this.fermer(); this.router.navigate(['/']); }", "async deconnecter(): Promise<void> { try { await this.auth.deconnecter(); this.fermer(); this.router.navigate(['/']); } catch (e) { this.erreur = messageErreur(e); } }")
])
edit('components/footer.ts', [('Projet de démonstration<br>Les données sont réinitialisées au rechargement.', 'Plateforme de location immobilière<br>Propriétaires et locataires, réunis.')])
edit('components/carte-logement.ts', [
    ('[src]="logement.images[0]"', '[src]="logement.images[0] || \'/images/logement-placeholder.svg\'"'),
    ('(click)="favori()"', '[disabled]="favoris.envoi || favoris.chargement" (click)="favori()"'),
    ('</div></div></article>', '</div>@if (favoris.erreur) { <p class="error" role="alert">{{favoris.erreur}}</p> }</div></article>')
])

edit('pages/accueil.ts', [
    ("import { Component, inject }", "import { Component, inject, OnInit }"),
    ("import { ReservationService } from '../services/reservation.service';", "import { BackendService } from '../services/backend.service';\nimport { firstValueFrom } from 'rxjs';\nimport { messageErreur } from '../services/api-error';\nimport { EtatRequete } from '../components/etat-requete';"),
    ('FiltresLogements, Bouton]', 'FiltresLogements, Bouton, EtatRequete]'),
    ('export class Accueil {', "export class Accueil implements OnInit {\n  chargement = true; erreur = ''; statistiques: {valeur:number; libelle:string}[] = [];"),
    ('demandes = inject(ReservationService);', 'backend = inject(BackendService);'),
    ('''  // Chiffres calculés à partir des données présentes, sans statistiques inventées.
  get statistiques() {
    return [
      {valeur: this.annonces.length, libelle: 'Logements publiés'},
      {valeur: this.auth.comptes.filter(c => c.role === 'proprietaire').length, libelle: 'Propriétaires inscrits'},
      {valeur: new Set(this.annonces.map(l => l.ville.trim().toLowerCase())).size, libelle: 'Villes couvertes'},
      {valeur: this.demandes.reservations.filter(r => r.statut === 'Acceptée').length, libelle: 'Réservations acceptées'}
    ];
  }''', '''  async ngOnInit(): Promise<void> {
    try { await this.biens.charger(); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; }
    try {
      const s = await firstValueFrom(this.backend.statistiques());
      this.statistiques = [{valeur:s.logements,libelle:'Logements publiés'},{valeur:s.proprietaires,libelle:'Propriétaires inscrits'},{valeur:s.villes,libelle:'Villes couvertes'},{valeur:s.reservations,libelle:'Réservations acceptées'}];
    } catch { this.statistiques = []; }
  }''')
])
edit('pages/accueil.html', [
    ('<div class="platform-stats">', '@if (statistiques.length) { <div class="platform-stats">'),
    ('''    </div>
    <small>Chiffres issus des données de démonstration de l'application.</small>''', '''    </div><small>Chiffres issus des données enregistrées sur la plateforme.</small> }'''),
    ('<div class="cards">@for', '<app-etat-requete [chargement]="chargement" [erreur]="erreur" />\n  @if (!chargement && !erreur) { <div class="cards">@for'),
    ('</div> }</div>\n  <div class="center-action">', '</div> }</div> }\n  <div class="center-action">')
])

edit('pages/logements.ts', [
    ("import { LogementService }", "import { EtatRequete } from '../components/etat-requete';\nimport { messageErreur } from '../services/api-error';\nimport { LogementService }"),
    ('[FiltresLogements, CarteLogement]', '[FiltresLogements, CarteLogement, EtatRequete]'),
    ('<p class="result-count"', '<app-etat-requete [chargement]="chargement" [erreur]="erreur" />\n      @if (!chargement && !erreur) { <p class="result-count"'),
    ('</div> }</div>\n    </section>', '</div> }</div> }\n    </section>'),
    ('saisie = criteresVides();', "chargement = false; erreur = '';\n  saisie = criteresVides();"),
    ('appliquer(criteres: CriteresLogements): void { this.filtres = {...criteres}; }', '''async appliquer(criteres: CriteresLogements): Promise<void> {
    this.filtres = {...criteres}; this.chargement = true; this.erreur = '';
    const params: Record<string,string | number> = {};
    for (const [cle, valeur] of Object.entries(criteres)) if (valeur !== null && valeur !== '') params[cle] = valeur;
    try { await this.biens.charger(params); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; }
  }''')
])

edit('pages/detail.ts', [
    ("import { Logement }", "import { EtatRequete } from '../components/etat-requete';\nimport { messageErreur } from '../services/api-error';\nimport { Logement }"),
    ('[RouterLink, DecimalPipe, DatePipe]', '[RouterLink, DecimalPipe, DatePipe, EtatRequete]'),
    ('@if (logement; as l)', '<app-etat-requete [chargement]="chargement" [erreur]="erreur" />@if (logement; as l)'),
    ('} @else { <div class="empty">', '} @else if (!chargement && !erreur) { <div class="empty">'),
    ('<a class="button full" [routerLink]="[\'/reserver\', l.id]">Demander une réservation ↗</a>', '@if (l.disponibleDebut && l.disponibleFin) { <a class="button full" [routerLink]="[\'/reserver\', l.id]">Demander une réservation ↗</a> } @else { <p class="notice">Le propriétaire doit renseigner les disponibilités avant toute réservation.</p> }'),
    ('''export class Detail implements OnInit { route = inject(ActivatedRoute); biens = inject(LogementService); logement?: Logement; ngOnInit(): void { this.route.paramMap.subscribe(p => { const l = this.biens.trouver(Number(p.get('id'))); this.logement = l && !l.archive ? l : undefined; }); } }''', '''export class Detail implements OnInit {
  route = inject(ActivatedRoute); biens = inject(LogementService); logement?: Logement; chargement = true; erreur = '';
  ngOnInit(): void { this.route.paramMap.subscribe(async p => {
    this.chargement = true; this.erreur = ''; this.logement = undefined;
    try { this.logement = await this.biens.consulter(Number(p.get('id'))); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; }
  }); }
}''')
])

edit('pages/compte.ts', [
    ("import { Role, Utilisateur }", "import { messageErreur } from '../services/api-error';\nimport { Utilisateur }"),
    ("Démonstration uniquement : cette connexion n'est pas une authentification sécurisée. Aucun mot de passe n'est enregistré.", 'Votre compte est enregistré sur le serveur. La connexion utilise une session ; aucun mot de passe ne reste dans le navigateur.'),
    ('<button class="button full" type="submit">', '<button class="button full" type="submit" [disabled]="envoi">'),
    ('↗</button></form>', '↗</button>@if (envoi) { <p class="notice" role="status">Enregistrement en cours…</p> }</form>'),
    ('''<div class="demo-box"><strong>Essayer avec un compte de démonstration</strong><p>N'importe quel mot de passe non vide convient.</p><button class="button secondary small" (click)="demo('locataire')">Compte locataire</button> <button class="button secondary small" (click)="demo('proprietaire')">Compte propriétaire</button><small>locataire@demo.tn · proprietaire@demo.tn</small></div>''', ''),
    ('La modification du mot de passe sera disponible avec le backend.', 'La modification du mot de passe nécessite un parcours dédié et reste indisponible.'),
    ("mode = 'connexion';", "envoi = false; mode = 'connexion';"),
    ('''  demo(role: Role): void { this.compte.email = role === 'locataire' ? 'locataire@demo.tn' : 'proprietaire@demo.tn'; this.motDePasse = 'demo123'; }
''', ''),
    ('envoyer(form: NgForm): void {', 'async envoyer(form: NgForm): Promise<void> {'),
    ('''    if (this.mode === 'profil') { if (this.auth.modifier(this.compte)) this.succes = 'Votre profil a été mis à jour.'; else this.erreur = 'Cet email est déjà utilisé.'; return; }
    const ok = this.mode === 'connexion' ? this.auth.connecter(this.compte.email, this.motDePasse) : this.auth.inscrire(this.compte);
    this.motDePasse = '';
    if (!ok) { this.erreur = this.mode === 'connexion' ? 'Compte inconnu. Utilisez un compte de démonstration ou inscrivez-vous.' : 'Cet email est déjà utilisé.'; return; }''', '''    if (this.envoi) return; this.envoi = true;
    try {
    if (this.mode === 'profil') { await this.auth.modifier(this.compte); this.succes = 'Votre profil a été enregistré.'; return; }
    if (this.mode === 'connexion') await this.auth.connecter(this.compte.email, this.motDePasse);
    else await this.auth.inscrire(this.compte, this.motDePasse);
    this.motDePasse = '';'''),
    ('''    else this.router.navigate([this.auth.utilisateur?.role === 'proprietaire' ? '/proprietaire' : '/reservations']);
  }''', '''    else this.router.navigate([this.auth.utilisateur?.role === 'proprietaire' ? '/proprietaire' : '/reservations']);
    } catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; this.motDePasse = ''; }
  }''')
])

edit('pages/formulaire-propriete.ts', [
    ("import { Logement }", "import { messageErreur } from '../services/api-error';\nimport { Logement }"),
    ('@if (introuvable)', '@if (chargement) { <p class="notice" role="status">Chargement du bien…</p> } @else if (introuvable)'),
    ("Ce bien n'existe pas ou ne vous appartient pas.", "{{erreur || 'Ce bien n’existe pas ou ne vous appartient pas.'}}"),
    ('<button class="button" type="submit">', '<button class="button" type="submit" [disabled]="envoi">'),
    ('photoChargee = false; photoErreur = false;', 'photoChargee = false; photoErreur = false; chargement = false; envoi = false;'),
    ('ngOnInit(): void {', 'async ngOnInit(): Promise<void> {'),
    ('''if (id) { const l = this.biens.trouver(Number(id)); if (!l || l.proprietaireId !== this.auth.utilisateur?.id) { this.introuvable = true; return; } this.logement = { ...l, images: [...l.images], equipements: [...l.equipements] }; this.image = l.images[0]; this.equipements = l.equipements.join(', '); }''', '''if (id) { this.chargement = true; try { const l = await this.biens.consulter(Number(id)); if (l.proprietaireId !== this.auth.utilisateur?.id) { this.introuvable = true; return; } this.logement = {...l,images:[...l.images],equipements:[...l.equipements]}; this.image = l.images[0] || ''; this.equipements = l.equipements.join(', '); } catch (e) { this.introuvable = true; this.erreur = messageErreur(e); } finally { this.chargement = false; } }'''),
    ('enregistrer(form: NgForm): void {', 'async enregistrer(form: NgForm): Promise<void> {'),
    ('''    if (this.biens.enregistrer(this.logement, this.auth.utilisateur.id)) this.router.navigate(['/proprietaire']); else this.erreur = 'Ce bien ne vous appartient pas.';''', '''    if (this.envoi) return; this.envoi = true;
    try { await this.biens.enregistrer(this.logement, this.auth.utilisateur.id); this.router.navigate(['/proprietaire'], {queryParams:{enregistre:'1'}}); }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }''')
])

edit('pages/reserver.ts', [
    ("import { Logement }", "import { messageErreur } from '../services/api-error';\nimport { Logement }"),
    ('@if (logement; as l)', '@if (chargement) { <p class="notice" role="status">Chargement du logement…</p> } @if (logement; as l)'),
    ('} @else { <div class="empty">', '} @else if (!chargement) { <div class="empty">'),
    ("Ce logement n'est plus disponible.", "{{erreur || 'Ce logement n’est plus disponible.'}}"),
    ('<button class="button" type="submit">', '<button class="button" type="submit" [disabled]="envoi">'),
    ('''  ngOnInit(): void { const l = this.biens.trouver(Number(this.route.snapshot.paramMap.get('id'))); this.logement = l && !l.archive ? l : undefined; }
  envoyer(form: NgForm): void { if (form.invalid || !this.logement) return; this.erreur = this.demandes.demander(this.logement.id, this.debut, this.fin, this.message); if (!this.erreur) this.router.navigate(['/reservations'], {queryParams: {envoyee: '1'}}); }''', '''  chargement = true; envoi = false;
  async ngOnInit(): Promise<void> { try { const l = await this.biens.consulter(Number(this.route.snapshot.paramMap.get('id'))); this.logement = !l.archive ? l : undefined; } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } }
  async envoyer(form: NgForm): Promise<void> {
    if (form.invalid || !this.logement || this.envoi) return;
    if (this.fin <= this.debut) { this.erreur = 'La fin doit être postérieure au début.'; return; }
    this.envoi = true; this.erreur = '';
    try { await this.demandes.demander(this.logement.id, this.debut, this.fin, this.message); this.router.navigate(['/reservations'], {queryParams:{envoyee:'1'}}); }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }''')
])

edit('pages/proprietaire.ts', [
    ("import { Component, inject }", "import { Component, inject, OnInit }"),
    ("import { Bouton }", "import { ActivatedRoute } from '@angular/router';\nimport { EtatRequete } from '../components/etat-requete';\nimport { messageErreur } from '../services/api-error';\nimport { Bouton }"),
    ('DecimalPipe, Bouton]', 'DecimalPipe, Bouton, EtatRequete]'),
    ('@if (mesBiens.length)', '<app-etat-requete [chargement]="chargement" [erreur]="erreur" />@if (!chargement && !erreur) { @if (mesBiens.length)'),
    ('Publier mon premier bien</a></div> }', 'Publier mon premier bien</a></div> } }'),
    ('(click)="archiver(l.id)"', '[disabled]="envoi" (click)="archiver(l.id)"'),
    ('export class Proprietaire {', 'export class Proprietaire implements OnInit {'),
    ("  succes = '';", "  route = inject(ActivatedRoute); chargement = true; envoi = false; erreur = '';\n  succes = this.route.snapshot.queryParamMap.get('enregistre') ? 'Le bien a été enregistré.' : '';\n  async ngOnInit(): Promise<void> { try { await Promise.all([this.biens.chargerMesBiens(), this.demandes.charger()]); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } }"),
    ('archiver(id: number): void {', 'async archiver(id: number): Promise<void> {'),
    ('''    this.biens.archiver(id, this.auth.utilisateur.id);
    this.succes = this.biens.trouver(id)?.archive ? 'Annonce archivée : elle ne figure plus dans la liste publique.' : 'Annonce réactivée : elle est de nouveau visible.';''', '''    if (this.envoi) return; this.envoi = true; this.erreur = '';
    try { await this.biens.archiver(id, !this.biens.trouver(id)?.archive); this.succes = this.biens.trouver(id)?.archive ? 'Annonce archivée.' : 'Annonce réactivée.'; }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }''')
])

edit('pages/reservations.ts', [
    ("import { Component, inject }", "import { Component, inject, OnInit }"),
    ("import { AuthService }", "import { EtatRequete } from '../components/etat-requete';\nimport { messageErreur } from '../services/api-error';\nimport { AuthService }"),
    ('[RouterLink, DatePipe]', '[RouterLink, DatePipe, EtatRequete]'),
    ('@if (liste.length)', '<app-etat-requete [chargement]="chargement" />@if (!chargement && !erreur) { @if (liste.length)'),
    ('Découvrir les logements</a> }</div> }', 'Découvrir les logements</a> }</div> } }'),
    ('(click)="decider(', '[disabled]="envoi" (click)="decider('),
    ('(click)="annuler(r.id)"', '[disabled]="envoi" (click)="annuler(r.id)"'),
    ('export class Reservations {', 'export class Reservations implements OnInit {'),
    ("  erreur = '';", "  erreur = ''; chargement = true; envoi = false;\n  async ngOnInit(): Promise<void> { try { await Promise.all([this.proprietaire ? this.biens.chargerMesBiens() : this.biens.charger(), this.demandes.charger()]); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } }"),
    ('''  decider(id: number, accepter: boolean): void {
    this.succes = ''; this.erreur = this.demandes.decider(id, accepter);
    if (!this.erreur) this.succes = accepter ? 'La demande a été acceptée.' : 'La demande a été refusée.';
  }
  annuler(id: number): void { this.demandes.annuler(id); this.erreur = ''; this.succes = 'Votre demande a été annulée.'; }''', '''  async decider(id: number, accepter: boolean): Promise<void> {
    if (this.envoi) return; this.envoi = true; this.erreur = ''; this.succes = '';
    try { await this.demandes.decider(id, accepter); this.succes = accepter ? 'La demande a été acceptée.' : 'La demande a été refusée.'; }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }
  async annuler(id: number): Promise<void> {
    if (this.envoi) return; this.envoi = true; this.erreur = ''; this.succes = '';
    try { await this.demandes.annuler(id); this.succes = 'Votre demande a été annulée.'; }
    catch (e) { this.erreur = messageErreur(e); } finally { this.envoi = false; }
  }''')
])

edit('pages/favoris.ts', [
    ("import { Component, inject }", "import { Component, inject, OnInit }"),
    ("import { RouterLink }", "import { EtatRequete } from '../components/etat-requete';\nimport { messageErreur } from '../services/api-error';\nimport { RouterLink }"),
    ('[RouterLink, CarteLogement]', '[RouterLink, CarteLogement, EtatRequete]'),
    ('<div class="cards">', '<app-etat-requete [chargement]="chargement || favoris.chargement" [erreur]="erreur || favoris.erreur" />@if (!chargement && !favoris.chargement && !erreur && !favoris.erreur) { <div class="cards">'),
    ('</div> }</div></section>', '</div> }</div> }</section>'),
    ('export class Favoris {', "export class Favoris implements OnInit { chargement = true; erreur = ''; async ngOnInit(): Promise<void> { try { await Promise.all([this.biens.charger(), this.favoris.charger()]); } catch (e) { this.erreur = messageErreur(e); } finally { this.chargement = false; } }")
])

edit('app.html', [('  <div class="app-layout"', '  @if (auth.erreur) { <p class="error" role="alert">{{auth.erreur}}</p> }\n  <div class="app-layout"')])
edit('services/acces.guard.ts', [('// Ces restrictions servent à la démonstration, pas à la sécurité réelle.', '// La garde guide la navigation ; Spring Boot vérifie également chaque action.')])
print('Pages reliées aux services HTTP.')
