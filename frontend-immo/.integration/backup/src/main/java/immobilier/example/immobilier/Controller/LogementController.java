package immobilier.example.immobilier.Controller;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
@RestController
@RequestMapping("/logements")
public class LogementController {

    @GetMapping
    public String listeLogements() {
        return "Liste des logements";
    }

    @GetMapping("/{id}")
    public String consulterLogement(@PathVariable Long id) {
        return "Logement " + id;
    }

    @PostMapping
    public String ajouterLogement() {
        return "Logement ajouté";
    }

    @PutMapping("/{id}")
    public String modifierLogement(@PathVariable Long id) {
        return "Logement modifié";
    }

    @DeleteMapping("/{id}")
    public String supprimerLogement(@PathVariable Long id) {
        return "Logement supprimé";
    }
}
