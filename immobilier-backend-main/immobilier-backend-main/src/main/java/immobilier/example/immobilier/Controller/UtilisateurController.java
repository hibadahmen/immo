package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.UtilisateurService;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.util.List;
@RestController @RequestMapping("/utilisateurs")
public class UtilisateurController {
    private final UtilisateurService service;
    public UtilisateurController(UtilisateurService service) { this.service = service; }
    @GetMapping public List<UtilisateurDto> liste() { return List.of(utilisateur(service.courant())); }
    @GetMapping("/{id}") public UtilisateurDto consulter(@PathVariable Long id) { var u = service.courant(); if (!u.getId().equals(id)) throw new ResponseStatusException(FORBIDDEN, "Vous ne pouvez consulter que votre profil."); return utilisateur(u); }
    @PutMapping("/moi") public UtilisateurDto modifier(@RequestBody Profil profil) { return service.modifier(profil); }
}
