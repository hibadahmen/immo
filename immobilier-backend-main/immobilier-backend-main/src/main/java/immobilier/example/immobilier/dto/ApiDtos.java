package immobilier.example.immobilier.dto;
import java.time.LocalDate;
import java.util.List;
import immobilier.example.immobilier.Entity.*;

public class ApiDtos {
    public record UtilisateurDto(Long id, String nom, String prenom, String email, String telephone, String role) {}
    public record Inscription(String nom, String prenom, String email, String telephone, String role, String motDePasse) {}
    public record Connexion(String email, String motDePasse) {}
    public record Profil(String nom, String prenom, String email, String telephone) {}
    public record LogementDto(Long id, Long proprietaireId, String titre, String description, String type, String ville, String adresse,
        double prix, double superficie, int pieces, List<String> equipements, List<String> images, LocalDate disponibleDebut, LocalDate disponibleFin, boolean archive) {}
    public record DemandeDto(Long id, Long logementId, Long locataireId, String locataireNom, LocalDate debut, LocalDate fin, String message, String statut) {}
    public record NouvelleDemande(Long logementId, LocalDate debut, LocalDate fin, String message) {}
    public record Archivage(boolean archive) {}
    public record Statistiques(long logements, long proprietaires, long villes, long reservations) {}
    public static String role(String valeur) {
        return valeur != null && valeur.toLowerCase().replace("é", "e").replace("role_", "").equals("proprietaire") ? "proprietaire" : "locataire";
    }
    public static boolean archive(Logement l) { return l.getStatut() != null && l.getStatut().toLowerCase().startsWith("archiv"); }
    public static UtilisateurDto utilisateur(Utilisateur u) { return new UtilisateurDto(u.getId(), u.getNom(), u.getPrenom(), u.getEmail(), u.getTelephone(), role(u.getRole())); }
    public static LogementDto logement(Logement l) {
        return new LogementDto(l.getId(), l.getProprietaire() == null ? null : l.getProprietaire().getId(), l.getTitre(), l.getDescription(),
            l.getType(), l.getVille(), l.getAdresse(), l.getPrix(), l.getSuperficie(), l.getNombrePieces() == null ? 0 : l.getNombrePieces(),
            List.copyOf(l.getEquipements()), List.copyOf(l.getImages()), l.getDisponibleDebut(), l.getDisponibleFin(), archive(l));
    }
    public static String statut(String valeur) {
        if (valeur == null) return "En attente";
        return switch (valeur.toLowerCase().replace("é", "e").replace("ée", "ee").replace("_", " ")) {
            case "acceptee", "accepte" -> "Acceptée";
            case "refusee", "refuse" -> "Refusée";
            case "annulee", "annule" -> "Annulée";
            default -> "En attente";
        };
    }
    public static DemandeDto demande(DemandeLocation d) {
        return new DemandeDto(d.getId(), d.getLogement() == null ? null : d.getLogement().getId(),
            d.getLocataire() == null ? null : d.getLocataire().getId(), d.getLocataire() == null ? "" : d.getLocataire().getPrenom() + " " + d.getLocataire().getNom(),
            d.getDebut(), d.getFin(), d.getMessage(), statut(d.getStatut()));
    }
}
