(() => {
  'use strict';
  document.querySelectorAll('[data-kl-comparison]').forEach(el => {
    const images=[...el.querySelectorAll('img[data-animation]')];
    const actions=el.querySelector('.vi-kl-actions');
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    const finish=()=>images.forEach(img=>{img.src=img.dataset.poster;});
    const replay=()=>{if(!reduced.matches)images.forEach(img=>{img.src=img.dataset.animation+'?replay='+Date.now();});};
    el.querySelector('[data-kl-pause]').addEventListener('click',finish);
    el.querySelector('[data-kl-replay]').addEventListener('click',replay);
    const preference=()=>{actions.hidden=reduced.matches;if(reduced.matches)finish();else replay();};
    reduced.addEventListener('change',preference);
    actions.hidden=reduced.matches;
  });
})();
