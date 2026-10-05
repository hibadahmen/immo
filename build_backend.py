from pathlib import Path
root = Path('immobilier-backend-main/immobilier-backend-main')
src = root / 'src/main/java/immobilier/example/immobilier'
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip()+'\n', encoding='utf-8')
write(root/'pom.xml', '''
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
<modelVersion>4.0.0</modelVersion>
<parent><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-parent</artifactId><version>3.5.11</version><relativePath/></parent>
<groupId>immobilier.example</groupId><artifactId>immobilier</artifactId><version>1.0.0</version>
<properties><java.version>17</java.version></properties>
<dependencies>
<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
<dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>runtime</scope></dependency>
<dependency><groupId>com.mysql</groupId><artifactId>mysql-connector-j</artifactId><scope>runtime</scope></dependency>
<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
<dependency><groupId>org.springframework.security</groupId><artifactId>spring-security-test</artifactId><scope>test</scope></dependency>
</dependencies>
<build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
</project>''')
write(root/'src/main/resources/application.properties', '''
spring.application.name=DarLoc
server.port=8080
spring.datasource.url=${DB_URL:jdbc:h2:file:./data/darloc}
spring.datasource.username=${DB_USERNAME:sa}
spring.datasource.password=${DB_PASSWORD:}
spring.jpa.hibernate.ddl-auto=update
spring.jpa.open-in-view=false
server.servlet.session.cookie.http-only=true
server.servlet.session.cookie.same-site=lax
server.servlet.session.timeout=8h
spring.servlet.multipart.max-file-size=5MB
spring.servlet.multipart.max-request-size=25MB
server.error.include-message=never
app.upload-dir=./uploads
''')
entities = {
'Utilisateur': '''
    public String nom;
    public String prenom;
    @Column(unique=true, nullable=false) public String email;
    @com.fasterxml.jackson.annotation.JsonIgnore public String motDePasse;
    public String telephone;
    public String role;
''',
'Logement': '''
    public String titre;
    @Column(length=6000) public String description;
    public java.math.BigDecimal prix;
    public String type;
    public String adresse;
    public String ville;
    public double superficie;
    public int nombrePieces;
    public boolean archive;
    public java.time.LocalDate disponibleDu;
    public java.time.LocalDate disponibleAu;
    @ElementCollection(fetch=FetchType.EAGER) public java.util.List<String> photos = new java.util.ArrayList<>();
    @ElementCollection(fetch=FetchType.EAGER) public java.util.Set<String> equipements = new java.util.LinkedHashSet<>();
    @ManyToOne(optional=false) public Utilisateur proprietaire;
''',
'DemandeLocation': '''
    public java.time.LocalDate debut;
    public java.time.LocalDate fin;
    @Column(length=2000) public String message;
    @Column(length=2000) public String reponse;
    public String statut = "EN_ATTENTE";
    public java.time.Instant creeLe = java.time.Instant.now();
    @ManyToOne(optional=false) public Utilisateur locataire;
    @ManyToOne(optional=false) public Logement logement;
'''}
for name, fields in entities.items():
    write(src/f'Entity/{name}.java', f'''package immobilier.example.immobilier.Entity;
import jakarta.persistence.*;
@Entity
public class {name} {{
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) public Long id;
    public Long getId() {{ return id; }}
    public void setId(Long id) {{ this.id=id; }}
{fields}
}}''')
write(src/'repository/UtilisateurRepository.java', '''package immobilier.example.immobilier.repository;
import immobilier.example.immobilier.Entity.Utilisateur;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
public interface UtilisateurRepository extends JpaRepository<Utilisateur,Long> {
    Optional<Utilisateur> findByEmail(String email);
}
''')
write(src/'repository/LogementRepository.java', '''package immobilier.example.immobilier.repository;
import immobilier.example.immobilier.Entity.Logement;
import org.springframework.data.jpa.repository.*;
import jakarta.persistence.LockModeType;
import java.util.*;
public interface LogementRepository extends JpaRepository<Logement,Long> {
    List<Logement> findByProprietaireIdOrderByIdDesc(Long id);
    List<Logement> findByArchiveFalseOrderByIdDesc();
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select l from Logement l where l.id = :id")
    Optional<Logement> lockById(Long id);
}''')
write(src/'repository/DemandeLocationRepository.java', '''package immobilier.example.immobilier.repository;
import immobilier.example.immobilier.Entity.DemandeLocation;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;
import java.time.LocalDate;
public interface DemandeLocationRepository extends JpaRepository<DemandeLocation,Long> {
    List<DemandeLocation> findByLocataireIdOrderByIdDesc(Long id);
    List<DemandeLocation> findByLogementProprietaireIdOrderByIdDesc(Long id);
    List<DemandeLocation> findByLogementIdAndStatut(Long id,String statut);
    boolean existsByLogementIdAndStatutAndDebutLessThanEqualAndFinGreaterThanEqual(Long id,String statut,LocalDate fin,LocalDate debut);
}''')
write(src/'config/SecurityConfig.java', '''package immobilier.example.immobilier.config;
import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
@Configuration
public class SecurityConfig {
    @Bean PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }
    @Bean SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http.authorizeHttpRequests(a -> a.anyRequest().permitAll())
            .csrf(c -> c.csrfTokenRepository(new org.springframework.security.web.csrf.HttpSessionCsrfTokenRepository()))
            .formLogin(f -> f.disable()).httpBasic(b -> b.disable()).logout(l -> l.disable())
            .exceptionHandling(e -> e.accessDeniedHandler((req,res,ex) -> {
                res.setStatus(403); res.setContentType("application/json;charset=UTF-8");
                res.getWriter().write("{\\"message\\":\\"Session expirée ou jeton de sécurité absent. Rechargez la page.\\"}");
            })).build();
    }
}''')
write(src/'web/ApiExceptionHandler.java', '''package immobilier.example.immobilier.web;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import java.util.Map;
@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(ResponseStatusException.class)
    ResponseEntity<?> known(ResponseStatusException e) { return ResponseEntity.status(e.getStatusCode()).body(Map.of("message",e.getReason()==null ? "Requête invalide" : e.getReason())); }
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<?> validation(MethodArgumentNotValidException e) { return ResponseEntity.badRequest().body(Map.of("message", "Vérifiez les champs du formulaire : " + e.getBindingResult().getFieldErrors().stream().map(f -> f.getField()+" "+f.getDefaultMessage()).findFirst().orElse("données invalides"))); }
    @ExceptionHandler({org.springframework.http.converter.HttpMessageNotReadableException.class,org.springframework.web.method.annotation.MethodArgumentTypeMismatchException.class})
    ResponseEntity<?> malformed(Exception e) { return ResponseEntity.badRequest().body(Map.of("message","Format de données invalide.")); }
    @ExceptionHandler(org.springframework.dao.DataIntegrityViolationException.class)
    ResponseEntity<?> conflict(Exception e) { return ResponseEntity.status(409).body(Map.of("message","Ces données existent déjà ou sont utilisées.")); }
    @ExceptionHandler(org.springframework.web.multipart.MaxUploadSizeExceededException.class)
    ResponseEntity<?> upload(Exception e) { return ResponseEntity.badRequest().body(Map.of("message","Une photo ne peut pas dépasser 5 Mo.")); }
}''')
write(src/'web/Inputs.java', '''package immobilier.example.immobilier.web;
import jakarta.validation.constraints.*;
import java.time.LocalDate;
import java.math.BigDecimal;
import java.util.*;
public class Inputs {
    public record Register(@NotBlank @Size(max=80) String nom,@NotBlank @Size(max=80) String prenom,@NotBlank @Email @Size(max=180) String email,@NotBlank @Size(max=30) String telephone,@NotBlank @Size(min=8,max=72) String motDePasse,@NotBlank String role) {}
    public record Login(@NotBlank @Email String email,@NotBlank @Size(max=72) String motDePasse) {}
    public record Profile(@NotBlank @Size(max=80) String nom,@NotBlank @Size(max=80) String prenom,@NotBlank @Email @Size(max=180) String email,@NotBlank @Size(max=30) String telephone) {}
    public record Password(@NotBlank String ancien,@NotBlank @Size(min=8,max=72) String nouveau) {}
    public record Property(@NotBlank @Size(max=160) String titre,@NotBlank @Size(max=6000) String description,@NotNull @DecimalMin("1") BigDecimal prix,@NotBlank String type,@NotBlank @Size(max=250) String adresse,@NotBlank @Size(max=100) String ville,@Positive double superficie,@Min(1) @Max(50) int nombrePieces,@NotNull LocalDate disponibleDu,@NotNull LocalDate disponibleAu,@NotNull @Size(min=1,max=12) List<@NotBlank String> photos,@NotNull @Size(max=30) Set<@Size(max=80) String> equipements) {}
    public record Booking(@NotNull Long logementId,@NotNull LocalDate debut,@NotNull LocalDate fin,@Size(max=2000) String message) {}
    public record Decision(@NotBlank String statut,@Size(max=2000) String reponse) {}
}''')
write(src/'service/UtilisateurService.java', '''package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.Utilisateur;
import immobilier.example.immobilier.repository.UtilisateurRepository;
import immobilier.example.immobilier.web.Inputs.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Service;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
@Service
public class UtilisateurService {
    private final UtilisateurRepository users;
    private final PasswordEncoder encoder;
    public UtilisateurService(UtilisateurRepository users,PasswordEncoder encoder) { this.users=users; this.encoder=encoder; }
    public Utilisateur current(HttpServletRequest request) {
        var session=request.getSession(false);
        if(session==null || !(session.getAttribute("userId") instanceof Long)) throw new ResponseStatusException(UNAUTHORIZED,"Connectez-vous pour continuer.");
        return users.findById((Long)session.getAttribute("userId")).orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED,"Compte introuvable."));
    }
    public Utilisateur require(HttpServletRequest request,String role) {
        var user=current(request);
        if(!role.equals(user.role)) throw new ResponseStatusException(FORBIDDEN,"Cette action est réservée au rôle "+role+".");
        return user;
    }
    public Utilisateur register(Register input,HttpServletRequest request) {
        if(!java.util.Set.of("LOCATAIRE","PROPRIETAIRE").contains(input.role())) throw new ResponseStatusException(BAD_REQUEST,"Rôle invalide.");
        String email=input.email().trim().toLowerCase(java.util.Locale.ROOT);
        if(users.findByEmail(email).isPresent()) throw new ResponseStatusException(CONFLICT,"Cette adresse email est déjà utilisée.");
        var u=new Utilisateur(); u.nom=input.nom().trim(); u.prenom=input.prenom().trim(); u.email=email; u.telephone=input.telephone(); u.role=input.role(); u.motDePasse=encoder.encode(input.motDePasse());
        u=users.save(u); establish(request,u); return u;
    }
    public Utilisateur login(Login input,HttpServletRequest request) {
        var u=users.findByEmail(input.email().trim().toLowerCase(java.util.Locale.ROOT)).orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED,"Email ou mot de passe incorrect."));
        if(!encoder.matches(input.motDePasse(),u.motDePasse)) throw new ResponseStatusException(UNAUTHORIZED,"Email ou mot de passe incorrect.");
        establish(request,u); return u;
    }
    private void establish(HttpServletRequest request,Utilisateur u) { request.getSession(); request.changeSessionId(); request.getSession().setAttribute("userId",u.id); }
    public Utilisateur update(Profile input,HttpServletRequest request) {
        var u=current(request); String email=input.email().trim().toLowerCase(java.util.Locale.ROOT);
        if(users.findByEmail(email).filter(other -> !other.id.equals(u.id)).isPresent()) throw new ResponseStatusException(CONFLICT,"Cette adresse email est déjà utilisée.");
        u.nom=input.nom().trim(); u.prenom=input.prenom().trim(); u.email=email; u.telephone=input.telephone(); return users.save(u);
    }
    public void password(Password input,HttpServletRequest request) {
        var u=current(request);
        if(!encoder.matches(input.ancien(),u.motDePasse)) throw new ResponseStatusException(BAD_REQUEST,"Le mot de passe actuel est incorrect.");
        u.motDePasse=encoder.encode(input.nouveau()); users.save(u); request.changeSessionId();
    }
}''')
write(src/'Controller/UtilisateurController.java', '''package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.UtilisateurService;
import immobilier.example.immobilier.web.Inputs.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.web.csrf.CsrfToken;
import java.util.Map;
@RestController @RequestMapping("/api")
public class UtilisateurController {
    private final UtilisateurService users;
    public UtilisateurController(UtilisateurService users) { this.users=users; }
    @GetMapping("/auth/csrf") public Object csrf(CsrfToken token) { return Map.of("token",token.getToken(),"headerName",token.getHeaderName()); }
    @PostMapping("/auth/inscription") public Object register(@Valid @RequestBody Register input,HttpServletRequest request) { return users.register(input,request); }
    @PostMapping("/auth/connexion") public Object login(@Valid @RequestBody Login input,HttpServletRequest request) { return users.login(input,request); }
    @PostMapping("/auth/deconnexion") public void logout(HttpServletRequest request) { if(request.getSession(false)!=null) request.getSession().invalidate(); }
    @GetMapping("/profil") public Object profile(HttpServletRequest request) { return users.current(request); }
    @PutMapping("/profil") public Object update(@Valid @RequestBody Profile input,HttpServletRequest request) { return users.update(input,request); }
    @PutMapping("/profil/mot-de-passe") public void password(@Valid @RequestBody Password input,HttpServletRequest request) { users.password(input,request); }
}''')
write(src/'service/LogementService.java', '''package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.*;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.web.Inputs.Property;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.time.LocalDate;
import java.math.BigDecimal;
import java.util.*;
@Service
public class LogementService {
    private final LogementRepository homes;
    private final DemandeLocationRepository bookings;
    public LogementService(LogementRepository homes,DemandeLocationRepository bookings) { this.homes=homes; this.bookings=bookings; }
    public Logement get(Long id) { return homes.findById(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND,"Logement introuvable.")); }
    public Logement locked(Long id) { return homes.lockById(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND,"Logement introuvable.")); }
    public void own(Logement home,Utilisateur user) { if(!home.proprietaire.id.equals(user.id)) throw new ResponseStatusException(FORBIDDEN,"Ce bien appartient à un autre propriétaire."); }
    public List<Logement> mine(Utilisateur user) { return homes.findByProprietaireIdOrderByIdDesc(user.id); }
    public void dates(LocalDate debut,LocalDate fin) { if(debut==null || fin==null || debut.isBefore(LocalDate.now()) || fin.isBefore(debut)) throw new ResponseStatusException(BAD_REQUEST,"Choisissez des dates valides à partir d’aujourd’hui."); }
    public boolean available(Logement h,LocalDate debut,LocalDate fin) {
        return !h.archive && !debut.isBefore(h.disponibleDu) && !fin.isAfter(h.disponibleAu) && !bookings.existsByLogementIdAndStatutAndDebutLessThanEqualAndFinGreaterThanEqual(h.id,"ACCEPTEE",fin,debut);
    }
    public List<Logement> search(String ville,BigDecimal min,BigDecimal max,String type,Integer pieces,LocalDate debut,LocalDate fin) {
        if(debut!=null || fin!=null) dates(debut,fin);
        if(min!=null && max!=null && min.compareTo(max)>0) throw new ResponseStatusException(BAD_REQUEST,"Le prix minimum doit être inférieur au maximum.");
        return homes.findByArchiveFalseOrderByIdDesc().stream().filter(h -> ville==null || h.ville.toLowerCase(Locale.ROOT).contains(ville.toLowerCase(Locale.ROOT)))
            .filter(h -> min==null || h.prix.compareTo(min)>=0).filter(h -> max==null || h.prix.compareTo(max)<=0)
            .filter(h -> type==null || type.isBlank() || type.equals(h.type)).filter(h -> pieces==null || h.nombrePieces>=pieces)
            .filter(h -> debut==null || available(h,debut,fin)).toList();
    }
    @Transactional public Logement save(Long id,Property input,Utilisateur user) {
        if(input.disponibleAu().isBefore(input.disponibleDu())) throw new ResponseStatusException(BAD_REQUEST,"La fin de disponibilité doit suivre le début.");
        if(!Set.of("Appartement","Maison","Villa","Studio").contains(input.type())) throw new ResponseStatusException(BAD_REQUEST,"Type de logement invalide.");
        for(String photo: input.photos()) if(!photo.matches("/api/photos/[a-f0-9-]+\\\\.(jpg|png|webp)")) throw new ResponseStatusException(BAD_REQUEST,"Importez les photos avant de publier.");
        var h=id==null ? new Logement() : locked(id);
        if(id!=null) {
            own(h,user);
            for(var b:bookings.findByLogementIdAndStatut(id,"ACCEPTEE")) if(!b.fin.isBefore(LocalDate.now()) && (b.debut.isBefore(input.disponibleDu()) || b.fin.isAfter(input.disponibleAu()))) throw new ResponseStatusException(CONFLICT,"Les disponibilités doivent couvrir les réservations acceptées.");
        }
        h.titre=input.titre().trim(); h.description=input.description().trim(); h.prix=input.prix(); h.type=input.type(); h.adresse=input.adresse().trim(); h.ville=input.ville().trim(); h.superficie=input.superficie(); h.nombrePieces=input.nombrePieces(); h.disponibleDu=input.disponibleDu(); h.disponibleAu=input.disponibleAu(); h.photos=new ArrayList<>(input.photos()); h.equipements=new LinkedHashSet<>(input.equipements()); h.proprietaire=user;
        return homes.save(h);
    }
    @Transactional public void archive(Long id,Utilisateur user) { var h=locked(id); own(h,user); h.archive=true; homes.save(h); }
}''')
write(src/'Controller/LogementController.java', '''package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.*;
import immobilier.example.immobilier.web.Inputs.Property;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.time.LocalDate;
import java.math.BigDecimal;
@RestController @RequestMapping("/api/logements")
public class LogementController {
    private final LogementService homes; private final UtilisateurService users;
    public LogementController(LogementService homes,UtilisateurService users) { this.homes=homes; this.users=users; }
    @GetMapping public Object list(@RequestParam(required=false) String ville,@RequestParam(required=false) BigDecimal min,@RequestParam(required=false) BigDecimal max,@RequestParam(required=false) String type,@RequestParam(required=false) Integer pieces,@RequestParam(required=false) LocalDate debut,@RequestParam(required=false) LocalDate fin) { return homes.search(ville,min,max,type,pieces,debut,fin).stream().map(immobilier.example.immobilier.web.Views::property).toList(); }
    @GetMapping("/miens") public Object mine(HttpServletRequest r) { return homes.mine(users.require(r,"PROPRIETAIRE")).stream().map(immobilier.example.immobilier.web.Views::property).toList(); }
    @GetMapping("/{id}") public Object get(@PathVariable Long id,HttpServletRequest r) { var h=homes.get(id); if(h.archive) { try { homes.own(h,users.current(r)); } catch(ResponseStatusException e) { throw new ResponseStatusException(NOT_FOUND,"Logement indisponible."); } } return immobilier.example.immobilier.web.Views.property(h); }
    @PostMapping public Object add(@Valid @RequestBody Property input,HttpServletRequest r) { return immobilier.example.immobilier.web.Views.property(homes.save(null,input,users.require(r,"PROPRIETAIRE"))); }
    @PutMapping("/{id}") public Object edit(@PathVariable Long id,@Valid @RequestBody Property input,HttpServletRequest r) { return immobilier.example.immobilier.web.Views.property(homes.save(id,input,users.require(r,"PROPRIETAIRE"))); }
    @DeleteMapping("/{id}") public void archive(@PathVariable Long id,HttpServletRequest r) { homes.archive(id,users.require(r,"PROPRIETAIRE")); }
}''')
write(src/'web/Views.java', '''package immobilier.example.immobilier.web;
import immobilier.example.immobilier.Entity.*;
import java.util.*;
public class Views {
    public static Map<String,Object> property(Logement h) {
        var m=new LinkedHashMap<String,Object>();
        m.put("id",h.id); m.put("titre",h.titre); m.put("description",h.description); m.put("prix",h.prix); m.put("type",h.type); m.put("adresse",h.adresse); m.put("ville",h.ville); m.put("superficie",h.superficie); m.put("nombrePieces",h.nombrePieces); m.put("archive",h.archive); m.put("disponibleDu",h.disponibleDu); m.put("disponibleAu",h.disponibleAu); m.put("photos",h.photos); m.put("equipements",h.equipements);
        m.put("proprietaire",Map.of("id",h.proprietaire.id,"prenom",h.proprietaire.prenom,"nom",h.proprietaire.nom)); return m;
    }
    public static Map<String,Object> booking(DemandeLocation b) {
        var m=new LinkedHashMap<String,Object>(); m.put("id",b.id); m.put("debut",b.debut); m.put("fin",b.fin); m.put("message",b.message); m.put("reponse",b.reponse); m.put("statut",b.statut); m.put("creeLe",b.creeLe); m.put("logement",property(b.logement)); m.put("locataire",b.locataire); return m;
    }
}''')
write(src/'service/DemandeLocationService.java', '''package immobilier.example.immobilier.service;
import immobilier.example.immobilier.Entity.*;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.web.Inputs.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import static org.springframework.http.HttpStatus.*;
import java.util.*;
@Service
public class DemandeLocationService {
    private final DemandeLocationRepository bookings; private final LogementService homes;
    public DemandeLocationService(DemandeLocationRepository bookings,LogementService homes) { this.bookings=bookings; this.homes=homes; }
    public List<DemandeLocation> list(Utilisateur u) { return "PROPRIETAIRE".equals(u.role) ? bookings.findByLogementProprietaireIdOrderByIdDesc(u.id) : bookings.findByLocataireIdOrderByIdDesc(u.id); }
    public DemandeLocation get(Long id,Utilisateur u) {
        var b=bookings.findById(id).orElseThrow(() -> new ResponseStatusException(NOT_FOUND,"Demande introuvable."));
        if(!b.locataire.id.equals(u.id) && !b.logement.proprietaire.id.equals(u.id)) throw new ResponseStatusException(FORBIDDEN,"Cette demande ne vous appartient pas."); return b;
    }
    @Transactional public DemandeLocation create(Booking input,Utilisateur u) {
        homes.dates(input.debut(),input.fin()); var h=homes.locked(input.logementId());
        if(!homes.available(h,input.debut(),input.fin())) throw new ResponseStatusException(CONFLICT,"Ce logement n’est pas disponible pour cette période.");
        var b=new DemandeLocation(); b.logement=h; b.locataire=u; b.debut=input.debut(); b.fin=input.fin(); b.message=input.message(); return bookings.save(b);
    }
    @Transactional public DemandeLocation decide(Long id,Decision input,Utilisateur u) {
        // Always lock the property first; competing approvals/cancellations serialize on the same row.
        var initial=get(id,u); homes.locked(initial.logement.id);
        var b=bookings.findById(id).orElseThrow();
        // Reload the booking after the lock, avoiding a stale managed status.
        entityManager.refresh(b);
        if(!"EN_ATTENTE".equals(b.statut)) throw new ResponseStatusException(CONFLICT,"Cette demande a déjà été traitée.");
        if("ANNULEE".equals(input.statut())) {
            if(!"LOCATAIRE".equals(u.role) || !b.locataire.id.equals(u.id)) throw new ResponseStatusException(FORBIDDEN,"Seul le locataire peut annuler sa demande.");
        } else {
            if(!"PROPRIETAIRE".equals(u.role)) throw new ResponseStatusException(FORBIDDEN,"Action réservée au propriétaire.");
            homes.own(b.logement,u);
            if(!Set.of("ACCEPTEE","REFUSEE").contains(input.statut())) throw new ResponseStatusException(BAD_REQUEST,"Statut invalide.");
            if("ACCEPTEE".equals(input.statut())) { homes.dates(b.debut,b.fin); if(!homes.available(b.logement,b.debut,b.fin)) throw new ResponseStatusException(CONFLICT,"Cette période est indisponible ou chevauche une réservation acceptée."); }
            b.reponse=input.reponse();
        }
        b.statut=input.statut(); return bookings.save(b);
    }
    @jakarta.persistence.PersistenceContext private jakarta.persistence.EntityManager entityManager;
}''')
write(src/'Controller/DemandeLocationController.java', '''package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.*;
import immobilier.example.immobilier.web.Inputs.*;
import immobilier.example.immobilier.web.Views;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/demandes")
public class DemandeLocationController {
    private final DemandeLocationService bookings; private final UtilisateurService users;
    public DemandeLocationController(DemandeLocationService bookings,UtilisateurService users) { this.bookings=bookings; this.users=users; }
    @GetMapping public Object list(HttpServletRequest r) { return bookings.list(users.current(r)).stream().map(Views::booking).toList(); }
    @GetMapping("/{id}") public Object get(@PathVariable Long id,HttpServletRequest r) { return Views.booking(bookings.get(id,users.current(r))); }
    @PostMapping public Object add(@Valid @RequestBody Booking input,HttpServletRequest r) { return Views.booking(bookings.create(input,users.require(r,"LOCATAIRE"))); }
    @PutMapping("/{id}") public Object decide(@PathVariable Long id,@Valid @RequestBody Decision input,HttpServletRequest r) { return Views.booking(bookings.decide(id,input,users.current(r))); }
}''')
write(src/'Controller/PhotoController.java', '''package immobilier.example.immobilier.Controller;
import immobilier.example.immobilier.service.UtilisateurService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;
import org.springframework.core.io.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;
import java.nio.file.*;
import java.util.*;
import javax.imageio.ImageIO;
@RestController @RequestMapping("/api/photos")
public class PhotoController {
    private final Path directory; private final UtilisateurService users;
    public PhotoController(@Value("${app.upload-dir}") String directory,UtilisateurService users) { this.directory=Path.of(directory).toAbsolutePath().normalize(); this.users=users; }
    @PostMapping public Object upload(@RequestParam("file") MultipartFile file,HttpServletRequest r) throws java.io.IOException {
        users.require(r,"PROPRIETAIRE");
        if(file.isEmpty() || file.getSize()>5*1024*1024) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Photo vide ou supérieure à 5 Mo.");
        try(var stream=ImageIO.createImageInputStream(file.getInputStream())) {
            var readers=ImageIO.getImageReaders(stream);
            if(!readers.hasNext()) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Choisissez une image JPEG ou PNG.");
            var reader=readers.next();
            try { reader.setInput(stream); if((long)reader.getWidth(0)*reader.getHeight(0)>25000000) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Image trop grande (25 mégapixels maximum)."); }
            finally { reader.dispose(); }
        }
        var image=ImageIO.read(file.getInputStream());
        if(image==null) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Image invalide.");
        Files.createDirectories(directory); String name=UUID.randomUUID()+".png";
        ImageIO.write(image,"png",directory.resolve(name).toFile());
        return Map.of("url","/api/photos/"+name);
    }
    @GetMapping("/{name}") public ResponseEntity<Resource> get(@PathVariable String name) {
        if(!name.matches("[a-f0-9-]+\\\\.(png|jpg|webp)")) throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        Path path=directory.resolve(name).normalize();
        if(!path.startsWith(directory) || !Files.isRegularFile(path)) throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        return ResponseEntity.ok().contentType(name.endsWith(".png") ? MediaType.IMAGE_PNG : MediaType.IMAGE_JPEG).cacheControl(CacheControl.maxAge(java.time.Duration.ofDays(7))).body(new FileSystemResource(path));
    }
}''')
