package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.service.*;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.util.Set;
@RestController @RequestMapping("/favoris") @Transactional
public class FavorisController {
    private final UtilisateurService utilisateurs; private final UtilisateurRepository repository; private final LogementService logements;
    public FavorisController(UtilisateurService utilisateurs, UtilisateurRepository repository, LogementService logements) { this.utilisateurs = utilisateurs; this.repository = repository; this.logements = logements; }
    @GetMapping public Set<Long> liste() { return Set.copyOf(utilisateurs.exigerRole("locataire").getFavorisIds()); }
    @PutMapping("/{id}") public Set<Long> ajouter(@PathVariable Long id) { var u = utilisateurs.exigerRole("locataire"); if (immobilier.example.immobilier.dto.ApiDtos.archive(logements.trouver(id))) throw new ResponseStatusException(CONFLICT, "Annonce archivée."); u.getFavorisIds().add(id); repository.save(u); return Set.copyOf(u.getFavorisIds()); }
    @DeleteMapping("/{id}") public Set<Long> retirer(@PathVariable Long id) { var u = utilisateurs.exigerRole("locataire"); u.getFavorisIds().remove(id); repository.save(u); return Set.copyOf(u.getFavorisIds()); }
}
