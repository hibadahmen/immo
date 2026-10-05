package immobilier.example.immobilier.Entity;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.util.*;

@Entity
public class Logement {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String titre;
    @Column(length = 5000)
    private String description;
    private double prix;
    private String adresse;
    private String ville;
    private double superficie;
    private int nombreChambres;
    private String statut;
    @ManyToOne
    private Utilisateur proprietaire;
    private String type;
    private Integer nombrePieces;
    private LocalDate disponibleDebut;
    private LocalDate disponibleFin;
    @ElementCollection
    @OrderColumn
    private List<String> images = new ArrayList<>();
    @ElementCollection
    @OrderColumn
    private List<String> equipements = new ArrayList<>();
    public Long getId() { return id; }
    public void setId(Long valeur) { this.id = valeur; }
    public String getTitre() { return titre; }
    public void setTitre(String valeur) { this.titre = valeur; }
    public String getDescription() { return description; }
    public void setDescription(String valeur) { this.description = valeur; }
    public double getPrix() { return prix; }
    public void setPrix(double valeur) { this.prix = valeur; }
    public String getAdresse() { return adresse; }
    public void setAdresse(String valeur) { this.adresse = valeur; }
    public String getVille() { return ville; }
    public void setVille(String valeur) { this.ville = valeur; }
    public double getSuperficie() { return superficie; }
    public void setSuperficie(double valeur) { this.superficie = valeur; }
    public int getNombreChambres() { return nombreChambres; }
    public void setNombreChambres(int valeur) { this.nombreChambres = valeur; }
    public String getStatut() { return statut; }
    public void setStatut(String valeur) { this.statut = valeur; }
    public Utilisateur getProprietaire() { return proprietaire; }
    public void setProprietaire(Utilisateur valeur) { this.proprietaire = valeur; }
    public String getType() { return type; }
    public void setType(String valeur) { this.type = valeur; }
    public Integer getNombrePieces() { return nombrePieces; }
    public void setNombrePieces(Integer valeur) { this.nombrePieces = valeur; }
    public LocalDate getDisponibleDebut() { return disponibleDebut; }
    public void setDisponibleDebut(LocalDate valeur) { this.disponibleDebut = valeur; }
    public LocalDate getDisponibleFin() { return disponibleFin; }
    public void setDisponibleFin(LocalDate valeur) { this.disponibleFin = valeur; }
    public List<String> getImages() { return images; }
    public void setImages(List<String> valeur) { this.images = valeur; }
    public List<String> getEquipements() { return equipements; }
    public void setEquipements(List<String> valeur) { this.equipements = valeur; }
}
