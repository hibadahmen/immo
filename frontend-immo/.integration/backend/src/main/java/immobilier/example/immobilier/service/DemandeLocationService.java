package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.*;
import immobilier.example.immobilier.repository.DemandeLocationRepository;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.time.LocalDate;
import java.util.List;

@Service @Transactional
public class DemandeLocationService {
    @jakarta.persistence.PersistenceContext
    private jakarta.persistence.EntityManager entityManager;
    private final DemandeLocationRepository repository; private final LogementService logements; private final UtilisateurService utilisateurs;
    public DemandeLocationService(DemandeLocationRepository repository, LogementService logements, UtilisateurService utilisateurs) { this.repository = repository; this.logements = logements; this.utilisateurs = utilisateurs; }
    public List<DemandeDto> liste() {
        Utilisateur u = utilisateurs.courant(); boolean proprietaire = role(u.getRole()).equals("proprietaire");
        return repository.findAll().stream().filter(d -> proprietaire ? d.getLogement() != null && d.getLogement().getProprietaire() != null && u.getId().equals(d.getLogement().getProprietaire().getId()) : d.getLocataire() != null && u.getId().equals(d.getLocataire().getId())).map(immobilier.example.immobilier.dto.ApiDtos::demande).toList();
    }
    public static boolean chevauche(LocalDate debut, LocalDate fin, LocalDate autreDebut, LocalDate autreFin) { return autreDebut != null && autreFin != null && debut.isBefore(autreFin) && fin.isAfter(autreDebut); }
    private void disponibilite(Logement l, LocalDate debut, LocalDate fin) {
        if (debut == null || fin == null || !fin.isAfter(debut)) throw new ResponseStatusException(BAD_REQUEST, "La fin doit être postérieure au début.");
        if (archive(l) || l.getDisponibleDebut() == null || l.getDisponibleFin() == null || debut.isBefore(l.getDisponibleDebut()) || fin.isAfter(l.getDisponibleFin())) throw new ResponseStatusException(CONFLICT, "Le logement n'est pas disponible sur cette période.");
        if (repository.findAll().stream().anyMatch(r -> r.getLogement() != null && l.getId().equals(r.getLogement().getId()) && statut(r.getStatut()).equals("Acceptée") && chevauche(debut, fin, r.getDebut(), r.getFin()))) throw new ResponseStatusException(CONFLICT, "Une réservation acceptée chevauche ces dates.");
    }
    public DemandeDto ajouter(NouvelleDemande d) {
        Utilisateur u = utilisateurs.exigerRole("locataire"); if (d.logementId() == null) throw new ResponseStatusException(BAD_REQUEST, "Choisissez un logement.");
        Logement l = logements.verrouiller(d.logementId()); disponibilite(l,d.debut(),d.fin());
        if (d.message() != null && d.message().length() > 1500) throw new ResponseStatusException(BAD_REQUEST, "Message trop long.");
        DemandeLocation demande = new DemandeLocation(); demande.setDate(LocalDate.now()); demande.setDebut(d.debut()); demande.setFin(d.fin()); demande.setMessage(d.message()); demande.setStatut("En attente"); demande.setLogement(l); demande.setLocataire(u); return demande(repository.save(demande));
    }
    public DemandeDto decider(Long id, String decision) {
        DemandeLocation d = repository.findById(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Demande introuvable."));
        if (d.getLogement() == null) throw new ResponseStatusException(CONFLICT, "Logement manquant.");
        // Toutes les décisions pour un même bien partagent ce verrou transactionnel.
        Logement l = logements.verrouiller(d.getLogement().getId());
        // Recharger après le verrou pour voir une décision concurrente sur la demande.
        entityManager.refresh(d);
        if (!statut(d.getStatut()).equals("En attente")) throw new ResponseStatusException(CONFLICT, "Cette demande a déjà été traitée.");
        if (decision.equals("Annulée")) {
            var u = utilisateurs.exigerRole("locataire"); if (d.getLocataire() == null || !u.getId().equals(d.getLocataire().getId())) throw new ResponseStatusException(FORBIDDEN, "Cette demande ne vous appartient pas.");
        } else { logements.verifierProprietaire(l); if (decision.equals("Acceptée")) disponibilite(l,d.getDebut(),d.getFin()); }
        d.setStatut(decision); return demande(repository.save(d));
    }
}
