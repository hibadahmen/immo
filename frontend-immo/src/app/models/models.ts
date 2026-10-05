export type Role = 'locataire' | 'proprietaire';
export interface Utilisateur { id: number; nom: string; prenom: string; email: string; telephone: string; role: Role; }
export interface Logement {
  id: number; proprietaireId: number | null; titre: string; description: string; type: string;
  ville: string; adresse: string; prix: number; superficie: number; pieces: number;
  equipements: string[]; images: string[]; disponibleDebut: string; disponibleFin: string; archive: boolean;
}
export type Statut = 'En attente' | 'Acceptée' | 'Refusée' | 'Annulée';
export interface Reservation { id: number; logementId: number | null; locataireId: number | null; locataireNom: string; debut: string | null; fin: string | null; message: string | null; statut: Statut; }
