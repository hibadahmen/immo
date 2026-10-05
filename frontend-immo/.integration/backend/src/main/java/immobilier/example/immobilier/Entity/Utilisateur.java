package immobilier.example.immobilier.Entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.util.*;

@Entity
public class Utilisateur {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nom;
    private String prenom;
    private String email;
    private String motDePasse;
    private String telephone;
    private String role;
    @ElementCollection
    private Set<Long> favorisIds = new HashSet<>();
    public Long getId() { return id; }
    public void setId(Long valeur) { this.id = valeur; }
    public String getNom() { return nom; }
    public void setNom(String valeur) { this.nom = valeur; }
    public String getPrenom() { return prenom; }
    public void setPrenom(String valeur) { this.prenom = valeur; }
    public String getEmail() { return email; }
    public void setEmail(String valeur) { this.email = valeur; }
    public String getMotDePasse() { return motDePasse; }
    public void setMotDePasse(String valeur) { this.motDePasse = valeur; }
    public String getTelephone() { return telephone; }
    public void setTelephone(String valeur) { this.telephone = valeur; }
    public String getRole() { return role; }
    public void setRole(String valeur) { this.role = valeur; }
    public Set<Long> getFavorisIds() { return favorisIds; }
    public void setFavorisIds(Set<Long> valeur) { this.favorisIds = valeur; }
}
