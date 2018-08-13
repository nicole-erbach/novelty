import ctypes
import numpy as np
from numpy import ctypeslib
import scipy.signal.windows

fastCSpectrogram = ctypes.CDLL('/home/nico/develop/public/novelty/fastSpectrogram.so')
#fastSpectrogram.fastSpectrogram.argtypes = [ctypeslib.ndpointer(np.float32, ndim=1, flags='C'), ctypeslib.ndpointer(np.float32, ndim=2, flags='C'), ctypes.c_int, ctypes.c_int, ctypes.c_int]

fastCSpectrogram.absSpectrogram.argtypes = [ctypeslib.ndpointer(np.float32, ndim=1, flags='C'), ctypeslib.ndpointer(np.float32, ndim=2, flags='C'), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypeslib.ndpointer(np.float32, ndim=1, flags='C')]

def absSpectrogram(wave, hop, frame, window):
    global fastC
    specsize = int(np.floor(frame / 2) +1)
    nBlocks = int(np.floor(wave.size / hop - frame/hop + 1));
    spectrogram = np.zeros([nBlocks, specsize], dtype=np.float32);
    
    window = scipy.signal.windows.get_window(window, frame, fftbins=False).astype(np.float32)
    #print(wave.size)
    #print(spectrogram.size)
    fastCSpectrogram.absSpectrogram(wave, spectrogram, wave.size, hop, frame, window)
        
    return spectrogram

