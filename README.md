
# Novelty Module

The Novelty Module delivers a generic approach to generate a wide area 
of novelty functions of music data as often used in Music 
Information Retrieval (MIR). Currently the novelty function is only 
calculated on an energy-base (energy (changes) in frequency bands), tonal 
or harmonic additions may be added later.

To cover a broad range of different novelty function approaches the 
calculation is divided into three parts, each with multiple parameters 
that can be customized: First step is the calculation of the 
short-time-fourier-transformation (STFT) to get a 
magnitude-**spectrogram**. Second, the spectrogram is vertically reduced 
to **frequency bands** by aggregating frequency bins. Afterwards, the 
**post-processing** allows the optional calculation of the 
time-derivative to get energy changes, to transform energy values to a 
logarithmic scale and to perform another frequency-band-reduction (as 
proposed in [2]). (An intermediate (psychoacoustic) filtering right after the calculation of the spectrogram as used in [1] may be included in a later version)

Each step is calculated in a single function, taking all neccessary 
parameters. The function **getNovelty()** is a quick and easy wrapper 
around these functions taking the waveform input, sampling rate 
and parameters for all calculation steps with reasonable default values 
(as documented below). It returns the novelty function. To calculate 
a custom novelty function, call **getNovelty()** with only those 
parameters that need to be customized. For full control, a dictionary 
with all parameters as key-value pairs can be passed (then, individual 
parameters will not be accepted), you can get a dictionary with the 
default values by calling **getParameters()**.

Calculating the magnitude spectrogram is the part with the highest 
computational effort, which is by default done using 
scipy.signal.spectrogram(). This repository includes a much faster, 
specialized (though not much optimized) function implemented in c and using fftw. If this function is available in python it is used automatically. This can be achieved by compiling fastSpectrogram.c as a shared object, for example by using the following command:

*gcc -shared -o fastSpectrogram.so -fPIC -lfftw3f -0fast fastSpectrogram.c*
(Tested under Linux, needs gcc and libfftw3-dev installed)

## getNovelty(wave, fs, **kwargs)

**wave:** input audio signal. Needs to be mono-waveform

**fs:** sampling rate of input signal in Hz

**hoptime:** hopsize used in STFT to calculate the spectrogram in seconds (to ensure constant time resolution of novelty function independent of the sampling rate) (**0.02322 s**)

**frametime:** framesize used in STFT to calculate the spectrogram in seconds (**0.09288 s**)

**window:** window used for STFT. Accepts all windows known from scipy.signal.windows (as string) (boxcar, triang, blackman, hamming, hann, bartlett, flattop, parzen, bohman, blackmanharris, nuttall, barthann). (**"hamming"**)

**nBands:** number of frequecy bands of the novelty function (**11 bands**)

**freqscale:** scale to arange the frequency bands. Either "**tonal**" to include the same amount of (semi-)tones in one frequency band (as used in [2]) or "**mel**" to arange frequency bands according to the (psychoacoustic) mel-scale (as used in [1]) (**"tonal"**).

**minFreq:** lower frequency of lowest band. (**40 Hz**)

**maxFreq:** upper frequency of highest band (**11000 Hz**)

**splitFrequencies:** alternatively a vector of manual split frequencies is accepted. In that case, nBands, freqscale, minFreq and maxFreq are ignored. (**None**)

**overlap:** if True, a frequency band includes frequency bins between the next but one split frequencies with a triangular weight (with the peak at in-between split frequency). (**True**)

**diffLength:** calculate the difference of a energy band value to the mean of the diffLength preceding values. diffLength=0 dows not change the novelty function, diffLength=1 leads to the first derivative (energy changes), diffLength>1 leads to a smoother response of energy changes. (**4**)

**posDiff:** if True, reduce novelty function to positive values (half-wave-rectification). Useful in combination with diffLength>0 to only capture sections of rising energy. (**True**)

**logarithmic:** transform novelty function to logarithmic scale. (**False**)

**nPostReduction:** Apply a second reduction of frequency bands as a last step (after al other post processing) as used in *Onset Patterns*. Leading to nBands / nPostReduction energyBands. (**1**)

Input parameters are checked for completeness, but not for consistency or usefulness. Unsuitable parameters or an unsuitable combination may lead to strange results, long runtime or crashes.

## COMING SOON

If different novelty functions of the same waveform input will be 
calculated, to compare or optimize parameters, a Novelty object may be 
used to save some calculations. The Novelty object is created using 
waveform and samplingrate. Calling **NoveltyObject.getNovelty()** will 
calculate and return the novelty function the way as above. Intermediate 
results (spectrogram, energy in frequency bands,...) are stored, 
parameters may be changed at any time. At the next call of 
**NoveltyObject.getNovelty()** stored data are used as possible (if parameters did not change) and only calculations with new parameters are performed.

 
<br><br>
 
 
[1]: Pampalk, Elias. Islands of music: Analysis, organization, and visualization of music archives. 2001.

[2]: Pohle, Tim, et al. On Rhythm and General Music Similarity. In: ISMIR. 2009. S. 525-530.
