# Angular et Spring Boot : application Darna

Les pages et le design sont conservés. Les annonces, profils, favoris et réservations proviennent maintenant de PostgreSQL via Spring Boot. Il n'y a plus de données fictives dans les services Angular.

## Démarrer les deux projets

Vérifier que PostgreSQL est démarré et que la base configurée dans `application.properties` est accessible. Sa configuration n'a pas été remplacée.

Terminal 1 — backend (le projet Maven est dans le dossier imbriqué) :

```powershell
cd E:\L3MDW1\fullstuck\projet\immobilier-backend-main\immobilier-backend-main
mvn spring-boot:run
```

Terminal 2 — frontend :

```powershell
cd E:\L3MDW1\fullstuck\projet\frontend-immo
npm.cmd start
```

Ouvrir **http://localhost:4200**. Spring Boot écoute sur **8080**. Garder le même nom d'hôte pendant la session : les cookies de `localhost` et de `127.0.0.1` sont distincts. Ne lancer qu'un serveur Angular sur 4200.

## Modifications et notions simples

- `src/app/config/api.config.ts` centralise le préfixe `/api`. `proxy.conf.json` transmet ces requêtes vers `http://localhost:8080` en retirant `/api`.
- `app.config.ts` fournit `HttpClient` et restaure la session au démarrage. Angular envoie automatiquement le cookie et l'en-tête CSRF aux requêtes sur `/api`.
- Les services `logement`, `auth`, `reservation`, `favoris` utilisent HTTP. Les tableaux restants sont des caches de réponses, pas une base de données fictive.
- `await` attend la réponse avant de montrer un succès. En cas d'échec, un message explique le problème et les données affichées ne simulent pas une opération réussie.
- `components/etat-requete.ts` et `services/api-error.ts` partagent les messages de chargement et d'erreur.
- Les pages appellent les services à leur ouverture. Les formulaires d'inscription, connexion, profil, bien et réservation transmettent leurs données au backend.
- `models/models.ts` décrit les réponses des DTO. Les dates sont au format `YYYY-MM-DD`, les identifiants sont numériques et les listes ne sont pas paginées dans cette première intégration.
- Les statistiques publiques sont calculées côté serveur. Elles sont masquées si leur requête échoue.
- `angular.json` utilise un nouveau dossier de cache car l'ancien cache Vite était verrouillé par Windows.

Backend :

- Les trois contrôleurs existants renvoient maintenant des DTO JSON et appellent les services JPA.
- `dto/ApiDtos.java` définit les réponses et formulaires de l'API. Aucun mot de passe ou objet JPA complet n'est renvoyé.
- Les trois entités ont leurs getters/setters. Les dates de début/fin, disponibilités, type, nombre de pièces, images, équipements et favoris manquants ont été ajoutés.
- `nombreChambres` et la date historique de demande sont conservés. Le nombre de pièces utilise une nouvelle colonne distincte : les anciens biens doivent être complétés par leur propriétaire.
- `UtilisateurService` vérifie les informations du profil et hache les nouveaux mots de passe avec BCrypt.
- `LogementService` contrôle le propriétaire, valide les champs et interdit une disponibilité excluant une réservation acceptée.
- `DemandeLocationService` vérifie le rôle, les dates, la disponibilité, le statut et les chevauchements. Un verrou PostgreSQL sur le logement sérialise les décisions concurrentes. L'arrivée le jour du départ précédent est autorisée.
- `SecurityConfig` utilise Spring Security, une session et la protection CSRF. CORS autorise uniquement `http://localhost:4200` et `http://127.0.0.1:4200`, avec credentials. La sécurité n'est pas désactivée.
- Les nouveaux contrôleurs fournissent session, favoris, statistiques et messages d'erreur.

## Endpoints utilisés

Les chemins ci-dessous sont ceux de Spring Boot. Angular les appelle avec le préfixe `/api`.

| Méthode | Chemin | Fonction |
| --- | --- | --- |
| GET | `/auth/csrf` | Préparer le jeton CSRF |
| POST | `/auth/inscription` | Créer un compte et ouvrir une session |
| POST | `/auth/connexion` | Vérifier le mot de passe et ouvrir une session |
| GET | `/auth/moi` | Restaurer le compte depuis la session |
| POST | `/auth/deconnexion` | Fermer la session |
| PUT | `/utilisateurs/moi` | Modifier son profil |
| GET | `/logements` | Annonces publiques ; filtres ville, type, min, max, pieces |
| GET | `/logements/mes-biens` | Biens du propriétaire connecté, archives incluses |
| GET | `/logements/{id}` | Détail public ou archive de son propre bien |
| POST | `/logements` | Publier un bien |
| PUT | `/logements/{id}` | Modifier son bien |
| PATCH | `/logements/{id}/archivage` | Archiver ou réactiver avec `{ "archive": true/false }` |
| GET | `/demandes` | Demandes du locataire ou demandes reçues par le propriétaire |
| POST | `/demandes` | Envoyer logementId, debut, fin, message |
| PUT | `/demandes/{id}/accepter` | Accepter après vérification des chevauchements |
| PUT | `/demandes/{id}/refuser` | Refuser une demande en attente |
| PUT | `/demandes/{id}/annuler` | Annuler sa demande en attente |
| GET | `/favoris` | Identifiants favoris du locataire connecté |
| PUT / DELETE | `/favoris/{id}` | Ajouter / retirer un favori |
| GET | `/statistiques` | Chiffres réels agrégés |

Les routes logements et demandes existaient, mais renvoyaient du texte. Session, favoris, statistiques, profil, liste propriétaire, archivage et annulation manquaient : seuls les endpoints nécessaires ont été ajoutés. L'ancien DELETE logement archive désormais, sans suppression physique. La liste des utilisateurs ne permet de lire que son propre compte.

## Vérifier depuis le navigateur

1. Sur `/inscription`, créer un propriétaire avec un nouvel email et un vrai mot de passe (6 caractères minimum).
2. Publier un bien avec une photo, un loyer, des caractéristiques et une disponibilité. Recharger : il doit rester dans Mes propriétés.
3. Modifier le loyer et le profil, puis recharger pour vérifier les valeurs enregistrées.
4. Se déconnecter et créer un locataire. Chercher le logement, ajouter un favori et recharger `/favoris`.
5. Demander une période comprise dans la disponibilité. Recharger Mes réservations : le statut doit rester En attente.
6. Créer une deuxième demande qui chevauche la première. Revenir au propriétaire : accepter la première, puis essayer la seconde. La seconde acceptation doit être refusée avec un message.
7. Refuser une demande ou revenir au locataire pour annuler une demande en attente.
8. Archiver le bien comme propriétaire : il reste dans son espace, mais disparaît des annonces publiques.
9. Dans les outils du navigateur, onglet Réseau, les requêtes `/api/...` doivent renvoyer du JSON. Les erreurs 401, 403 et 409 signalent respectivement la connexion requise, une action interdite et un conflit métier.

Les anciens comptes dont les mots de passe ne sont pas hachés avec BCrypt ne sont pas acceptés : aucune authentification n'existait auparavant. Leurs données sont conservées. Un parcours de réinitialisation du mot de passe n'est pas fourni ; utiliser de nouveaux comptes pour ce premier test. Aucun mot de passe n'est enregistré dans localStorage.

Les anciens logements sans disponibilité ni nombre de pièces doivent être complétés dans le formulaire. Aucune période fictive n'a été attribuée aux données existantes. La modification du mot de passe et la messagerie ne sont pas ajoutées.

## Vérifications effectuées

- Compilation de production Angular réussie.
- 7 tests Angular réussis dans Chrome : structure, filtres, requêtes API, refus d'une mutation et restauration de session.
- Compilation Maven réussie et démarrage du backend modifié sur 8080.
- Test de démarrage Spring Boot avec PostgreSQL réussi et 4 tests unitaires de réservation réussis.
- Parcours HTTP réel passant par le proxy Angular : inscription, connexion/déconnexion, création/modification/relecture du logement, filtres, favoris, profil, archivage/réactivation, réservation, acceptation/refus/annulation. Les mauvaises permissions renvoient 403 ; le chevauchement renvoie 409.
- Inscription via le véritable formulaire Angular dans Chrome puis rechargement : navigation et session conservées, aucune exception JavaScript.

Les vérifications ont créé des comptes de test identifiés par `integration.invalid`, ainsi qu'un bien marqué `[TEST INTÉGRATION ...]`, archivé à la fin. Ils sont conservés : aucune donnée n'a été supprimée. Le script `.integration/check_api.py` peut être relancé, mais crée de nouveaux comptes et un nouveau bien de test.

La concurrence simultanée de deux acceptations n'a pas été testée en charge. Le déploiement en production et HTTPS restent à configurer. Le proxy Angular sert au développement ; en production, configurer un proxy `/api` sur l'hébergement.

Pour relancer les tests :

```powershell
# Dans le frontend
npm.cmd run build
npm.cmd test -- --watch=false --browsers=ChromeHeadless

# Dans le backend Maven
mvn clean test
```

Une sauvegarde des fichiers backend avant intégration est conservée dans `frontend-immo/.integration/backup`. La base n'a pas été changée : Hibernate conserve `ddl-auto=update` et ajoute les colonnes/tables nécessaires sans recréer la base.
