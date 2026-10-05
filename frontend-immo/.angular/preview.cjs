const fs = require('fs');
(async () => {
  const targets = await (await fetch('http://127.0.0.1:9223/json')).json();
  const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r, {once:true}));
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', e => {
    const m = JSON.parse(e.data);
    if (m.id) { pending.get(m.id)?.(m); pending.delete(m.id); }
  });
  const send = (method, params = {}) => new Promise(r => {
    const n = ++id; pending.set(n, r); ws.send(JSON.stringify({id:n, method, params}));
  });
  await send('Emulation.setDeviceMetricsOverride', {width:390, height:1000, deviceScaleFactor:1, mobile:true});
  await send('Page.navigate', {url:'http://127.0.0.1:4200/'});
  await new Promise(r => setTimeout(r, 3500));
  const info = await send('Runtime.evaluate', {expression: 'JSON.stringify({viewport:innerWidth,document:document.documentElement.scrollWidth,menu:getComputedStyle(document.querySelector(".menu-toggle")).display})', returnByValue:true});
  console.log(info.result.result.value);
  const shot = await send('Page.captureScreenshot', {format:'png'});
  fs.writeFileSync('preview-mobile.png', Buffer.from(shot.result.data, 'base64'));
  await send('Browser.close');
  ws.close();
})().catch(e => { console.error(e); process.exit(1); });
