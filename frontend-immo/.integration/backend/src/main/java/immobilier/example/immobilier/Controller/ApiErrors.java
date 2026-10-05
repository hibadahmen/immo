package immobilier.example.immobilier.Controller;
import java.util.Map;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.ResponseEntity;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.converter.HttpMessageNotReadableException;
@RestControllerAdvice
public class ApiErrors {
    @ExceptionHandler(ResponseStatusException.class)
    ResponseEntity<?> erreur(ResponseStatusException ex) { return ResponseEntity.status(ex.getStatusCode()).body(Map.of("message", ex.getReason() == null ? "Opération impossible." : ex.getReason())); }
    @ExceptionHandler(DataIntegrityViolationException.class)
    ResponseEntity<?> conflit(DataIntegrityViolationException ex) { return ResponseEntity.status(409).body(Map.of("message", "Ces données existent déjà ou ne peuvent pas être enregistrées.")); }
    @ExceptionHandler(HttpMessageNotReadableException.class)
    ResponseEntity<?> format(HttpMessageNotReadableException ex) { return ResponseEntity.badRequest().body(Map.of("message", "Vérifiez le format des champs et des dates.")); }
}
