package immobilier.example.immobilier.Controller;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@RestController
@RequestMapping("/utilisateurs")
public class UtilisateurController {

    @GetMapping
    public String listeUtilisateurs() {
        return "Liste des utilisateurs";
    }

    @GetMapping("/{id}")
    public String consulterUtilisateur(@PathVariable Long id) {
        return "Utilisateur " + id;
    }
}