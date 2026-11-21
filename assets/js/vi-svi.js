/* Conjugate Gaussian SVI: natural-parameter updates, not interpolated targets. */
(() => {
  'use strict';
  const observations = [0.2,1.1,2.8,3.5,1.7,4.2,2.1,0.8,3.1,2.6,4.6,1.3];
  const N = observations.length;
  const optimum = observations.reduce((a,b)=>a+b,0)/(N+2);
  const local = (x,m) => (x+m)/2;
  const moments = p => ({m:-p[0]/(2*p[1]),v:-1/(2*p[1])});
  const gap = p => {
    const {m,v}=moments(p);
    return -.5*((1+N/2)*(m-optimum)**2+(N+1)*v-1-Math.log((N+1)*v));
  };
  function update(p,batch,t) {
    const {m}=moments(p), eta=(t+2)**(-.7);
    const proposal=[N/batch.length*batch.reduce((a,i)=>a+local(observations[i],m),0),-(N+1)/2];
    return p.map((v,i)=>(1-eta)*v+eta*proposal[i]);
  }
  function random(seed) { return () => {seed=(Math.imul(1664525,seed)+1013904223)>>>0; return seed/4294967296;}; }
  function sample(rng) {
    const indices=observations.map((_,i)=>i);
    for(let i=N-1;i>0;i--){const j=Math.floor(rng()*(i+1));[indices[i],indices[j]]=[indices[j],indices[i]];}
    return indices.slice(0,3);
  }
  if(typeof module!=='undefined') module.exports={observations,optimum,local,moments,gap,update,random,sample};
  if(typeof document==='undefined') return;
  const NS='http://www.w3.org/2000/svg';
  const mathCache=new Map();
  function mathNode(tex) {
    if(!window.MathJax?.tex2chtml) return null;
    if(!mathCache.has(tex)) mathCache.set(tex,window.MathJax.tex2chtml(tex,{display:false}));
    return mathCache.get(tex).cloneNode(true);
  }
  function add(svg,tag,attrs,text) {
    const e=document.createElementNS(NS,tag);
    Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));
    if(text!==undefined)e.textContent=text;
    svg.append(e);return e;
  }
  document.querySelectorAll('[data-svi]').forEach(root=>{
    const network=root.querySelector('[data-svi-network]'),density=root.querySelector('[data-svi-density]'),elbo=root.querySelector('[data-svi-elbo]');
    const status=root.querySelector('[data-svi-status]'),values=root.querySelector('[data-svi-values]');
    const play=root.querySelector('[data-svi-play]'),step=root.querySelector('[data-svi-step]');
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    let p,locals,batch,phase,t,history,rng,timer=null,frame=null;
    const teal='#20a5a5',blue='#709de5',orange='#e39a55',muted='#8795a6';
    function text(svg,x,y,s,color='currentColor',size=13) {add(svg,'text',{x,y,fill:color,'font-size':size,'text-anchor':'middle'},s);}
    function math(svg,x,y,tex,color='currentColor',size=13,width=100) {
      const node=mathNode(tex);
      if(!node){text(svg,x,y,tex,color,size);return;}
      const box=add(svg,'foreignObject',{x:x-width/2,y:y-size-3,width,height:size*2.8,overflow:'visible'});
      const content=document.createElementNS('http://www.w3.org/1999/xhtml','div');
      content.style.cssText='text-align:center;white-space:nowrap;color:'+color+';font-size:'+size+'px;line-height:1.2';
      content.append(node);box.append(content);
    }
    function curve(svg,m,v,color,dash=false) {
      const points=Array.from({length:181},(_,i)=>{
        const x=-3+9*i/180,y=Math.exp(-.5*(x-m)**2/v)/Math.sqrt(2*Math.PI*v);
        return (35+270*i/180)+','+(162-y*86);
      });
      add(svg,'polyline',{points:points.join(' '),fill:'none',stroke:color,'stroke-width':2.8,'stroke-dasharray':dash?'6 4':'none'});
    }
    function render(display=p,progress=1) {
      const {m,v}=moments(display);
      network.replaceChildren();density.replaceChildren();elbo.replaceChildren();
      root.querySelectorAll('.vi-svi-stages li').forEach((li,i)=>li.classList.toggle('active',i===phase));
      for(let i=0;i<N;i++){
        const x=48+(i%6)*116,y=i<6?205:302,selected=batch.includes(i),color=selected?orange:muted;
        add(network,'line',{x1:340,y1:68,x2:x,y2:y-25,stroke:color,opacity:selected?.65:.12,'stroke-width':selected?2:1});
        if(selected&&phase===2){
          const f=progress;add(network,'circle',{cx:x+(340-x)*f,cy:y-25+(68-y+25)*f,r:5,fill:orange});
        }
        add(network,'circle',{cx:x,cy:y-20,r:23,fill:selected?'rgba(227,154,85,.13)':'transparent',stroke:color,'stroke-width':selected?2:1});
        math(network,x,y-16,'q_{'+(i+1)+'}',color,16);
        math(network,x-20,y+18,'x_{'+(i+1)+'}=',muted,12,55);
        text(network,x+19,y+18,observations[i].toFixed(1),muted,12);
        math(network,x-20,y+35,'m_{'+(i+1)+'}=',color,12,55);
        text(network,x+19,y+35,locals[i].toFixed(2),color,12);
      }
      add(network,'rect',{x:235,y:14,width:210,height:64,rx:20,fill:'var(--global-bg-color,#fff)',stroke:teal,'stroke-width':2});
      math(network,340,39,'q_{\\phi_g}(z_g)',teal,18,200);
      text(network,340,62,'mean '+m.toFixed(2)+' · sd '+Math.sqrt(v).toFixed(2),teal);
      const formulas=[
        '\\mathcal B\\subset\\{1,\\ldots,12\\},\\quad|\\mathcal B|=3',
        'q_i^\\star=\\mathcal N\\!\\left((x_i+m_g)/2,\\,1/2\\right),\\quad i\\in\\mathcal B',
        '\\widehat\\phi_g=\\alpha_0+4\\sum_{i\\in\\mathcal B}\\bar T_i',
        '\\phi_g^{(t+1)}=(1-\\eta_t)\\phi_g^{(t)}+\\eta_t\\widehat\\phi_g'
      ];
      math(network,340,125,formulas[Math.max(0,phase)],phase===2?orange:'currentColor',16,650);
      math(density,170,19,'q_{\\phi_g}(z_g)\\quad\\text{and}\\quad q_{\\phi_g^\\star}(z_g)', 'currentColor',13,330);
      add(density,'line',{x1:35,y1:162,x2:305,y2:162,stroke:muted});
      curve(density,optimum,1/(N+1),blue,true);curve(density,m,v,teal);
      [-3,0,3,6].forEach(x=>text(density,35+(x+3)*30,180,String(x),muted,11));
      math(density,170,198,'z_g',muted,12);
      math(elbo,170,19,'\\mathcal L_{\\mathrm{prof}}(\\phi_g)-\\mathcal L_{\\mathrm{prof}}(\\phi_g^\\star)','currentColor',13,330);
      const floor=Math.floor(history[0]/5)*5, sx=i=>40+260*i/Math.max(12,history.length-1),sy=g=>40+120*g/floor;
      add(elbo,'line',{x1:40,y1:40,x2:305,y2:40,stroke:blue,'stroke-dasharray':'5 4'});
      text(elbo,22,44,'0',blue,11);text(elbo,22,164,String(floor),muted,11);
      add(elbo,'polyline',{points:history.map((g,i)=>sx(i)+','+sy(g)).join(' '),fill:'none',stroke:teal,'stroke-width':2});
      add(elbo,'circle',{cx:sx(history.length-1),cy:sy(history.at(-1)),r:4,fill:teal});
      text(elbo,170,190,'Global updates: '+t,muted,12);
      values.textContent='Global mean '+m.toFixed(3)+' · variance '+v.toFixed(3)+' · ELBO gap '+gap(display).toFixed(3)+' nats';
    }
    function animate(from,to) {
      if(reduced.matches){render(to);return;}
      const start=performance.now();
      function tick(now){
        const f=Math.min(1,(now-start)/650),ease=f*f*(3-2*f);
        render(from.map((v,i)=>v+(to[i]-v)*ease),ease);
        if(f<1)frame=requestAnimationFrame(tick);else frame=null;
      }
      frame=requestAnimationFrame(tick);
    }
    function advance(){
      if(frame){cancelAnimationFrame(frame);frame=null;}
      phase=(phase+1)%4;
      if(phase===0){batch=sample(rng);status.textContent='Select: observations '+batch.map(i=>i+1).join(', ')+'. Their local fits may be stale.';}
      if(phase===1){const {m}=moments(p);batch.forEach(i=>locals[i]=local(observations[i],m));status.replaceChildren(document.createTextNode('Fit locals: '));const equation=mathNode('m_i=(x_i+m_g)/2,\\quad v_i=1/2');status.append(equation||document.createTextNode('average the observation and global mean'),document.createTextNode('. The global distribution stays fixed.'));}
      if(phase===2){status.textContent='Send statistics: multiply the three fitted local messages by 4 to estimate the full-data sum, then add the prior.';animate(p,p);return;}
      if(phase===3){const before=p;p=update(p,batch,t);t++;history.push(gap(p));status.textContent='Global update '+t+': blend with step size '+((t+1)**(-.7)).toFixed(3)+'. '+(history.at(-1)<history.at(-2)?'This noisy step lowered the profiled ELBO.':'The profiled ELBO improved.');animate(before,p);return;}
      render();
    }
    function pause(){if(timer)clearInterval(timer);timer=null;play.textContent='Play';}
    function reset(){pause();if(frame)cancelAnimationFrame(frame);frame=null;p=[-1.5,-.5];locals=observations.map(()=>0);batch=[];phase=-1;t=0;history=[gap(p)];rng=random(7283);status.textContent='Start with a broad global belief far from the best fit. Press Next stage to select a minibatch.';render();}
    step.addEventListener('click',()=>{pause();advance();});
    play.addEventListener('click',()=>{if(timer){pause();return;}play.textContent='Pause';advance();timer=setInterval(advance,1500);});
    root.querySelector('[data-svi-reset]').addEventListener('click',reset);
    root.closest('.vi-paper-theory')?.addEventListener('toggle',e=>{if(!e.target.open)pause();});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
    reduced.addEventListener('change',()=>{pause();if(frame)cancelAnimationFrame(frame);frame=null;render();});
    root.querySelector('[data-svi-live]').hidden=false;reset();
    if(window.MathJax?.startup?.promise)window.MathJax.startup.promise.then(()=>render());
    else window.addEventListener('load',()=>window.MathJax?.startup?.promise?.then(()=>render()),{once:true});
  });
})();
