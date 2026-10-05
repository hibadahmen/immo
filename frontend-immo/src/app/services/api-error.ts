import { HttpErrorResponse } from '@angular/common/http';
export function messageErreur(e: unknown): string {
  if (e instanceof HttpErrorResponse) {
    if (e.status === 0 || e.status === 502 || e.status === 504) return 'Serveur indisponible. Vérifiez que Spring Boot est lancé sur le port 8080.';
    if (typeof e.error?.message === 'string') return e.error.message;
    if (e.status === 401) return 'Session expirée. Veuillez vous reconnecter.';
    if (e.status === 403) return 'Action non autorisée. Rechargez la page si votre session a expiré.';
  }
  return 'Impossible de terminer cette opération. Réessayez.';
}
