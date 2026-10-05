package immobilier.example.immobilier;
import immobilier.example.immobilier.Entity.*;
import immobilier.example.immobilier.service.*;
import immobilier.example.immobilier.repository.*;
import immobilier.example.immobilier.dto.ApiDtos.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.server.ResponseStatusException;
import java.time.LocalDate;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ReglesLocationTests {
    @Mock DemandeLocationRepository repository;
    @Mock LogementService logements;
    @Mock UtilisateurService utilisateurs;
    @Mock jakarta.persistence.EntityManager entityManager;
    @InjectMocks DemandeLocationService service;
    Logement bien;
    @BeforeEach void preparer() {
        bien = new Logement(); bien.setId(1L); bien.setDisponibleDebut(LocalDate.parse("2027-01-01")); bien.setDisponibleFin(LocalDate.parse("2028-01-01"));
    }
    @Test void refuseDatesInversees() {
        when(utilisateurs.exigerRole("locataire")).thenReturn(new Utilisateur()); when(logements.verrouiller(1L)).thenReturn(bien);
        assertThrows(ResponseStatusException.class, () -> service.ajouter(new NouvelleDemande(1L,LocalDate.parse("2027-04-01"),LocalDate.parse("2027-03-01"),"")));
        verify(repository,never()).save(any());
    }
    @Test void refuseChevauchementAccepte() {
        when(utilisateurs.exigerRole("locataire")).thenReturn(new Utilisateur()); when(logements.verrouiller(1L)).thenReturn(bien);
        DemandeLocation acceptee = new DemandeLocation(); acceptee.setLogement(bien); acceptee.setStatut("Acceptée"); acceptee.setDebut(LocalDate.parse("2027-02-01")); acceptee.setFin(LocalDate.parse("2027-05-01"));
        when(repository.findAll()).thenReturn(List.of(acceptee));
        assertThrows(ResponseStatusException.class, () -> service.ajouter(new NouvelleDemande(1L,LocalDate.parse("2027-03-01"),LocalDate.parse("2027-06-01"),"")));
        verify(repository,never()).save(any());
    }
    @Test void autorisePeriodesConsecutives() {
        assertFalse(DemandeLocationService.chevauche(LocalDate.parse("2027-05-01"),LocalDate.parse("2027-06-01"),LocalDate.parse("2027-02-01"),LocalDate.parse("2027-05-01")));
    }
    @Test void refuseProprietaireQuiDemandeUneLocation() {
        when(utilisateurs.exigerRole("locataire")).thenThrow(new ResponseStatusException(org.springframework.http.HttpStatus.FORBIDDEN));
        assertThrows(ResponseStatusException.class, () -> service.ajouter(new NouvelleDemande(1L,LocalDate.parse("2027-02-01"),LocalDate.parse("2027-03-01"),"")));
        verify(repository,never()).save(any());
    }
}
