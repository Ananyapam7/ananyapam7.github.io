(() => {
  'use strict';
  const normal = z => Math.exp(-z*z/2)/Math.sqrt(2*Math.PI);
  const X = z => 42+(z+4)*42;
  function plot(svg, fn, signed, shade) {
    const base = signed ? 130 : 210, scale = signed ? 270 : 410;
    const Y = y => base-y*scale;
    let html = `<path class="axis" d="M42 20V${signed?220:210}M42 ${base}H378"/>`;
    for (let z=-4;z<=4;z+=2) html+=`<text x="${X(z)}" y="240" text-anchor="middle">${z}</text>`;
    for (const y of (signed?[-.3,0,.3]:[0,.2,.4])) html+=`<text x="35" y="${Y(y)+5}" text-anchor="end">${y.toFixed(1)}</text>`;
    html+='<text x="380" y="240">z</text>';
    const path = (lo,hi) => Array.from({length:161},(_,i)=>{const z=lo+(hi-lo)*i/160;return `${i?'L':'M'}${X(z).toFixed(2)} ${Y(fn(z)).toFixed(2)}`;}).join(' ');
    if (shade) for(const [lo,hi,color] of shade) html+=`<path d="${path(lo,hi)} L${X(hi)} ${base} L${X(lo)} ${base}Z" fill="${color}" fill-opacity=".22"/>`;
    html+=`<path d="${path(-4,4)}" fill="none" stroke="${signed?'#9670ce':'#138894'}" stroke-width="2.5"/>`;
    svg.innerHTML=html;
  }
  document.querySelectorAll('[data-expectations]').forEach(el=>{
    const density=el.querySelector('[data-density]'), integrand=el.querySelector('[data-integrand]');
    const buttons=[...el.querySelectorAll('[data-question]')];
    function render(question){
      const probability=question==='probability', second=question==='second';
      plot(density,normal,false,probability?[[-1,1,'#138894']]:null);
      if(probability){
        plot(integrand,z=>Math.abs(z)<=1?normal(z):0,false,[[-1,1,'#138894']]);
      }else plot(integrand,z=>(second?z*z:z)*normal(z),!second,second?[[-4,4,'#138894']]:[[-4,0,'#d16b48'],[0,4,'#9670ce']]);
      const result=probability?'f(z) = 1 on [−1, 1], and 0 elsewhere. P(−1 ≤ z ≤ 1) ≈ 0.6827. Only density inside the interval contributes.':second?'f(z) = z². E[z²] = 1. Squaring makes contributions on both sides positive. Because the mean is zero, this is also the variance.':'f(z) = z. E[z] = 0. The negative contributions (coral) and positive contributions (violet) cancel.';
      el.querySelector('.vi-expectation-result').textContent=result;
      integrand.setAttribute('aria-label',result);
      buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.question===question)));
    }
    buttons.forEach(button=>button.addEventListener('click',()=>render(button.dataset.question)));
    render('mean');el.querySelector('.vi-expectation-controls').hidden=false;
  });
})();
