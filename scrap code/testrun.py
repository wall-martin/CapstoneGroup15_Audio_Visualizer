import numpy as np
from scipy.io.wavfile import read as wavread
from scipy.io.wavfile import write as wavwrite
from scipy.fft import rfft, rfftfreq

rate, data = wavread('riff_clean.wav')
print('rate:',rate,'Hz')
print('data is a:',type(data))
print('data shape is:', data.shape)

length = data.shape[0] / rate
time = np.linspace(0., length, data.shape[0])

print(length, 'seconds')

data_normal = np.int16((data / data.max()) * 32767)

def spec(data,L,overlap):
    new_data = data
    starts = np.arange(0, data.shape[0], L - overlap, dtype=int)
    starts = starts[starts + L < data.shape[0]]
    data_L = []
    data_R = []
    for start in starts:
        # short term discrete fourier transform
        data_Ln = rfft(data[start:start + L, 0])
        data_L.append(data_Ln)
        data_Rn = rfft(data[start:start + L, 1])
        data_R.append(data_Rn)
    specL = np.array(data_L).T
    specR = np.array(data_R).T
    # rescale the absolute value of the spectrogram as rescaling is standard
    spec = 10 * np.log10(specX)

yrf = rfft(data_normal[:,0])
xrf = rfftfreq(data.shape[0], 1 / rate)

plt.plot(xrf, np.abs(yrf))
plt.show()

ylf = rfft(data_normal[:,1])
xlf = rfftfreq(data.shape[0], 1 / rate)

plt.plot(xlf, np.abs(ylf))
plt.show()