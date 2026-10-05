const fs = require('fs');
const crypto = require('crypto');
const delay = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const pages = await (await fetch('http://127.0.0.1:9223/json')).json();
  const ws = new WebSocket(pages.find(p => p.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r, {once:true}));
  let id = 0; const pending = new Map(); const errors = [];
  ws.addEventListener('message', e => {
    const m = JSON.parse(e.data);
    if (m.id) { pending.get(m.id)?.(m); pending.delete(m.id); }
    if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  });
  const send = (method, params={}) => new Promise(r => { const n = ++id; pending.set(n,r); ws.send(JSON.stringify({id:n,method,params})); });
  const evaluate = async expression => {
    const result = await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if (result.result.exceptionDetails) throw new Error(result.result.exceptionDetails.text);
    return result.result.result.value;
  };
  await send('Runtime.enable');
  await send('Page.navigate',{url:'http://localhost:4200/inscription'});
  await delay(2500);
  const email = `navigateur.${Date.now()}@integration.invalid`;
  const values = {prenom:'TestNavigateur',nom:'Intégration',email,telephone:'22123456',motDePasse:crypto.randomBytes(12).toString('hex')};
  await evaluate(`(() => { const values=${JSON.stringify(values)}; for (const [name,value] of Object.entries(values)) { const input=document.querySelector('[name="'+name+'"]'); if (!input) throw new Error('Champ absent: '+name); input.value=value; input.dispatchEvent(new Event('input',{bubbles:true})); } document.querySelector('form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})); })()`);
  await delay(2500);
  const before = await evaluate('JSON.stringify({path:location.pathname,texte:document.body.innerText})');
  if (JSON.parse(before).path !== '/reservations') throw new Error('Inscription Angular échouée : ' + before);
  await send('Page.reload'); await delay(2000);
  const after = JSON.parse(await evaluate('JSON.stringify({path:location.pathname,profil:document.querySelector(".sidebar-person")?.innerText})'));
  if (after.path !== '/reservations' || !after.profil?.includes('TestNavigateur')) throw new Error('Session non restaurée : ' + JSON.stringify(after));
  const screenshot = await send('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync('.integration/session-browser.png',Buffer.from(screenshot.result.data,'base64'));
  await send('Browser.close'); ws.close();
  if (errors.length) throw new Error(errors.join('\n'));
  console.log('OK : formulaire Angular réel, inscription avec CSRF, navigation et session conservée après rechargement. Aucune exception JavaScript.');
})().catch(e => { console.error(e.message); process.exit(1); });
