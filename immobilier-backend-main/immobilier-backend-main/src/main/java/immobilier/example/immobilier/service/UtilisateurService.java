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
    private String email(String valeur) { String email = texte(valeur, 254).toLowerCase(); if (!email.matches("[^\\s@]+@[^\\s@]+\\.[^\\s@]+")) throw new ResponseStatusException(BAD_REQUEST, "Email invalide."); return email; }
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
