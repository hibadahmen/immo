package immobilier.example.immobilier.repository;

import immobilier.example.immobilier.Entity.Logement;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LogementRepository
        extends JpaRepository<Logement, Long> {
}