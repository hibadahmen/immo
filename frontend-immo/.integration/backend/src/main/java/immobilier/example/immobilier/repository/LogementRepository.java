package immobilier.example.immobilier.repository;
import immobilier.example.immobilier.Entity.Logement;
import java.util.Optional;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
public interface LogementRepository extends JpaRepository<Logement, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select l from Logement l where l.id = :id")
    Optional<Logement> verrouiller(@Param("id") Long id);
}
