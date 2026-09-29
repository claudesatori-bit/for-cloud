// Exports every cue time from the film to cues.json so the score lands on the picture.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage();
await p.goto('file://'+__dirname+'/index.html?render');await p.evaluate(()=>window.ready);
const c=await p.evaluate(()=>{const ticks=[];let last=count(0);for(let f=0;f<240;f++){const n=count(f/60);if(n!==last){ticks.push(f/60);last=n}}
  return{count:ticks,chips:CHIPS.map((_,i)=>1.35+i*.26),slams:SLAMS.map(s=>s[0]),cards:CARDS.map(c=>c[0]),cfg:CFG.map(v=>v+.14),phases:PH_T,
    tickets:TK_T,resolved:TK_R,msgs:MSG.map(m=>({t0:m.t0,user:m.who==='user',n:m.s.length})),locks:LOCK_T,stamp:STAMP,
    panes:PANES.map(p=>p.e),paneOut:PANE_OUT,cities:CITIES.map(c=>c.t0+.7),svc:SVC.map(s=>s[0])}});
require('fs').writeFileSync('cues.json',JSON.stringify(c,null,0));console.log(Object.keys(c).join(' '));await b.close()})();
