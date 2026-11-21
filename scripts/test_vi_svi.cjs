const assert=require('node:assert/strict');
const {observations:x,optimum,local,moments,gap,update,random,sample}=require('../assets/js/vi-svi.js');
const close=(a,b,tol=1e-9)=>assert.ok(Math.abs(a-b)<tol,a+' != '+b);
const N=x.length,p=[-1.5,-.5],eta=2**(-.7);
// Average every possible minibatch: it must equal the full-data natural step.
const mean=[0,0];let count=0;
for(let i=0;i<N;i++)for(let j=i+1;j<N;j++)for(let k=j+1;k<N;k++){
 const result=update(p,[i,j,k],0);result.forEach((v,r)=>mean[r]+=v);count++;
}
const full=[x.reduce((s,v)=>s+local(v,moments(p).m),0),-(N+1)/2];
mean.forEach((v,i)=>close(v/count,(1-eta)*p[i]+eta*full[i]));
// Independent Gaussian ELBO calculation verifies the profiled diagnostic.
function elbo(param){
 const {m,v}=moments(param),lv=.5;
 let e=-.5*(m*m+v)+.5*Math.log(v);
 x.forEach(xi=>{const mi=local(xi,m);e+=-.5*((mi-m)**2+lv+v)-.5*((xi-mi)**2+lv)+.5*Math.log(lv);});
 return e;
}
const best=[optimum*(N+1),-(N+1)/2];
for(const param of [p,best,[4,-3],[0,-1]])close(gap(param),elbo(param)-elbo(best));
close(gap(best),0);
let current=p,rng=random(7283),dips=0,last=gap(p);
for(let t=0;t<500;t++){
 const batch=sample(rng);assert.equal(new Set(batch).size,3);
 current=update(current,batch,t);
 assert.ok(moments(current).v>0);
 const next=gap(current);assert.ok(Number.isFinite(next)&&next<=1e-10);
 if(next<last)dips++;last=next;
}
assert.ok(last>gap(p)+20);assert.ok(dips>0);
console.log('Passed: unbiased minibatches, independently calculated ELBO, stable updates and genuine stochastic dips.');
