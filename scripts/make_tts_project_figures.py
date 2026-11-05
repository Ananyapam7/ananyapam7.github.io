"""Plot the stored project audio on a shared spectrogram scale.

Sources: skit-ai/woc-tts-enhancement/docs/audio (NOIZEUS sp15, station, 5 dB).
This does not rerun filters or generate benchmark scores.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/img/tts/spectrogram-comparison.png'
AUDIO = ROOT / 'assets/audio/tts'


def main():
    files = [('Clean reference','sp15.wav'), ('Noisy input · station noise, 5 dB','sp15_station_sn5.wav'),
             ('Wiener-filtered output','wiener_filtered_sp15_station_sn5.wav'),
             ('Log-MMSE-filtered output','mmse_log_filtered_sp15_station_sn5.wav')]
    spectra = []
    for title,name in files:
        rate, samples = wavfile.read(AUDIO/name)
        assert rate == 8000 and samples.dtype == np.int16 and samples.ndim == 1
        signal = samples.astype(float) / 32768.0
        f,t,z = stft(signal,fs=rate,nperseg=256,noverlap=192,boundary=None,padded=False)
        spectra.append((title,f,t,np.abs(z)))
    reference = max(s[3].max() for s in spectra)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':'#33465b',
                         'axes.labelcolor':'#33465b','xtick.color':'#33465b','ytick.color':'#33465b'})
    fig,axes=plt.subplots(2,2,figsize=(11.2,7.1),dpi=180,sharex=True,sharey=True)
    for ax,(title,f,t,magnitude) in zip(axes.flat,spectra):
        db=20*np.log10(np.maximum(magnitude,reference*1e-5)/reference)
        mesh=ax.pcolormesh(t,f/1000,db,shading='auto',cmap='magma',vmin=-75,vmax=0,rasterized=True)
        ax.set_title(title,loc='left',fontsize=11,fontweight='bold',pad=12)
        ax.set_xlim(0,2.9);ax.set_ylim(0,4)
        ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for ax in axes[-1,:]:ax.set_xlabel('Time (seconds)')
    for ax in axes[:,0]:ax.set_ylabel('Frequency (kHz)')
    fig.subplots_adjust(left=.065,right=.88,bottom=.09,top=.94,hspace=.36,wspace=.17)
    bar=fig.colorbar(mesh,cax=fig.add_axes([.91,.15,.016,.68]))
    bar.set_label('Magnitude (dB, shared reference)')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT,facecolor='white');plt.close(fig)
    print(OUT)


if __name__ == '__main__':main()
