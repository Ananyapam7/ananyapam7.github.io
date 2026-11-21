const assert = require("node:assert/strict");
const {initial,elbo,update} = require("../assets/js/vi-cavi.js");
let checks=0;
for(const rho of [0,.2,.8,.95]){
 let s=initial();
 for(let k=0;k<300;k++){
  const j=k%2,t=update(s,rho,j),delta=elbo(t,rho)-elbo(s,rho);
  assert.deepEqual([t.m[1-j],t.v[1-j]],[s.m[1-j],s.v[1-j]]);
  assert(delta>=-1e-11);
  const kl=.5*(s.v[j]/t.v[j]+(s.m[j]-t.m[j])**2/t.v[j]-1+Math.log(t.v[j]/s.v[j]));
  assert(Math.abs(delta-kl)<1e-10);
  let old=elbo(s,rho);
  for(let a=1;a<=20;a++){
   const f=a/20,u={m:s.m.map((v,i)=>v+f*(t.m[i]-v)),v:s.v.map((v,i)=>v+f*(t.v[i]-v))};
   const e=elbo(u,rho);assert(e>=old-1e-10);old=e;checks++;
  }
  s=t;
 }
 assert(Math.abs(elbo(s,rho)-.5*Math.log(1-rho*rho))<1e-10);
}
console.log("Passed KL-gain identity, fixed-factor checks, "+checks+" interpolated frames, and optimum checks.");
