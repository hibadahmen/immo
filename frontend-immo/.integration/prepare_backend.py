from pathlib import Path
import shutil

source = Path('../immobilier-backend-main/immobilier-backend-main').resolve()
target = Path('.integration/backend').resolve()
shutil.copytree(source / 'src', target / 'src', dirs_exist_ok=True)
shutil.copy2(source / 'pom.xml', target / 'pom.xml')
base = target / 'src/main/java/immobilier/example/immobilier'

def write(path, text):
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text.strip() + '\n', encoding='utf-8')

# Garder les colonnes existantes et ajouter seulement les champs manquants.
entities = {
 'Utilisateur': [('Long','id'),('String','nom'),('String','prenom'),('String','email'),('String','motDePasse'),('String','telephone'),('String','role'),('Set<Long>','favorisIds')],
 'Logement': [('Long','id'),('String','titre'),('String','description'),('double','prix'),('String','adresse'),('String','ville'),('double','superficie'),('int','nombreChambres'),('String','statut'),('Utilisateur','proprietaire'),('String','type'),('Integer','nombrePieces'),('LocalDate','disponibleDebut'),('LocalDate','disponibleFin'),('List<String>','images'),('List<String>','equipements')],
 'DemandeLocation': [('Long','id'),('LocalDate','date'),('String','message'),('String','statut'),('Utilisateur','locataire'),('Logement','logement'),('LocalDate','debut'),('LocalDate','fin')]
}
for name, fields in entities.items():
    content = 'package immobilier.example.immobilier.Entity;\n\nimport jakarta.persistence.*;\nimport java.time.LocalDate;\nimport java.util.*;\n\n@Entity\npublic class ' + name + ' {\n'
    for kind, field in fields:
        annotation = ''
        initial = ''
        if field == 'id': annotation = '    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)\n'
        elif kind in ['Utilisateur', 'Logement']: annotation = '    @ManyToOne\n'
        elif kind.startswith('List'): annotation = '    @ElementCollection\n    @OrderColumn\n'; initial = ' = new ArrayList<>()'
        elif kind.startswith('Set'): annotation = '    @ElementCollection\n'; initial = ' = new HashSet<>()'
        # Les grands textes peuvent dépasser 255 caractères, sans toucher aux données existantes.
        elif field in ['description','message']: annotation = '    @Column(length = 5000)\n'
        content += annotation + f'    private {kind} {field}{initial};\n'
    for kind, field in fields:
        cap = field[0].upper() + field[1:]
        content += f'    public {kind} get{cap}() {{ return {field}; }}\n    public void set{cap}({kind} valeur) {{ this.{field} = valeur; }}\n'
    write('Entity/' + name + '.java', content + '}')

pom = (target / 'pom.xml').read_text(encoding='utf-8')
pom = pom.replace('<dependencies>', '<dependencies>\n        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>')
(target / 'pom.xml').write_text(pom, encoding='utf-8')
properties = target / 'src/main/resources/application.properties'
with properties.open('a', encoding='utf-8') as stream:
    stream.write('\n# Session locale : le cookie de session reste inaccessible au JavaScript.\nserver.servlet.session.cookie.http-only=true\nserver.servlet.session.cookie.same-site=lax\nserver.servlet.session.timeout=30m\nspring.jpa.open-in-view=false\n')

write('dto/ApiDtos.java', '''
package immobilier.example.immobilier.dto;
import java.time.LocalDate;
import java.util.List;
import immobilier.example.immobilier.Entity.*;

public class ApiDtos {
    public record UtilisateurDto(Long id, String nom, String prenom, String email, String telephone, String role) {}
    public record Inscription(String nom, String prenom, String email, String telephone, String role, String motDePasse) {}
    public record Connexion(String email, String motDePasse) {}
    public record Profil(String nom, String prenom, String email, String telephone) {}
    public record LogementDto(Long id, Long proprietaireId, String titre, String description, String type, String ville, String adresse,
        double prix, double superficie, int pieces, List<String> equipements, List<String> images, LocalDate disponibleDebut, LocalDate disponibleFin, boolean archive) {}
    public record DemandeDto(Long id, Long logementId, Long locataireId, String locataireNom, LocalDate debut, LocalDate fin, String message, String statut) {}
    public record NouvelleDemande(Long logementId, LocalDate debut, LocalDate fin, String message) {}
    public record Archivage(boolean archive) {}
    public record Statistiques(long logements, long proprietaires, long villes, long reservations) {}
    public static String role(String valeur) {
        return valeur != null && valeur.toLowerCase().replace("é", "e").replace("role_", "").equals("proprietaire") ? "proprietaire" : "locataire";
    }
    public static boolean archive(Logement l) { return l.getStatut() != null && l.getStatut().toLowerCase().startsWith("archiv"); }
    public static UtilisateurDto utilisateur(Utilisateur u) { return new UtilisateurDto(u.getId(), u.getNom(), u.getPrenom(), u.getEmail(), u.getTelephone(), role(u.getRole())); }
    public static LogementDto logement(Logement l) {
        return new LogementDto(l.getId(), l.getProprietaire() == null ? null : l.getProprietaire().getId(), l.getTitre(), l.getDescription(),
            l.getType(), l.getVille(), l.getAdresse(), l.getPrix(), l.getSuperficie(), l.getNombrePieces() == null ? 0 : l.getNombrePieces(),
            List.copyOf(l.getEquipements()), List.copyOf(l.getImages()), l.getDisponibleDebut(), l.getDisponibleFin(), archive(l));
    }
    public static String statut(String valeur) {
        if (valeur == null) return "En attente";
        return switch (valeur.toLowerCase().replace("é", "e").replace("ée", "ee").replace("_", " ")) {
            case "acceptee", "accepte" -> "Acceptée";
            case "refusee", "refuse" -> "Refusée";
            case "annulee", "annule" -> "Annulée";
            default -> "En attente";
        };
    }
    public static DemandeDto demande(DemandeLocation d) {
        return new DemandeDto(d.getId(), d.getLogement() == null ? null : d.getLogement().getId(),
            d.getLocataire() == null ? null : d.getLocataire().getId(), d.getLocataire() == null ? "" : d.getLocataire().getPrenom() + " " + d.getLocataire().getNom(),
            d.getDebut(), d.getFin(), d.getMessage(), statut(d.getStatut()));
    }
}
''')

write('config/SecurityConfig.java', '''
package immobilier.example.immobilier.config;
import java.util.List;
import org.springframework.context.annotation.*;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.csrf.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.cors.*;

@Configuration
public class SecurityConfig {
    @Bean PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }
    @Bean SecurityFilterChain security(HttpSecurity http) throws Exception {
        return http.cors(cors -> cors.configurationSource(corsConfiguration()))
            .csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(HttpMethod.GET, "/logements", "/logements/*", "/statistiques", "/auth/csrf", "/auth/moi").permitAll()
                .requestMatchers(HttpMethod.POST, "/auth/connexion", "/auth/inscription").permitAll()
                .requestMatchers("/error").permitAll()
                .anyRequest().authenticated())
            .exceptionHandling(errors -> errors
                .authenticationEntryPoint((req, res, ex) -> { res.setStatus(401); res.setContentType("application/json;charset=UTF-8"); res.getWriter().write("{\\"message\\":\\"Veuillez vous connecter.\\"}"); })
                .accessDeniedHandler((req, res, ex) -> { res.setStatus(403); res.setContentType("application/json;charset=UTF-8"); res.getWriter().write("{\\"message\\":\\"Action non autorisée ou session expirée. Rechargez la page.\\"}"); }))
            .build();
    }
    @Bean CorsConfigurationSource corsConfiguration() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:4200", "http://127.0.0.1:4200"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("Content-Type", "X-XSRF-TOKEN"));
        config.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config); return source;
    }
}
''')

write('Controller/ApiErrors.java', '''
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
''')

write('repository/UtilisateurRepository.java', '''
package immobilier.example.immobilier.repository;
import immobilier.example.immobilier.Entity.Utilisateur;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
public interface UtilisateurRepository extends JpaRepository<Utilisateur, Long> {
    Optional<Utilisateur> findByEmailIgnoreCase(String email);
}
''')
write('repository/LogementRepository.java', '''
package immobilier.example.immobilier.repository;
import immobilier.example.immobilier.Entity.Logement;
import java.util.Optional;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
public interface LogementRepository extends JpaRepository<Logement, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select l from Logement l where l.id = :id")
    Optional<Logement> verrouiller(@Param("id") Long id);
}
''')

write('service/UtilisateurService.java', '''
package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.Utilisateur;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;

@Service @Transactional
public class UtilisateurService {
    private final UtilisateurRepository repository;
    private final PasswordEncoder passwords;
    public UtilisateurService(UtilisateurRepository repository, PasswordEncoder passwords) { this.repository = repository; this.passwords = passwords; }
    public Utilisateur courant() {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || auth.getName().equals("anonymousUser")) throw new ResponseStatusException(UNAUTHORIZED, "Veuillez vous connecter.");
        try { return repository.findById(Long.valueOf(auth.getName())).orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED, "Compte introuvable.")); }
        catch (NumberFormatException ex) { throw new ResponseStatusException(UNAUTHORIZED, "Session invalide."); }
    }
    public Utilisateur exigerRole(String roleAttendu) { Utilisateur u = courant(); if (!role(u.getRole()).equals(roleAttendu)) throw new ResponseStatusException(FORBIDDEN, "Cette action ne correspond pas à votre rôle."); return u; }
    public static String texte(String valeur, int max) { if (valeur == null || valeur.isBlank() || valeur.length() > max) throw new ResponseStatusException(BAD_REQUEST, "Complétez les champs obligatoires (longueur invalide)."); return valeur.trim(); }
    private String email(String valeur) { String email = texte(valeur, 254).toLowerCase(); if (!email.matches("[^\\\\s@]+@[^\\\\s@]+\\\\.[^\\\\s@]+")) throw new ResponseStatusException(BAD_REQUEST, "Email invalide."); return email; }
    private void verifierProfil(String nom, String prenom, String telephone) { texte(nom,60); texte(prenom,60); if (!texte(telephone,20).matches("[+0-9 ()-]{8,20}")) throw new ResponseStatusException(BAD_REQUEST, "Téléphone invalide."); }
    public Utilisateur inscrire(Inscription d) {
        verifierProfil(d.nom(), d.prenom(), d.telephone()); String email = email(d.email());
        if (repository.findByEmailIgnoreCase(email).isPresent()) throw new ResponseStatusException(CONFLICT, "Cet email est déjà utilisé.");
        if (!java.util.List.of("locataire", "proprietaire").contains(d.role())) throw new ResponseStatusException(BAD_REQUEST, "Rôle invalide.");
        String password = texte(d.motDePasse(),72); if (password.length() < 6 || password.getBytes(java.nio.charset.StandardCharsets.UTF_8).length > 72) throw new ResponseStatusException(BAD_REQUEST, "Mot de passe : 6 caractères minimum et 72 octets maximum.");
        Utilisateur u = new Utilisateur(); u.setNom(d.nom().trim()); u.setPrenom(d.prenom().trim()); u.setEmail(email); u.setTelephone(d.telephone().trim()); u.setRole(d.role()); u.setMotDePasse(passwords.encode(d.motDePasse())); return repository.save(u);
    }
    public Utilisateur connecter(Connexion d) {
        Utilisateur u = repository.findByEmailIgnoreCase(email(d.email())).orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED, "Email ou mot de passe incorrect."));
        if (d.motDePasse() == null || u.getMotDePasse() == null || !u.getMotDePasse().startsWith("$2") || !passwords.matches(d.motDePasse(), u.getMotDePasse())) throw new ResponseStatusException(UNAUTHORIZED, "Email ou mot de passe incorrect. Les anciens comptes sans mot de passe BCrypt doivent être réinitialisés.");
        return u;
    }
    public UtilisateurDto modifier(Profil d) {
        Utilisateur u = courant(); verifierProfil(d.nom(), d.prenom(), d.telephone()); String email = email(d.email());
        repository.findByEmailIgnoreCase(email).filter(autre -> !autre.getId().equals(u.getId())).ifPresent(autre -> { throw new ResponseStatusException(CONFLICT, "Cet email est déjà utilisé."); });
        u.setNom(d.nom().trim()); u.setPrenom(d.prenom().trim()); u.setTelephone(d.telephone().trim()); u.setEmail(email); return utilisateur(repository.save(u));
    }
}
''')

write('Controller/UtilisateurController.java', '''
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
''')

write('Controller/AuthController.java', '''
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
''')

write('service/LogementService.java', '''
package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.*;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.service.UtilisateurService.texte;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.util.List;

@Service @Transactional
public class LogementService {
    private final LogementRepository repository; private final UtilisateurService utilisateurs; private final DemandeLocationRepository demandes;
    public LogementService(LogementRepository repository, UtilisateurService utilisateurs, DemandeLocationRepository demandes) { this.repository = repository; this.utilisateurs = utilisateurs; this.demandes = demandes; }
    public Logement trouver(Long id) { return repository.findById(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Logement introuvable.")); }
    public Logement verrouiller(Long id) { return repository.verrouiller(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Logement introuvable.")); }
    public void verifierProprietaire(Logement l) { var u = utilisateurs.exigerRole("proprietaire"); if (l.getProprietaire() == null || !u.getId().equals(l.getProprietaire().getId())) throw new ResponseStatusException(FORBIDDEN, "Ce bien ne vous appartient pas."); }
    public List<LogementDto> liste(String ville, String type, Double min, Double max, Integer pieces) {
        if ((min != null && min < 0) || (max != null && max < 0) || (min != null && max != null && min > max)) throw new ResponseStatusException(BAD_REQUEST, "Budget invalide.");
        return repository.findAll().stream().filter(l -> !archive(l))
            .filter(l -> ville == null || ville.isBlank() || (l.getVille() != null && l.getVille().toLowerCase().contains(ville.toLowerCase())))
            .filter(l -> type == null || type.isBlank() || type.equals(l.getType()))
            .filter(l -> min == null || l.getPrix() >= min).filter(l -> max == null || l.getPrix() <= max)
            .filter(l -> pieces == null || pieces.equals(l.getNombrePieces())).map(immobilier.example.immobilier.dto.ApiDtos::logement).toList();
    }
    public List<LogementDto> mesBiens() { Long id = utilisateurs.exigerRole("proprietaire").getId(); return repository.findAll().stream().filter(l -> l.getProprietaire() != null && id.equals(l.getProprietaire().getId())).map(immobilier.example.immobilier.dto.ApiDtos::logement).toList(); }
    public LogementDto consulter(Long id) { Logement l = trouver(id); if (archive(l)) verifierProprietaire(l); return logement(l); }
    public LogementDto enregistrer(Long id, LogementDto d) {
        var u = utilisateurs.exigerRole("proprietaire"); Logement l = id == null ? new Logement() : verrouiller(id); if (id != null) verifierProprietaire(l);
        texte(d.titre(),120); texte(d.description(),5000); texte(d.ville(),120); texte(d.adresse(),255);
        if (!List.of("Appartement","Maison","Studio","Villa").contains(d.type()) || !Double.isFinite(d.prix()) || d.prix() <= 0 || !Double.isFinite(d.superficie()) || d.superficie() <= 0 || d.pieces() <= 0) throw new ResponseStatusException(BAD_REQUEST, "Type, prix, superficie ou nombre de pièces invalide.");
        if (d.disponibleDebut() == null || d.disponibleFin() == null || !d.disponibleFin().isAfter(d.disponibleDebut())) throw new ResponseStatusException(BAD_REQUEST, "Dates de disponibilité invalides.");
        if (d.images() == null || d.images().isEmpty() || d.images().size() > 20 || d.images().stream().anyMatch(image -> image == null || image.length() > 255 || !image.matches("(?i)^(https?://|/)[^\\\\s]+$"))) throw new ResponseStatusException(BAD_REQUEST, "Ajoutez une URL HTTP(S) ou un chemin /images/... valide.");
        if (d.equipements() != null && (d.equipements().size() > 50 || d.equipements().stream().anyMatch(e -> e == null || e.isBlank() || e.length() > 255))) throw new ResponseStatusException(BAD_REQUEST, "Équipements invalides.");
        if (id != null && demandes.findAll().stream().anyMatch(r -> r.getLogement() != null && id.equals(r.getLogement().getId()) && statut(r.getStatut()).equals("Acceptée") && (r.getDebut() == null || r.getFin() == null || r.getDebut().isBefore(d.disponibleDebut()) || r.getFin().isAfter(d.disponibleFin())))) throw new ResponseStatusException(CONFLICT, "La disponibilité doit conserver les réservations acceptées.");
        l.setTitre(d.titre().trim()); l.setDescription(d.description().trim()); l.setVille(d.ville().trim()); l.setAdresse(d.adresse().trim()); l.setPrix(d.prix()); l.setSuperficie(d.superficie()); l.setNombrePieces(d.pieces()); l.setType(d.type());
        l.setDisponibleDebut(d.disponibleDebut()); l.setDisponibleFin(d.disponibleFin()); l.setImages(new java.util.ArrayList<>(d.images())); l.setEquipements(new java.util.ArrayList<>(d.equipements() == null ? List.of() : d.equipements()));
        if (id == null) { l.setProprietaire(u); l.setStatut("ACTIVE"); }
        return logement(repository.save(l));
    }
    public LogementDto archiver(Long id, boolean archive) { Logement l = verrouiller(id); verifierProprietaire(l); l.setStatut(archive ? "ARCHIVE" : "ACTIVE"); return logement(repository.save(l)); }
}
''')

write('Controller/LogementController.java', '''
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
''')

write('service/DemandeLocationService.java', '''
package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.*;
import immobilier.example.immobilier.repository.DemandeLocationRepository;
import immobilier.example.immobilier.dto.ApiDtos.*;
import static immobilier.example.immobilier.dto.ApiDtos.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.time.LocalDate;
import java.util.List;

@Service @Transactional
public class DemandeLocationService {
    private final DemandeLocationRepository repository; private final LogementService logements; private final UtilisateurService utilisateurs;
    public DemandeLocationService(DemandeLocationRepository repository, LogementService logements, UtilisateurService utilisateurs) { this.repository = repository; this.logements = logements; this.utilisateurs = utilisateurs; }
    public List<DemandeDto> liste() {
        Utilisateur u = utilisateurs.courant(); boolean proprietaire = role(u.getRole()).equals("proprietaire");
        return repository.findAll().stream().filter(d -> proprietaire ? d.getLogement() != null && d.getLogement().getProprietaire() != null && u.getId().equals(d.getLogement().getProprietaire().getId()) : d.getLocataire() != null && u.getId().equals(d.getLocataire().getId())).map(immobilier.example.immobilier.dto.ApiDtos::demande).toList();
    }
    public static boolean chevauche(LocalDate debut, LocalDate fin, LocalDate autreDebut, LocalDate autreFin) { return autreDebut != null && autreFin != null && debut.isBefore(autreFin) && fin.isAfter(autreDebut); }
    private void disponibilite(Logement l, LocalDate debut, LocalDate fin) {
        if (debut == null || fin == null || !fin.isAfter(debut)) throw new ResponseStatusException(BAD_REQUEST, "La fin doit être postérieure au début.");
        if (archive(l) || l.getDisponibleDebut() == null || l.getDisponibleFin() == null || debut.isBefore(l.getDisponibleDebut()) || fin.isAfter(l.getDisponibleFin())) throw new ResponseStatusException(CONFLICT, "Le logement n'est pas disponible sur cette période.");
        if (repository.findAll().stream().anyMatch(r -> r.getLogement() != null && l.getId().equals(r.getLogement().getId()) && statut(r.getStatut()).equals("Acceptée") && chevauche(debut, fin, r.getDebut(), r.getFin()))) throw new ResponseStatusException(CONFLICT, "Une réservation acceptée chevauche ces dates.");
    }
    public DemandeDto ajouter(NouvelleDemande d) {
        Utilisateur u = utilisateurs.exigerRole("locataire"); if (d.logementId() == null) throw new ResponseStatusException(BAD_REQUEST, "Choisissez un logement.");
        Logement l = logements.verrouiller(d.logementId()); disponibilite(l,d.debut(),d.fin());
        if (d.message() != null && d.message().length() > 1500) throw new ResponseStatusException(BAD_REQUEST, "Message trop long.");
        DemandeLocation demande = new DemandeLocation(); demande.setDate(LocalDate.now()); demande.setDebut(d.debut()); demande.setFin(d.fin()); demande.setMessage(d.message()); demande.setStatut("En attente"); demande.setLogement(l); demande.setLocataire(u); return demande(repository.save(demande));
    }
    public DemandeDto decider(Long id, String decision) {
        DemandeLocation d = repository.findById(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Demande introuvable."));
        if (d.getLogement() == null) throw new ResponseStatusException(CONFLICT, "Logement manquant.");
        // Toutes les décisions pour un même bien partagent ce verrou transactionnel.
        Logement l = logements.verrouiller(d.getLogement().getId());
        // Recharger après le verrou pour voir une décision concurrente sur la demande.
        repository.flush();
        if (!statut(d.getStatut()).equals("En attente")) throw new ResponseStatusException(CONFLICT, "Cette demande a déjà été traitée.");
        if (decision.equals("Annulée")) {
            var u = utilisateurs.exigerRole("locataire"); if (d.getLocataire() == null || !u.getId().equals(d.getLocataire().getId())) throw new ResponseStatusException(FORBIDDEN, "Cette demande ne vous appartient pas.");
        } else { logements.verifierProprietaire(l); if (decision.equals("Acceptée")) disponibilite(l,d.getDebut(),d.getFin()); }
        d.setStatut(decision); return demande(repository.save(d));
    }
}
''')

write('Controller/DemandeLocationController.java', '''
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
''')

write('Controller/FavorisController.java', '''
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
''')

write('Controller/StatistiquesController.java', '''
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
''')
print('Backend préparé dans .integration/backend ; base et données existantes conservées.')
