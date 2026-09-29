const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+__dirname+'/index.html?render');await p.evaluate(()=>window.ready);
const c=await p.evaluate(()=>({cards:CH_CARDS.map(c=>c.t0),slams:SLAMS.map(s=>s[0]),nodes:Object.values(NODES).map(n=>n.t0),runs:RUNS.map(r=>({t0:r.t0,br:r.br})),seg:SEG}));
require('fs').writeFileSync('cues.json',JSON.stringify(c,null,1));console.log(JSON.stringify(c).slice(0,300));await b.close()})();
