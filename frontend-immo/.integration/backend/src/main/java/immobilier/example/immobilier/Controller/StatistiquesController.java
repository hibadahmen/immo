package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.transaction.annotation.Transactional;
@RestController @Transactional(readOnly=true)
public class StatistiquesController {
    private final LogementRepository logements; private final UtilisateurRepository utilisateurs; private final DemandeLocationRepository demandes;
    public StatistiquesController(LogementRepository logements, UtilisateurRepository utilisateurs, DemandeLocationRepository demandes) { this.logements = logements; this.utilisateurs = utilisateurs; this.demandes = demandes; }
    @GetMapping("/statistiques") public Statistiques statistiques() {
        var actifs = logements.findAll().stream().filter(l -> !archive(l)).toList();
        return new Statistiques(actifs.size(), utilisateurs.findAll().stream().filter(u -> role(u.getRole()).equals("proprietaire")).count(), actifs.stream().map(l -> l.getVille()).filter(v -> v != null && !v.isBlank()).map(String::toLowerCase).distinct().count(), demandes.findAll().stream().filter(d -> statut(d.getStatut()).equals("Acceptée")).count());
    }
}
