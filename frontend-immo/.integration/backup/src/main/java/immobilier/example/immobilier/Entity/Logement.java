package immobilier.example.immobilier.Entity;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.ManyToOne;


@Entity
public class Logement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String titre;
    private String description;
    private double prix;
    private String adresse;
    private String ville;
    private double superficie;
    private int nombreChambres;
    private String statut; 

    @ManyToOne
    private Utilisateur proprietaire;
    public Long getId() {
       return id;
    }

    public void setId(Long id) {
       this.id = id;
    }

}