package immobilier.example.immobilier.service;

import immobilier.example.immobilier.Entity.DemandeLocation;
import immobilier.example.immobilier.repository.DemandeLocationRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class DemandeLocationService {

    private final DemandeLocationRepository repository;

    public DemandeLocationService(
            DemandeLocationRepository repository) {
        this.repository = repository;
    }

    public List<DemandeLocation> getAll() {
        return repository.findAll();
    }

    public Optional<DemandeLocation> getById(Long id) {
        return repository.findById(id);
    }

    public DemandeLocation ajouter(DemandeLocation d) {
        return repository.save(d);
    }

    public DemandeLocation modifier(Long id, DemandeLocation d) {
        d.setId(id);
        return repository.save(d);
    }

    public void supprimer(Long id) {
        repository.deleteById(id);
    }
}
