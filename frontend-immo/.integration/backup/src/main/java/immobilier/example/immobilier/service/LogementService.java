package immobilier.example.immobilier.service;

import immobilier.example.immobilier.Entity.Logement;
import immobilier.example.immobilier.repository.LogementRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class LogementService {

    private final LogementRepository repository;

    public LogementService(LogementRepository repository) {
        this.repository = repository;
    }

    public List<Logement> getAll() {
        return repository.findAll();
    }

    public Optional<Logement> getById(Long id) {
        return repository.findById(id);
    }

    public Logement ajouter(Logement l) {
        return repository.save(l);
    }

    public Logement modifier(Long id, Logement l) {
        l.setId(id);
        return repository.save(l);
    }

    public void supprimer(Long id) {
        repository.deleteById(id);
    }
}
