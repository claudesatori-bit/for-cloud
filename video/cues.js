const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+__dirname+'/index.html?render');await p.evaluate(()=>window.ready);
const c=await p.evaluate(()=>({nodes:NA.map(n=>n.t0),chips:CHIPS.map(c=>c.t0),pillars:PIL.map(p=>p.t0)}));
require('fs').writeFileSync('cues.json',JSON.stringify(c));console.log(Object.keys(c));await b.close()})();
