---
layout: page
title: Speech Enhancement in TTS Systems
description: Winter of Code 2022 · reducing speech artifacts while preserving intelligibility and voice quality.
img: assets/img/clean_audio_spectrogram.png
importance: 3
category: Major
---

Text-to-speech (TTS) systems can produce understandable speech with audible hiss, roughness, or other noise-like artifacts. Removing those sounds is useful only if the words, pitch, and character of the voice survive the processing.

In this Winter of Code project with Skit, I worked on **speech-enhancement filters and the metrics needed to evaluate them**. The project asked two questions:

1. Can established signal-processing methods improve the audio?
2. How can we tell whether an output is clearer, rather than simply quieter?

[Source code](https://github.com/skit-ai/woc-tts-enhancement) · [Published project write-up](https://tech.skit.ai/woc/) · [Presentation (PDF)]({{ '/assets/pdf/Speech_Enhancement_in_TTS_Skit.pdf' | relative_url }})

## The central finding

The same filter can behave very differently on noisy recordings and on synthesized speech. Our classical filters were more successful on **NOIZEUS**, a benchmark of speech mixed with environmental noise, than on the **Skit TTS dataset**. Some filtered TTS outputs lost speech quality instead of improving it.

This pointed to an important assumption mismatch: a method designed to estimate a separate background-noise process may also suppress parts of a synthesized voice. The [published project write-up](https://tech.skit.ai/woc/#conclusion) discusses this limitation and the motivation for investigating learned denoisers.

## Listen to one example

The clips below are stored outputs from the project repository: one NOIZEUS utterance, its version with **station noise at 5 dB SNR**, and two filtered versions. A lower signal-to-noise ratio (SNR) means noise is stronger relative to the speech.

Listen for both the background sound and the speech itself. Do quieter pauses come with duller consonants, a changed voice, or other artifacts?

<div class="row my-4" role="group" aria-label="Speech enhancement listening comparison">
  <div class="col-md-6 mb-3">
    <div class="border rounded p-3 h-100">
      <p><strong>Clean reference</strong></p>
      <audio controls preload="none" style="width: 100%;" aria-label="Clean reference, NOIZEUS utterance sp15">
        <source src="{{ '/assets/audio/tts/sp15.wav' | relative_url }}" type="audio/wav">
        <a href="{{ '/assets/audio/tts/sp15.wav' | relative_url }}">Download clean reference</a>
      </audio>
    </div>
  </div>
  <div class="col-md-6 mb-3">
    <div class="border rounded p-3 h-100">
      <p><strong>Noisy input · station, 5 dB</strong></p>
      <audio controls preload="none" style="width: 100%;" aria-label="Noisy input with station noise at 5 dB">
        <source src="{{ '/assets/audio/tts/sp15_station_sn5.wav' | relative_url }}" type="audio/wav">
        <a href="{{ '/assets/audio/tts/sp15_station_sn5.wav' | relative_url }}">Download noisy input</a>
      </audio>
    </div>
  </div>
  <div class="col-md-6 mb-3">
    <div class="border rounded p-3 h-100">
      <p><strong>Wiener-filtered output</strong></p>
      <audio controls preload="none" style="width: 100%;" aria-label="Wiener-filtered version of the noisy utterance">
        <source src="{{ '/assets/audio/tts/wiener_filtered_sp15_station_sn5.wav' | relative_url }}" type="audio/wav">
        <a href="{{ '/assets/audio/tts/wiener_filtered_sp15_station_sn5.wav' | relative_url }}">Download Wiener output</a>
      </audio>
    </div>
  </div>
  <div class="col-md-6 mb-3">
    <div class="border rounded p-3 h-100">
      <p><strong>Log-MMSE-filtered output</strong></p>
      <audio controls preload="none" style="width: 100%;" aria-label="Log-MMSE-filtered version of the noisy utterance">
        <source src="{{ '/assets/audio/tts/mmse_log_filtered_sp15_station_sn5.wav' | relative_url }}" type="audio/wav">
        <a href="{{ '/assets/audio/tts/mmse_log_filtered_sp15_station_sn5.wav' | relative_url }}">Download log-MMSE output</a>
      </audio>
    </div>
  </div>
</div>

These are examples from the [repository's audio collection](https://github.com/skit-ai/woc-tts-enhancement/tree/main/docs/audio), not a ranking of the methods across the full dataset.

### What does the sound look like?

A **spectrogram** shows how energy at different frequencies changes over time. Brighter regions indicate stronger spectral energy. Speech structure and background noise can occupy overlapping regions, which helps explain why aggressive filtering can damage the voice as well as reduce noise.

{% include figure.html path="assets/img/tts/spectrogram-comparison.png" class="img-fluid" alt="Four spectrograms of the same NOIZEUS utterance: clean reference, station-noise input at 5 dB, Wiener-filtered output, and log-MMSE-filtered output. All panels use the same frequency range and color scale." caption="Spectrograms computed from the four stored clips above, using one shared magnitude reference and fixed color limits. This is a single listening example, not an aggregate benchmark. A darker output alone does not establish better speech quality." zoomable=true %}

## How the enhancement methods work

A common starting model is **noisy recording = clean speech + background noise**. An enhancer estimates the speech from the observed recording. Its success depends on how closely its assumptions match the actual disturbance.

I implemented and tested five classical approaches:

| Method | Intuition | Important trade-off |
| --- | --- | --- |
| **Wiener filter** | Attenuate spectral components according to estimated speech and noise power. | Strong attenuation can also remove weak speech components. |
| **Kalman filter** | Recursively estimate an evolving speech signal using a dynamical model and noisy observations. | Performance depends on the signal model and noise estimates. |
| **Spectral subtraction with oversubtraction and flooring** | Subtract an estimated noise spectrum; retain a floor to avoid excessively deep spectral valleys. | More subtraction can distort speech; the floor trades residual noise against musical-noise artifacts. |
| **Bayesian MMSE** | Estimate the clean short-time spectral amplitude by minimizing expected squared amplitude error. | An amplitude-error objective does not capture every aspect of perceived quality. |
| **Bayesian log-MMSE** | Estimate spectral amplitude using a squared-error objective in the log-amplitude domain. | The different objective can improve perceptual behavior, but still relies on a suitable noise model. |

The [filter implementations](https://github.com/skit-ai/woc-tts-enhancement/tree/main/Filters) and [visual examples](https://github.com/skit-ai/woc-tts-enhancement/blob/main/Filters/README.md) show how these methods were applied.

<details class="technical-note" markdown="1">
<summary>Why reducing noise can also damage speech</summary>

For a spectral filter, each time–frequency component receives a gain. A gain close to 1 preserves the component; a small gain suppresses it. The filter must infer whether a component is primarily speech or noise from the observed signal and its noise estimate.

If a quiet consonant or a detail of the synthesized voice resembles the estimated noise, it can be attenuated too. Spectral subtraction has a related sensitivity: its oversubtraction factor controls how much estimated noise is removed, while its floor controls how much residual energy remains. The useful setting depends on the audio and disturbance.

This is why lower output energy or a cleaner-looking spectrogram is insufficient evidence of successful enhancement.

</details>

## Two datasets, two different tests

| Dataset | What it contains | What it tests |
| --- | --- | --- |
| **NOIZEUS** | 30 speech utterances from six speakers, corrupted with eight environmental noise types at 0, 5, 10, and 15 dB SNR. | How filters handle known additive-noise conditions, with clean references available. |
| **Skit TTS dataset** | Speech generated by the in-house TTS systems. | Whether the same methods improve the noise-like artifacts present in synthesized speech. |

The environmental conditions included airport, babble, car, exhibition hall, restaurant, street, train, and station noise. The [dataset documentation](https://github.com/skit-ai/woc-tts-enhancement/blob/main/Dataset/README.md) includes examples across noise types and SNR levels; the original benchmark is [NOIZEUS](https://ecs.utdallas.edu/loizou/speech/noizeus/).

A filter that works on an artificially mixed recording has not yet demonstrated that it will work on synthesis artifacts. The second dataset was essential to test that transfer.

## Measuring improvement from several angles

Speech quality has several dimensions. An output can sound less noisy yet be harder to understand, or preserve the words while altering the pitch and timbre. The project therefore implemented and tested a collection of complementary metrics.

| Question | Metrics | How to read them |
| --- | --- | --- |
| **Does it sound closer to a clean reference?** | Perceptual Evaluation of Speech Quality (**PESQ**, narrowband and wideband) | Higher scores generally indicate better predicted perceptual quality. |
| **Are the words easier to understand?** | Short-Time Objective Intelligibility (**STOI**) | Higher scores indicate better estimated intelligibility relative to a reference. |
| **How much has the spectral character changed?** | Mel-Cepstral Distortion (**MCD**, two implementations) and Mean Speech Distortion (**MSD**) | Lower distortion is better; interpretation depends on the representation and alignment. |
| **Are pitch and voicing preserved?** | Gross Pitch Error (**GPE**), Voicing Decision Error (**VDE**), and F0 Frame Error (**FFE**) | Lower error rates are better. GPE focuses on pitch disagreement in mutually voiced frames; VDE captures voiced/unvoiced mistakes; FFE combines pitch and voicing errors. |
| **Does a recognizer recover the intended words?** | Word Error Rate (**WER**) | Lower is better, but the result also depends on the speech recognizer. |

The [metric modules and examples](https://github.com/skit-ai/woc-tts-enhancement/tree/main/Metrics) provide a reusable evaluation component of the project.

For reference-based comparisons, sample rates, channel handling, and temporal alignment matter. A natural recording of the same sentence is not automatically a perfectly matched reference for synthetic speech: legitimate differences in timing, voice, or prosody can affect a score. Listening remains important when interpreting the metrics.

## What we learned

The original experiments and [presentation]({{ '/assets/pdf/Speech_Enhancement_in_TTS_Skit.pdf' | relative_url }}) support three practical observations:

- **The noise condition matters.** Wiener and Kalman filtering were strong baselines on NOIZEUS, with their relative performance depending on the noise and SNR.
- **The metric matters.** A gain in one measure does not establish that all aspects of the voice improved. Quality, intelligibility, spectral distortion, and pitch should be examined together.
- **The target domain matters.** The classical methods did not transfer cleanly to the Skit TTS examples. Assumption mismatch was a plausible explanation: synthesis artifacts need not behave like a separate, slowly varying background-noise process.

This motivated follow-up exploration of learned enhancement models, including [Facebook Denoiser](https://github.com/facebookresearch/denoiser), [SEGAN](https://github.com/santi-pdp/segan_pytorch), and [RNNoise](https://github.com/xiph/rnnoise). Their usefulness would still need to be assessed on the TTS artifacts of interest; the signal-processing results do not establish a neural-model result.

## Explore the work

- [Source code, filters, metrics, and notebooks](https://github.com/skit-ai/woc-tts-enhancement)
- [Published Skit project write-up](https://tech.skit.ai/woc/)
- [Project presentation (PDF)]({{ '/assets/pdf/Speech_Enhancement_in_TTS_Skit.pdf' | relative_url }})
- [Devfolio project page](https://devfolio.co/projects/speech-enhancement-and-metrics-in-tts-systems-e9f9)

<details class="technical-note" markdown="1">
<summary>Get the code</summary>

```bash
git clone https://github.com/skit-ai/woc-tts-enhancement
cd woc-tts-enhancement
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`. The repository contains the filter modules, evaluation metrics, notebooks, and stored example outputs used in this page.

</details>
