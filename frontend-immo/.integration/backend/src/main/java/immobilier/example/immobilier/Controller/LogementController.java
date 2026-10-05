package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.LogementService;
import immobilier.example.immobilier.dto.ApiDtos.*;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController @RequestMapping("/logements")
public class LogementController {
    private final LogementService service;
    public LogementController(LogementService service) { this.service = service; }
    @GetMapping public List<LogementDto> liste(@RequestParam(required=false) String ville, @RequestParam(required=false) String type, @RequestParam(required=false) Double min, @RequestParam(required=false) Double max, @RequestParam(required=false) Integer pieces) { return service.liste(ville,type,min,max,pieces); }
    @GetMapping("/mes-biens") public List<LogementDto> mesBiens() { return service.mesBiens(); }
    @GetMapping("/{id}") public LogementDto consulter(@PathVariable Long id) { return service.consulter(id); }
    @PostMapping public LogementDto ajouter(@RequestBody LogementDto d) { return service.enregistrer(null,d); }
    @PutMapping("/{id}") public LogementDto modifier(@PathVariable Long id, @RequestBody LogementDto d) { return service.enregistrer(id,d); }
    @PatchMapping("/{id}/archivage") public LogementDto archiver(@PathVariable Long id, @RequestBody Archivage d) { return service.archiver(id,d.archive()); }
    // L'ancien DELETE archive le bien ; aucune ligne de logement n'est supprimée.
    @DeleteMapping("/{id}") public LogementDto supprimer(@PathVariable Long id) { return service.archiver(id,true); }
}
