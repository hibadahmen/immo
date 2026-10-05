package immobilier.example.immobilier.Controller;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.PathVariable;

@RestController
@RequestMapping("/demandes")
public class DemandeLocationController {

    @GetMapping
    public String listeDemandes() {
        return "Liste des demandes";
    }

    @PostMapping
    public String envoyerDemande() {
        return "Demande envoyée";
    }

    @PutMapping("/{id}/accepter")
    public String accepterDemande(@PathVariable Long id) {
        return "Demande acceptée";
    }

    @PutMapping("/{id}/refuser")
    public String refuserDemande(@PathVariable Long id) {
        return "Demande refusée";
    }
}