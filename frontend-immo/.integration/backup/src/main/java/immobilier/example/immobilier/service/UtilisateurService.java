package immobilier.example.immobilier.service;

import immobilier.example.immobilier.Entity.Utilisateur;
import immobilier.example.immobilier.repository.UtilisateurRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class UtilisateurService {

    private final UtilisateurRepository repository;

    public UtilisateurService(UtilisateurRepository repository) {
        this.repository = repository;
    }

    public List<Utilisateur> getAll() {
        return repository.findAll();
    }

    public Optional<Utilisateur> getById(Long id) {
        return repository.findById(id);
    }

    public Utilisateur ajouter(Utilisateur u) {
        return repository.save(u);
    }

    public Utilisateur modifier(Long id, Utilisateur u) {
        u.setId(id);
        return repository.save(u);
    }

    public void supprimer(Long id) {
        repository.deleteById(id);
    }
}



