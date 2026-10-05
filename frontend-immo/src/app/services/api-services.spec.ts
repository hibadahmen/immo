import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ReservationService } from './reservation.service';
import { AuthService } from './auth.service';
import { LogementService } from './logement.service';

describe('Services reliés à Spring Boot', () => {
  let http: HttpTestingController;
  beforeEach(() => { TestBed.configureTestingModule({providers:[provideHttpClient(),provideHttpClientTesting()]}); http = TestBed.inject(HttpTestingController); });
  afterEach(() => http.verify());
  it('envoie une demande sans inventer le locataire ni le statut', async () => {
    const service = TestBed.inject(ReservationService);
    const operation = service.demander(12,'2027-01-01','2027-03-01','Bonjour');
    const req = http.expectOne('/api/demandes');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({logementId:12,debut:'2027-01-01',fin:'2027-03-01',message:'Bonjour'});
    expect(service.reservations.length).toBe(0);
    req.flush({id:32,logementId:12,locataireId:7,locataireNom:'Nour',debut:'2027-01-01',fin:'2027-03-01',message:'Bonjour',statut:'En attente'});
    await operation;
    expect(service.reservations[0].id).toBe(32);
  });
  it('conserve le statut si le backend refuse un chevauchement', async () => {
    const service = TestBed.inject(ReservationService);
    service.reservations = [{id:1,logementId:2,locataireId:3,locataireNom:'Test',debut:'2027-01-01',fin:'2027-02-01',message:'',statut:'En attente'}];
    const operation = service.decider(1,true);
    const verification = expectAsync(operation).toBeRejected();
    http.expectOne('/api/demandes/1/accepter').flush({message:'Chevauchement'},{status:409,statusText:'Conflict'});
    await verification;
    expect(service.reservations[0].statut).toBe('En attente');
  });
  it('restaure le profil depuis la session serveur après rechargement', async () => {
    const auth = TestBed.inject(AuthService);
    const operation = auth.initialiser();
    http.expectOne('/api/auth/csrf').flush({token:'test'});
    await Promise.resolve();
    http.expectOne('/api/auth/moi').flush({id:3,nom:'Test',prenom:'Nour',email:'nour@test.tn',telephone:'22123456',role:'locataire'});
    await operation;
    expect(auth.utilisateur?.id).toBe(3);
  });
  it('envoie les critères de recherche au serveur', async () => {
    const service = TestBed.inject(LogementService);
    const operation = service.charger({ville:'Tunis',type:'Studio',max:700});
    const req = http.expectOne(r => r.url === '/api/logements');
    expect(req.request.params.get('ville')).toBe('Tunis');
    expect(req.request.params.get('max')).toBe('700');
    req.flush([]); await operation;
    expect(service.logements).toEqual([]);
  });
});
