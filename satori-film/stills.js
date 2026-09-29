const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async()=>{
  const b=await chromium.launch({args:['--allow-file-access-from-files','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:1920,height:1080}});
  const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('file://'+__dirname+'/index.html?render');
  await p.evaluate(()=>window.ready);
  const ts=process.argv.slice(2).map(Number);
  const out=process.env.OUT||'stills';require('fs').mkdirSync(out,{recursive:true});
  for(const t of ts){const s=Date.now();await p.evaluate(t=>render(t),t);await p.screenshot({path:`${out}/t${t.toFixed(2).padStart(5,"0")}.jpg`,type:'jpeg',quality:80});console.log(t,Date.now()-s,'ms')}
  console.log('errors:',errs.slice(0,10));await b.close();
})();
