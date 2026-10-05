package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.DemandeLocationService;
import immobilier.example.immobilier.dto.ApiDtos.*;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController @RequestMapping("/demandes")
public class DemandeLocationController {
    private final DemandeLocationService service;
    public DemandeLocationController(DemandeLocationService service) { this.service = service; }
    @GetMapping public List<DemandeDto> liste() { return service.liste(); }
    @PostMapping public DemandeDto ajouter(@RequestBody NouvelleDemande d) { return service.ajouter(d); }
    @PutMapping("/{id}/accepter") public DemandeDto accepter(@PathVariable Long id) { return service.decider(id,"Acceptée"); }
    @PutMapping("/{id}/refuser") public DemandeDto refuser(@PathVariable Long id) { return service.decider(id,"Refusée"); }
    @PutMapping("/{id}/annuler") public DemandeDto annuler(@PathVariable Long id) { return service.decider(id,"Annulée"); }
}
