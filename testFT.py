import numpy as np
from scipy.io.wavfile import read as wavread
from scipy.io.wavfile import write as wavwrite
from scipy.fft import rfft, rfftfreq
from matplotlib import pyplot as plt


audioName = 'sweep.wav'
rate, data = wavread(audioName)

WIDTH, HEIGHT = 256,256
FPS = 60
MP = int(np.floor(WIDTH/2))

length = data.shape[0] / rate
T = int(np.floor(length * FPS))

window = 500
r = int(data.shape[0]/window)
for i in range(1,r):
    iter = i
    _data = data[(iter - 1 ) * window:iter * window,0]


    yf = rfft(_data)
    xf = rfftfreq(_data.shape[0], 1 / rate) # don't actually need lol
    yf = (10 * np.log10(yf))

    plt.plot(np.abs(yf))
    plt.show()