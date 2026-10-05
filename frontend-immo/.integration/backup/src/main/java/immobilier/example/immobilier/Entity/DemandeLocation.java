package immobilier.example.immobilier.Entity;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.ManyToOne;
import java.time.LocalDate;

@Entity
public class DemandeLocation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private LocalDate date;
    private String message;
    private String statut; 

    @ManyToOne
    private Utilisateur locataire;

    @ManyToOne
    private Logement logement;
    public Long getId() {
    return id;
}

public void setId(Long id) {
    this.id = id;
}

}
