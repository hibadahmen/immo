import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';
// La garde guide la navigation ; Spring Boot vérifie également chaque action.
export const accesGuard: CanActivateFn = (route, state) => {
  const utilisateur = inject(AuthService).utilisateur; const router = inject(Router);
  if (!utilisateur) return router.createUrlTree(['/connexion'], {queryParams: {retour: state.url}});
  if (route.data['role'] && route.data['role'] !== utilisateur.role) return router.createUrlTree([utilisateur.role === 'proprietaire' ? '/proprietaire' : '/reservations']);
  return true;
};
