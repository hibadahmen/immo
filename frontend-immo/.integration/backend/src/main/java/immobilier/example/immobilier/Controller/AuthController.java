package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.UtilisateurService;
import immobilier.example.immobilier.Entity.Utilisateur;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import jakarta.servlet.http.*;
import java.util.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.csrf.CsrfToken;

@RestController @RequestMapping("/auth")
public class AuthController {
    private final UtilisateurService service;
    public AuthController(UtilisateurService service) { this.service = service; }
    @GetMapping("/csrf") public Map<String,String> csrf(CsrfToken token) { return Map.of("token", token.getToken()); }
    @GetMapping("/moi") public UtilisateurDto moi() { return utilisateur(service.courant()); }
    @PostMapping("/connexion") public UtilisateurDto connexion(@RequestBody Connexion d, HttpServletRequest req, HttpServletResponse res) { return ouvrir(service.connecter(d), req, res); }
    @PostMapping("/inscription") public UtilisateurDto inscription(@RequestBody Inscription d, HttpServletRequest req, HttpServletResponse res) { return ouvrir(service.inscrire(d), req, res); }
    @PostMapping("/deconnexion") public void deconnexion(HttpServletRequest req) { if (req.getSession(false) != null) req.getSession(false).invalidate(); SecurityContextHolder.clearContext(); }
    private UtilisateurDto ouvrir(Utilisateur u, HttpServletRequest req, HttpServletResponse res) {
        req.getSession(); req.changeSessionId();
        var auth = UsernamePasswordAuthenticationToken.authenticated(u.getId().toString(), null, List.of(new SimpleGrantedAuthority("ROLE_" + role(u.getRole()).toUpperCase())));
        var context = SecurityContextHolder.createEmptyContext(); context.setAuthentication(auth); SecurityContextHolder.setContext(context);
        new HttpSessionSecurityContextRepository().saveContext(context, req, res);
        return utilisateur(u);
    }
}
