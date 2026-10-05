import { TestBed } from '@angular/core/testing';
import { FiltresLogements } from './filtres-logements';

describe('Formulaire de recherche', () => {
  it('empêche une recherche avec un budget minimum supérieur au maximum', async () => {
    await TestBed.configureTestingModule({imports: [FiltresLogements]}).compileComponents();
    const fixture = TestBed.createComponent(FiltresLogements);
    fixture.componentInstance.criteres = {ville: '', type: '', min: 900, max: 500, pieces: null};
    const recherche = spyOn(fixture.componentInstance.recherche, 'emit');
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.nativeElement.querySelector('form').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
    fixture.detectChanges();
    expect(recherche).not.toHaveBeenCalled();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('budget minimum');
  });
});
