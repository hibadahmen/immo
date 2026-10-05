package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.*;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.service.UtilisateurService.texte;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.util.List;

@Service @Transactional
public class LogementService {
    private final LogementRepository repository; private final UtilisateurService utilisateurs; private final DemandeLocationRepository demandes;
    public LogementService(LogementRepository repository, UtilisateurService utilisateurs, DemandeLocationRepository demandes) { this.repository = repository; this.utilisateurs = utilisateurs; this.demandes = demandes; }
    public Logement trouver(Long id) { return repository.findById(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Logement introuvable.")); }
    public Logement verrouiller(Long id) { return repository.verrouiller(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Logement introuvable.")); }
    public void verifierProprietaire(Logement l) { var u = utilisateurs.exigerRole("proprietaire"); if (l.getProprietaire() == null || !u.getId().equals(l.getProprietaire().getId())) throw new ResponseStatusException(FORBIDDEN, "Ce bien ne vous appartient pas."); }
    public List<LogementDto> liste(String ville, String type, Double min, Double max, Integer pieces) {
        if ((min != null && min < 0) || (max != null && max < 0) || (min != null && max != null && min > max)) throw new ResponseStatusException(BAD_REQUEST, "Budget invalide.");
        return repository.findAll().stream().filter(l -> !archive(l))
            .filter(l -> ville == null || ville.isBlank() || (l.getVille() != null && l.getVille().toLowerCase().contains(ville.toLowerCase())))
            .filter(l -> type == null || type.isBlank() || type.equals(l.getType()))
            .filter(l -> min == null || l.getPrix() >= min).filter(l -> max == null || l.getPrix() <= max)
            .filter(l -> pieces == null || pieces.equals(l.getNombrePieces())).map(immobilier.example.immobilier.dto.ApiDtos::logement).toList();
    }
    public List<LogementDto> mesBiens() { Long id = utilisateurs.exigerRole("proprietaire").getId(); return repository.findAll().stream().filter(l -> l.getProprietaire() != null && id.equals(l.getProprietaire().getId())).map(immobilier.example.immobilier.dto.ApiDtos::logement).toList(); }
    public LogementDto consulter(Long id) { Logement l = trouver(id); if (archive(l)) verifierProprietaire(l); return logement(l); }
    public LogementDto enregistrer(Long id, LogementDto d) {
        var u = utilisateurs.exigerRole("proprietaire"); Logement l = id == null ? new Logement() : verrouiller(id); if (id != null) verifierProprietaire(l);
        texte(d.titre(),120); texte(d.description(),5000); texte(d.ville(),120); texte(d.adresse(),255);
        if (!List.of("Appartement","Maison","Studio","Villa").contains(d.type()) || !Double.isFinite(d.prix()) || d.prix() <= 0 || !Double.isFinite(d.superficie()) || d.superficie() <= 0 || d.pieces() <= 0) throw new ResponseStatusException(BAD_REQUEST, "Type, prix, superficie ou nombre de pièces invalide.");
        if (d.disponibleDebut() == null || d.disponibleFin() == null || !d.disponibleFin().isAfter(d.disponibleDebut())) throw new ResponseStatusException(BAD_REQUEST, "Dates de disponibilité invalides.");
        if (d.images() == null || d.images().isEmpty() || d.images().size() > 20 || d.images().stream().anyMatch(image -> image == null || image.length() > 255 || !image.matches("(?i)^(https?://|/)[^\\s]+$"))) throw new ResponseStatusException(BAD_REQUEST, "Ajoutez une URL HTTP(S) ou un chemin /images/... valide.");
        if (d.equipements() != null && (d.equipements().size() > 50 || d.equipements().stream().anyMatch(e -> e == null || e.isBlank() || e.length() > 255))) throw new ResponseStatusException(BAD_REQUEST, "Équipements invalides.");
        if (id != null && demandes.findAll().stream().anyMatch(r -> r.getLogement() != null && id.equals(r.getLogement().getId()) && statut(r.getStatut()).equals("Acceptée") && (r.getDebut() == null || r.getFin() == null || r.getDebut().isBefore(d.disponibleDebut()) || r.getFin().isAfter(d.disponibleFin())))) throw new ResponseStatusException(CONFLICT, "La disponibilité doit conserver les réservations acceptées.");
        l.setTitre(d.titre().trim()); l.setDescription(d.description().trim()); l.setVille(d.ville().trim()); l.setAdresse(d.adresse().trim()); l.setPrix(d.prix()); l.setSuperficie(d.superficie()); l.setNombrePieces(d.pieces()); l.setType(d.type());
        l.setDisponibleDebut(d.disponibleDebut()); l.setDisponibleFin(d.disponibleFin()); l.setImages(new java.util.ArrayList<>(d.images())); l.setEquipements(new java.util.ArrayList<>(d.equipements() == null ? List.of() : d.equipements()));
        if (id == null) { l.setProprietaire(u); l.setStatut("ACTIVE"); }
        return logement(repository.save(l));
    }
    public LogementDto archiver(Long id, boolean archive) { Logement l = verrouiller(id); verifierProprietaire(l); l.setStatut(archive ? "ARCHIVE" : "ACTIVE"); return logement(repository.save(l)); }
}
