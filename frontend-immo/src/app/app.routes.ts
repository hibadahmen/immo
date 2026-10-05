import { Routes } from '@angular/router';
import { accesGuard } from './services/acces.guard';

export const routes: Routes = [
  {path: '', loadComponent: () => import('./pages/accueil').then(m => m.Accueil)},
  {path: 'logements', loadComponent: () => import('./pages/logements').then(m => m.Logements)},
  {path: 'logements/:id', loadComponent: () => import('./pages/detail').then(m => m.Detail)},
  {path: 'connexion', data: {mode: 'connexion'}, loadComponent: () => import('./pages/compte').then(m => m.Compte)},
  {path: 'inscription', data: {mode: 'inscription'}, loadComponent: () => import('./pages/compte').then(m => m.Compte)},
  {path: 'profil', canActivate: [accesGuard], data: {mode: 'profil'}, loadComponent: () => import('./pages/compte').then(m => m.Compte)},
  {path: 'proprietaire', canActivate: [accesGuard], data: {role: 'proprietaire'}, loadComponent: () => import('./pages/proprietaire').then(m => m.Proprietaire)},
  {path: 'proprietaire/ajouter', canActivate: [accesGuard], data: {role: 'proprietaire'}, loadComponent: () => import('./pages/formulaire-propriete').then(m => m.FormulairePropriete)},
  {path: 'proprietaire/modifier/:id', canActivate: [accesGuard], data: {role: 'proprietaire'}, loadComponent: () => import('./pages/formulaire-propriete').then(m => m.FormulairePropriete)},
  {path: 'proprietaire/demandes', canActivate: [accesGuard], data: {role: 'proprietaire', proprietaire: true}, loadComponent: () => import('./pages/reservations').then(m => m.Reservations)},
  {path: 'reserver/:id', canActivate: [accesGuard], data: {role: 'locataire'}, loadComponent: () => import('./pages/reserver').then(m => m.Reserver)},
  {path: 'reservations', canActivate: [accesGuard], data: {role: 'locataire'}, loadComponent: () => import('./pages/reservations').then(m => m.Reservations)},
  {path: 'favoris', canActivate: [accesGuard], data: {role: 'locataire'}, loadComponent: () => import('./pages/favoris').then(m => m.Favoris)},
  {path: '**', loadComponent: () => import('./pages/introuvable').then(m => m.Introuvable)}
];
