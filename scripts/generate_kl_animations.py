"""Reproduce the forward/reverse KL GIFs with deterministic gradient descent.
Run: python scripts/generate_kl_animations.py
Dependencies: numpy, scipy, matplotlib, Pillow.
"""
from pathlib import Path
import json
import numpy as np
from scipy.special import logsumexp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

OUT=Path(__file__).resolve().parents[1]/'assets/vi'
OUT.mkdir(parents=True,exist_ok=True)
z=np.linspace(-24,24,16001)
logp=logsumexp(np.array([-.5*((z+3)/.6)**2,-.5*((z-3)/.6)**2]),axis=0)-np.log(2*.6*np.sqrt(2*np.pi))
p=np.exp(logp)
trap=getattr(np,'trapezoid',np.trapz)
plogp=trap(p*logp,z)

def objective(v,kind):
    m,l=v;s=np.exp(l)
    logq=-.5*((z-m)/s)**2-l-.5*np.log(2*np.pi)
    if kind=='forward':
        loss=plogp+.5*np.log(2*np.pi)+l+(9.36+m*m)/(2*s*s)
        grad=np.array([m/s**2,1-(9.36+m*m)/s**2])
    else:
        q=np.exp(logq);r=logq-logp
        loss=trap(q*r,z)
        grad=np.array([trap(q*(r+1)*(z-m)/s**2,z),trap(q*(r+1)*(((z-m)/s)**2-1),z)])
    return float(loss),grad


# A rotated 2D target: a two-mode mixture in u and an independent N(0,.8^2) in v.
# Rotation makes the separation diagonal without changing either KL divergence.
angle=np.deg2rad(25)
rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])

def objective2(v,kind):
    m,n,l,k=v;sy=np.exp(k)
    xloss,xgrad=objective([m,l],kind)
    if kind=='forward':
        yloss=k-np.log(.8)+(.64+n*n)/(2*sy*sy)-.5
        grad=[n/sy**2,1-(.64+n*n)/sy**2]
    else:
        yloss=np.log(.8)-k+(sy*sy+n*n)/(2*.64)-.5
        grad=[n/.64,sy*sy/.64-1]
    return xloss+yloss,np.array([xgrad[0],grad[0],xgrad[1],grad[1]])

def fit(kind):
    v=np.array([1.2,-1,np.log(1.3),np.log(1.8)])
    states=[v.copy()];losses=[objective2(v,kind)[0]]
    for _ in range(320):
        loss,g=objective2(v,kind);step=.3
        for _ in range(35):
            trial=v-step*g;value=objective2(trial,kind)[0]
            if value<=loss-1e-4*step*np.dot(g,g) and np.dot(objective2(trial,kind)[1],g)>=0:break
            step*=.5
        v=trial;states.append(v.copy());losses.append(value)
    assert np.max(np.diff(losses))<1e-9
    return np.array(states),np.array(losses)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#526277','text.color':'#243449','xtick.color':'#8b99ab','ytick.color':'#8b99ab'})
grid=np.linspace(-7,7,260);X,Y=np.meshgrid(grid,grid)
U=rotation[0,0]*X+rotation[1,0]*Y;V=rotation[0,1]*X+rotation[1,1]*Y
P=(np.exp(-.5*((U-3)/.6)**2)+np.exp(-.5*((U+3)/.6)**2))*np.exp(-.5*(V/.8)**2)/(4*np.pi*.6*.8)
levels=np.array([.06,.18,.38,.65,.88])
# Smooth display between actual iterates, with KL recomputed at every displayed state.
times=np.expm1(np.linspace(0,np.log(321),100))
metadata={}
for kind in ['forward','reverse']:
    states,losses=fit(kind);frames=[];displayloss=[]
    fig=plt.figure(figsize=(6.8,6.5),dpi=100,facecolor='#f8fafc')
    ax=fig.add_axes([.09,.22,.84,.59]);trace=fig.add_axes([.13,.075,.77,.065])
    for t in times:
        i=min(int(t),319);f=min(t-i,1);state=states[i]*(1-f)+states[i+1]*f
        m,n,l,k=state;sx,sy=np.exp([l,k]);loss=objective2(state,kind)[0];displayloss.append(loss)
        Q=np.exp(-.5*((U-m)/sx)**2-.5*((V-n)/sy)**2)/(2*np.pi*sx*sy)
        ax.clear();trace.clear();ax.set_facecolor('#f8fafc');trace.set_facecolor('#f8fafc')
        ax.contourf(X,Y,P,levels=[P.max()*.06,P.max()],colors=['#e8f1fd'],alpha=.65)
        ax.contour(X,Y,P,levels=levels*P.max(),colors=['#367ac6'],linewidths=1.65,alpha=.9)
        ax.contour(X,Y,Q,levels=levels/(2*np.pi*sx*sy),colors=['#df514b'],linewidths=2.0,linestyles='--')
        center=rotation@np.array([m,n]);ax.scatter(*center,s=30,color='#df514b',zorder=6)
        ax.set(xlim=(-7,7),ylim=(-4.8,4.8),aspect='equal',xlabel=r'$z_1$',ylabel=r'$z_2$')
        ax.set_xticks([-6,-3,0,3,6]);ax.set_yticks([-4,-2,0,2,4]);ax.grid(alpha=.1)
        for spine in ax.spines.values():spine.set_color('#dce3eb')
        trace.plot(np.arange(i+1),losses[:i+1],color='#df514b',lw=1.8)
        trace.scatter([t],[loss],s=22,color='#df514b')
        trace.set(xlim=(0,320),ylim=(0,losses.max()*1.05),ylabel='KL')
        trace.set_xticks([0,160,320]);trace.tick_params(labelsize=10)
        for spine in trace.spines.values():spine.set_color('#dce3eb')
        for artist in list(fig.texts):artist.remove()
        title='Forward KL' if kind=='forward' else 'Reverse KL'
        formula=r'$\mathrm{KL}(\pi\,\|\,q)$' if kind=='forward' else r'$\mathrm{KL}(q\,\|\,\pi)$'
        fig.text(.1,.945,title,fontsize=22,weight='bold')
        fig.text(.1,.895,'Cover both modes' if kind=='forward' else 'Concentrate on one mode',fontsize=13,color='#526277')
        fig.text(.71,.942,f'KL = {loss:.3f}',fontsize=14,color='#df514b')
        fig.text(.1,.845,'—  Target density',fontsize=12,color='#367ac6')
        fig.text(.48,.845,'– –  Gaussian approximation',fontsize=12,color='#df514b')
        fig.text(.5,.018,'Optimization step',ha='center',fontsize=10,color='#526277')
        fig.canvas.draw();frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB'))
    assert np.max(np.diff(displayloss))<1e-5
    frames[-1].save(OUT/f'{kind}-kl-final.png')
    frames[35].save(OUT/f'{kind}-kl-mid.png')
    durations=[70]*len(frames);durations[0]=800;durations[-1]=2200
    frames[0].save(OUT/f'{kind}-kl.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True)
    metadata[kind]={'final_mean_uv':states[-1,:2].tolist(),'final_sd_uv':np.exp(states[-1,2:]).tolist(),'initial_kl':float(losses[0]),'final_kl':float(losses[-1]),'steps':320,'frames':len(frames),'rotation_degrees':25}
    plt.close(fig)
assert abs(metadata['forward']['final_mean_uv'][0])<.001
assert abs(metadata['forward']['final_sd_uv'][0]-np.sqrt(9.36))<.001
assert abs(metadata['reverse']['final_mean_uv'][0]-3)<.01
assert abs(metadata['reverse']['final_sd_uv'][0]-.6)<.01
(OUT/'kl-optimization.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps(metadata,indent=2))
