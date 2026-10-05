"""Vérification locale : crée des comptes et un bien identifiés comme tests, sans suppression."""
import json, secrets, time
from pathlib import Path
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError
from http.cookiejar import CookieJar

base = 'http://localhost:4200/api'
stamp = str(int(time.time()))
password = secrets.token_urlsafe(16)

class Client:
    def __init__(self):
        self.cookies = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookies))
        self.token = None
    def request(self, method, path, body=None, expected=200):
        headers = {'Content-Type': 'application/json'}
        if method != 'GET' and self.token: headers['X-XSRF-TOKEN'] = self.token
        req = Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=15) as res:
                assert res.status == expected, (path, res.status)
                raw = res.read()
                return json.loads(raw) if raw else None
        except HTTPError as e:
            if e.code == expected: return json.loads(e.read())
            raise RuntimeError(f'{method} {path} : {e.code} : {e.read().decode()}') from e
    def register(self, role):
        self.token = self.request('GET', '/auth/csrf')['token']
        return self.request('POST', '/auth/inscription', {'nom':'Intégration','prenom':'Test','email':f'{role}.{stamp}.{secrets.token_hex(3)}@integration.invalid','telephone':'22123456','role':role,'motDePasse':password})

owner = Client(); tenant = Client(); stranger = Client()
u = owner.register('proprietaire'); tenant.register('locataire'); stranger.register('proprietaire')
assert owner.request('GET', '/auth/moi')['id'] == u['id']
property_data = {'titre':f'[TEST INTÉGRATION {stamp}] Appartement','description':'Bien créé pour vérifier la connexion Angular et Spring Boot.','type':'Appartement','ville':'Tunis','adresse':'Adresse de test','prix':900,'superficie':75,'pieces':3,'equipements':['Wi-Fi'],'images':['/images/logement-placeholder.svg'],'disponibleDebut':'2027-01-01','disponibleFin':'2028-12-31','archive':False}
home = owner.request('POST', '/logements', property_data)
hid = home['id']; property_data['id'] = hid
assert owner.request('GET',f'/logements/{hid}')['titre'] == property_data['titre']
property_data['prix'] = 950
owner.request('PUT',f'/logements/{hid}',property_data)
assert owner.request('GET',f'/logements/{hid}')['prix'] == 950
assert any(l['id'] == hid for l in tenant.request('GET','/logements?ville=Tunis&type=Appartement&max=1000'))
stranger.request('PUT',f'/logements/{hid}',property_data,expected=403)
tenant.request('POST','/logements',property_data,expected=403)
tenant.request('PUT',f'/favoris/{hid}',{})
assert hid in tenant.request('GET','/favoris')
def demande(debut,fin): return tenant.request('POST','/demandes',{'logementId':hid,'debut':debut,'fin':fin,'message':'Test de persistance'})
tenant.request('POST','/demandes',{'logementId':hid,'debut':'2027-06-01','fin':'2027-05-01'},expected=400)
first = demande('2027-02-01','2027-05-01'); overlap = demande('2027-03-01','2027-06-01'); cancelled = demande('2027-08-01','2027-09-01')
tenant.request('PUT',f"/demandes/{first['id']}/accepter",{},expected=403)
owner.request('PUT',f"/demandes/{first['id']}/accepter",{})
owner.request('PUT',f"/demandes/{overlap['id']}/accepter",{},expected=409)
owner.request('PUT',f"/demandes/{overlap['id']}/refuser",{})
tenant.request('PUT',f"/demandes/{cancelled['id']}/annuler",{})
assert any(r['id'] == first['id'] and r['statut'] == 'Acceptée' for r in tenant.request('GET','/demandes'))
profile = {k:u[k] for k in ['nom','prenom','email','telephone']}; profile['prenom'] = 'TestModifié'
owner.request('PUT','/utilisateurs/moi',profile)
assert owner.request('GET','/auth/moi')['prenom'] == 'TestModifié'
owner.request('PATCH',f'/logements/{hid}/archivage',{'archive':True})
assert not any(l['id'] == hid for l in tenant.request('GET','/logements'))
owner.request('PATCH',f'/logements/{hid}/archivage',{'archive':False})
assert any(l['id'] == hid for l in tenant.request('GET','/logements'))
# Nouvelle connexion : les informations sont relues depuis PostgreSQL.
owner.request('POST','/auth/deconnexion',{})
owner.request('GET','/auth/moi',expected=401)
owner.token = owner.request('GET','/auth/csrf')['token']
owner.request('POST','/auth/connexion',{'email':u['email'],'motDePasse':password})
assert owner.request('GET',f'/logements/{hid}')['prix'] == 950
assert owner.request('GET','/auth/moi')['prenom'] == 'TestModifié'
tenant.request('DELETE',f'/favoris/{hid}')
assert hid not in tenant.request('GET','/favoris')
owner.request('PATCH',f'/logements/{hid}/archivage',{'archive':True})
Path('.integration/api-result.json').write_text(json.dumps({'logementId':hid,'demandeAccepteeId':first['id'],'comptesTests':3,'resultat':'OK','bienTestArchive':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('OK : inscription, session, publication, modification, recherche, favoris, profil, archivage, demandes, rôles et chevauchements. Le bien de test est archivé ; aucune donnée supprimée.')
