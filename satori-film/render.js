// Renders frames [a,b) of the film to an H.264 segment via ffmpeg.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { spawn } = require('child_process');
const [,, a, b, out, fps='60'] = process.argv;
const FF = process.env.FFMPEG;
(async () => {
  const br = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await br.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.error('pageerror', e.message));
  await p.goto('file://' + __dirname + '/index.html?render');
  await p.evaluate(() => window.ready);
  const ff = spawn(FF, ['-loglevel','error','-y','-f','image2pipe','-framerate',fps,'-c:v','png','-i','-',
    '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-r',fps, out], { stdio: ['pipe','inherit','inherit'] });
  const t0 = Date.now();
  for (let f = +a; f < +b; f++) {
    await p.evaluate(t => render(t), f / +fps);
    const buf = await p.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 300 === 0) console.log(out, f, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await br.close();
})();
