package immobilier.example.immobilier.repository;

import immobilier.example.immobilier.Entity.DemandeLocation;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DemandeLocationRepository
        extends JpaRepository<DemandeLocation, Long> {
}
