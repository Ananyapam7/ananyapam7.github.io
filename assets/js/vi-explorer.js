(() => {
  'use strict';
  const normal = (z,m,s) => Math.exp(-0.5*((z-m)/s)**2)/(s*Math.sqrt(2*Math.PI));
  const colors = ['#138894','#9670ce','#d16b48'];
  document.querySelectorAll('[data-vi]').forEach(el => {
    const kind=el.dataset.vi, svg=el.querySelector('svg'), inputs=[...el.querySelectorAll('input')];
    const play=el.querySelector('[data-play]'), original=inputs.map(i=>i.value), playLabel=play.textContent;
    let frame=0, running=false;
    function stop(){cancelAnimationFrame(frame);running=false;play.textContent=playLabel;play.setAttribute('aria-pressed','false');}
    function render(){
      const a=+inputs[0].value, b=inputs[1]?+inputs[1].value:0;
      inputs.forEach(i=>i.parentElement.querySelector('output').textContent=(+i.value).toFixed(2));
      let curves,labels,ymax,readout;
      if(kind==='update'){
        const variance=1/(1+1/.64), mean=variance*a/.64;
        curves=[z=>normal(z,0,1),z=>normal(a,z,.8),z=>normal(z,mean,Math.sqrt(variance))];
        labels=['Prior','Likelihood','Posterior'];ymax=.85;
        readout=`Posterior mean = ${mean.toFixed(2)} · posterior standard deviation = ${Math.sqrt(variance).toFixed(2)} · evidence p(x) = ${normal(a,0,Math.sqrt(1.64)).toFixed(3)}`;
      }else if(kind==='scale'){
        const target=z=>.4*normal(z,-1.8,.7)+.6*normal(z,1.5,.9);
        curves=[target,z=>a*target(z)];labels=['Normalized π','Unnormalized cπ'];ymax=1.5;
        readout=`Area Z = ${a.toFixed(2)} · γ(z) / Z = cπ(z) / c = π(z) · normalized area = 1`;
      }else{
        const kl=.5*((a-1)**2+b*b-1-Math.log(b*b));
        curves=[z=>normal(z,1,1),z=>normal(z,a,b)];labels=['Target π','Approximation q'];ymax=1.4;
        readout=`KL = ${kl.toFixed(3)} · ELBO = ${(2-kl).toFixed(3)} · log Z = 2.000 · ELBO + KL = 2.000`;
        const gap = el.querySelector('[data-gap]');
        if(gap){
          const y=30+kl*17;
          gap.innerHTML=`<title>ELBO ${(2-kl).toFixed(3)}, KL gap ${kl.toFixed(3)}, fixed log Z 2</title>
            <path class="axis" d="M58 25V205"/>
            <text x="48" y="35" text-anchor="end">2</text><text x="48" y="69" text-anchor="end">0</text><text x="48" y="171" text-anchor="end">−6</text>
            <rect x="80" y="30" width="440" height="${kl*17}" fill="#9670ce" fill-opacity=".17"/>
            <path d="M80 30H520" stroke="#138894" stroke-width="2.5" stroke-dasharray="7 5"/>
            <path d="M80 ${y}H520" stroke="#9670ce" stroke-width="3"/>
            <text x="540" y="30">log Z = 2</text>
            <text x="540" y="60">ELBO ${(2-kl).toFixed(3)}</text>
            <text x="540" y="90">KL ${kl.toFixed(3)}</text>
            <text x="80" y="223">${kl<.0005?'The gap is closed: q equals the target.':'Raise the violet line; shrink the shaded gap.'}</text>`;
        }

      }
      let content='<title>Probability density over z</title><path class="axis" d="M48 18V250H700"/>';
      for(let x=-5;x<=5;x++)content+=`<text x="${48+(x+5)*65.2}" y="272" text-anchor="middle">${x}</text>`;
      for(let j=1;j<=3;j++){const y=j*ymax/3;content+=`<text x="40" y="${254-y/ymax*220}" text-anchor="end">${y.toFixed(1)}</text>`;}
      content+='<text x="690" y="288">z</text>';
      curves.forEach((fn,i)=>{
        let d='';for(let n=0;n<=400;n++){const z=-5+n/40;d+=`${n?'L':'M'}${(48+n/400*652).toFixed(2)},${(250-fn(z)/ymax*220).toFixed(2)}`;}
        content+=`<path d="${d}" fill="none" stroke="${colors[i]}" stroke-width="3" ${((kind==='fit'&&i===0)||(kind!=='fit'&&i===1))?'stroke-dasharray="7 5"':''}/>`;
      });
      svg.innerHTML=content;
      el.querySelector('.vi-legend').innerHTML=labels.map((l,i)=>`<span style="--line:${colors[i]}">${l}</span>`).join('');
      el.querySelector('.vi-readout').textContent=readout;
    }
    inputs.forEach(i=>i.addEventListener('input',()=>{stop();render();}));
    el.querySelector('[data-reset]').addEventListener('click',()=>{stop();inputs.forEach((i,n)=>i.value=original[n]);render();});
    play.addEventListener('click',()=>{
      if(running){stop();return;}
      const start=performance.now(), initial=inputs.map(i=>+i.value);
      const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
      running=true;play.textContent='Pause';play.setAttribute('aria-pressed','true');
      function tick(now){
        const t=reduced?1:Math.min(1,(now-start)/3500), ease=t*t*(3-2*t);
        if(kind==='fit'){inputs[0].value=initial[0]+(1-initial[0])*ease;inputs[1].value=initial[1]+(1-initial[1])*ease;}
        else inputs[0].value=initial[0]+((kind==='update'?-initial[0]:(initial[0]>2.5?.5:5))-initial[0])*ease;
        render();if(t<1)frame=requestAnimationFrame(tick);else stop();
      }
      frame=requestAnimationFrame(tick);
    });
    document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
    render();el.querySelector('.vi-fallback').hidden=true;el.querySelector('.vi-fallback').style.display='none';el.querySelector('.vi-live').hidden=false;
  });
})();
