package immobilier.example.immobilier.repository;

import immobilier.example.immobilier.Entity.Utilisateur;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UtilisateurRepository
        extends JpaRepository<Utilisateur, Long> {
}
