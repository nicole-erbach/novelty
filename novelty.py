import numpy as np
import scipy.signal
try: 
    import fastCFunctions
except (OSError, ImportError):
    print("error importing fastC-Spectrogram-implementation. Working with scipy")


def getDefaultParameters():

    parameters = dict()

    # spectrogram parameters
    parameters["hoptime"] = 0.5*0.02321995
    parameters["frametime"] = 0.5*0.0928798
    parameters["window"] = "hamming"
    
    # energy bands parameters
    parameters["nBands"] = 11
    parameters["freqscale"] = "tonal"
    parameters["minFreq"] = 40
    parameters["maxFreq"] = 11000
    parameters["splitFrequencies"] = None
    parameters["overlap"] = True

    # post processing parameters
    parameters["diffLength"] = 4
    parameters["posDiff"] = True
    parameters["logarithmic"] = False
    parameters["nPostReduction"] = 1
    parameters["normalize"] = True
    
    return parameters


def getNovelty(wave, fs, parameters=None, **kwargs):

    # ---------------- check input ------------------------

    if len(kwargs) > 0:
        
        # dont allow parameters-dict and keywords the same time (warning or error?)
        if parameters != None:
            print("Please dont provide parameters-dictionary and seperate parameters the same time. Abort.")
            return
            
        # check given keys and update parameters 
        parameters = getDefaultParameters()
        for key, value in kwargs.items():
            try:
                parameters[key] = value
            except KeyError:
                print("unknown parameter: \"" + key + ". Abort.")
                return

    else: # len(kwargs == 0)

        if parameters == None:
            parameters = getDefaultParameters()
        else:
            defaults = getDefaultParameters()
            for i in defaults.keys():
                if i not in parameters:
                    print("key \"" + i + "\" is missing in parameter dictionary. Abort.") 
                    return
                    
    # TODO: add check of input values for consistency    

    # -------------- finished input-check ----------------

    # calculate splitFrequencies for energyBands
    if parameters["splitFrequencies"] == None:
        parameters["splitFrequencies"] = getSplitFrequencies(freqscale = parameters["freqscale"], nBands = parameters["nBands"], minHz = parameters["minFreq"], maxHz = parameters["maxFreq"], overlap = parameters["overlap"])

    spectrogramTime, spectrogramFreq, spectrogram = calcSpectrogram (wave, fs, int(np.round(fs*parameters["hoptime"])), int(np.round(fs*parameters["frametime"])), parameters["window"])
    
    energyCurves = calcEnergyCurves(spectrogramTime, spectrogramFreq, spectrogram, parameters["splitFrequencies"], parameters["overlap"])
    
    novelty = postProcessing(energyCurves, parameters["diffLength"], parameters["posDiff"], parameters["logarithmic"], parameters["nPostReduction"], parameters["normalize"])

    return novelty


def getSplitFrequencies(freqscale, nBands, minHz, maxHz, overlap):

    if overlap:
        nSplits = nBands +2
    else:
        nSplits = nBands + 1

    if freqscale == 'mel':
        upper = int(hz2mel(maxHz))
        lower = int(hz2mel(minHz))
        mels = np.linspace(lower, upper, num = nSplits)
        splitFrequencies = np.round(mel2hz(mels)).astype(np.int32)
    elif freqscale == 'tonal':
        upper =  int(hz2semitone(maxHz))
        lower =  int(hz2semitone(minHz))
        semitones = np.linspace(lower, upper, num = nSplits)
        splitFrequencies = np.round(semitone2hz(semitones)).astype(np.int32)
    else:
        print('unknown frequency scale. Single dimension novelty function results')
    
    return splitFrequencies
        
   
def calcSpectrogram (wave, fs, hopsize, framesize, window):
   
    try:
        spectrogram = fastCFunctions.absSpectrogram(wave.astype(np.float32), hopsize, framesize, window)
        spectrogram = spectrogram.transpose() 
    except NameError:
        a, s, spectrogram = scipy.signal.spectrogram(wave, window='hamming', nperseg = framesize, noverlap = framesize - hopsize, scaling = 'density', mode = 'magnitude')
    
    nBlocks = int((wave.size - framesize) // hopsize + 1)
    
    spectrogramFreq = np.arange(0, fs/2, fs/2 / spectrogram.shape[0]) 
    spectrogramTime = np.arange(nBlocks+1) * hopsize / fs
       
    return spectrogramTime, spectrogramFreq, spectrogram 

def calcEnergyCurves(spectrogramTime, spectrogramFreq, spectrogram, splitFrequencies, overlap):
    
    df = spectrogramFreq[1] - spectrogramFreq[0] 
    splitIndices = np.round(splitFrequencies / df).astype(np.int16)

    if overlap:

        energyCurves = np.zeros([len(splitIndices)-2, spectrogram.shape[1]])
        for i in range(len(splitIndices) - 2):
            lower = splitIndices[i]
            upper = splitIndices[i+2]
            energyCurves[i,:] = np.sum(spectrogram[lower:upper+1] * scipy.signal.triang(upper-lower+1)[:,None], axis=0) 

    else:

        energyCurves = np.zeros([len(splitIndices)-1, spectrogram.shape[1]])
        for i in range(len(splitIndices) - 1):
            lower = splitIndices[i]
            upper = splitIndices[i+1]
            energyCurves[i,:] = np.sum(spectrogram[lower:upper+1], axis=0) 

    return energyCurves

    
def postProcessing(energyCurves, diffLength, posDiff, logarithmic, nPostReduction, normalize=True):

    # calc diff 
    if diffLength > 0:
        a = 1
        b = np.ones(diffLength) / diffLength
        filtered = scipy.signal.lfilter(b, a, energyCurves)

        novelty = energyCurves[:, 1:] - filtered[:, :-1]
    else:
        novelty = energyCurves           

    if posDiff:
        novelty[novelty < 0] = 0

    if logarithmic:
        novelty[novelty < 1] = 1
        novelty = np.log(novelty)

    # post reduction
    if nPostReduction > 1:
        split = np.arange(0, int(np.ceil(novelty.shape[0] / nPostReduction)), 1)
        novelty = np.zeros([max(split), novelty.shape[1]])
        for i, val in enumerate(split):
            novelty[val-1,:] += novelty[i,:]

        novelty = novelty

    # normalize
    if normalize = True:
        novelty -= np.min(novelty, axis = -1)[:, None]
        novelty /= np.max(novelty, axis = -1)[:, None]+0.00001

    return novelty

def hz2mel(f):
    """Convert an array of frequency in Hz into mel."""
    return 1127.01048 * np.log(f/700 +1)

def mel2hz(m):
    """Convert an array of frequency in Hz into mel."""
    return (np.exp(m / 1127.01048) - 1) * 700        

def hz2semitone(f):
    """Convert an array of frequency in Hz into semitone number (440Hz = 0)."""
    return 12*np.log2(f/440)

def semitone2hz(f):
    """Convert an array of semitone numbers (440Hz = 0) to an array of hz."""
    return 440 * 2**(f/12)

