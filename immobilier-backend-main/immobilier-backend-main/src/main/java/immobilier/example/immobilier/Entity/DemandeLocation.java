package immobilier.example.immobilier.Entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.util.*;

@Entity
public class DemandeLocation {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private LocalDate date;
    @Column(length = 5000)
    private String message;
    private String statut;
    @ManyToOne
    private Utilisateur locataire;
    @ManyToOne
    private Logement logement;
    private LocalDate debut;
    private LocalDate fin;
    public Long getId() { return id; }
    public void setId(Long valeur) { this.id = valeur; }
    public LocalDate getDate() { return date; }
    public void setDate(LocalDate valeur) { this.date = valeur; }
    public String getMessage() { return message; }
    public void setMessage(String valeur) { this.message = valeur; }
    public String getStatut() { return statut; }
    public void setStatut(String valeur) { this.statut = valeur; }
    public Utilisateur getLocataire() { return locataire; }
    public void setLocataire(Utilisateur valeur) { this.locataire = valeur; }
    public Logement getLogement() { return logement; }
    public void setLogement(Logement valeur) { this.logement = valeur; }
    public LocalDate getDebut() { return debut; }
    public void setDebut(LocalDate valeur) { this.debut = valeur; }
    public LocalDate getFin() { return fin; }
    public void setFin(LocalDate valeur) { this.fin = valeur; }
}
