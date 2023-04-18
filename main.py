import pygame
import numpy as np
from sys import exit
from scipy.io.wavfile import read as wavread
from scipy.io.wavfile import write as wavwrite
from scipy.fft import rfft, rfftfreq
#testing purposes
from matplotlib import pyplot as plt


audioName = 'test_song.wav'
# audioName = 'test_song.wav'
rate, data = wavread(audioName)

pygame.mixer.init()
pygame.mixer.music.load(audioName)
pygame.mixer.music.set_volume(0.2)

WIDTH, HEIGHT = 900,900
FPS = 24
MP = int(np.floor(WIDTH/2))

length = data.shape[0] / rate
T = int(np.floor(length * FPS))

print(f"audio is {length} seconds long, so at {FPS}fps, we will show {T} frames total. Ish.")

#the full audio is length*rate samples. we determine T total frames needed. thee frames will determine our windows.

def spectro(data,overlap):
    _data = []
    window = int(data.shape[0] / T)
    specL = []
    specR = []
    for i in range(0, data.shape[0] - window - overlap, window):
        #get L,R channels into frequeny domains.
        # FFT taken over small windows such that each frame is a whole representation of the frequency spectryrm
        _specL = (rfft(data[i:i + window, 0]))
        _specR = (rfft(data[i:i + window, 1]))
        #these arrays currently have more values than we can represent by our HEIGHT constraint.
        #the idea is to use a clever function that averages array values over the entire frequency spectrum
        #and display it over HEIGHT pixles, where each pixle is one frequency range.
        #higher frequency ranges ought to be squished into less pixles than lower frequencies.
#        specL.append(dataFormat(_specL,HEIGHT)) #needs to be more robust...
#        specR.append(dataFormat(_specR, HEIGHT))
        specL.append(_specL)
        specR.append(_specR)
        #should end with two arrays of size T,
        # each containing RATE/2 entries (one for each frequency in sample range)
        #execpt we actually averaged out the RATE/2 frequency domain into HEIGHT many values (hopefully)

    #log for specific data values, because lower frequencies produce much smaller amplitude than do higher ones
    #could we try to implement the Mel scale? Probably?
#    _data.append(10 * np.log10(specL))
#    _data.append(10 * np.log10(specR))
    _data.append(specL)
    _data.append(specR)

    #now we have data split into L, R channels full of T arrays which themselves contain (RATE/2)/HEIGHT frequency amplitudes
    # if you wanted to know the strength of the 50Hz frequency during the 150th frame of our animation, on the left channel:
    #_data[0][150][50*]
    #*(or what4ever bc our frequencies have been averaged over HEIGHT lol)

    return _data

def dataFormat(data,HEIGHT): #looking to average out the values across the Y axis (frequency values) over our limited HEIGHT
    # NEEDS HELP LOL
    gapSize = int((data.shape[0]) / HEIGHT)
    _data = []
    for i in range(0, data.shape[0], gapSize):
        _data.append(abs(np.average(data[i:(i + gapSize)])))
    return _data

specData = spectro(data,0)

pygame.init()
HEIGHT = specData[0][0].shape[0]
screen = pygame.display.set_mode((WIDTH+100,HEIGHT+100))
pygame.display.set_caption('Test')
clock = pygame.time.Clock()
specSurface = pygame.Surface((WIDTH,HEIGHT+50))
font = pygame.font.Font('freesansbold.ttf', 32)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.mixer.music.play()
    bars = specData[0][0].shape[0]
    for frame in range(T-1):
#        screen.fill('Black')
#        text = font.render(f'{frame}', True, 'green')
#        screen.blit(text, (600,30))
        specSurface.fill('Black')
#        plt.plot(np.abs(specData[0][frame][:]))
#        plt.show()
        for i in range(HEIGHT):
            pygame.draw.line(specSurface, 'RED', (MP - abs(specData[0][frame][i]), HEIGHT - i), (MP + abs(specData[0][frame][i]), HEIGHT - i))
        screen.blit(specSurface,(0,0))
        pygame.display.update()
        pygame.time.Clock().tick(FPS)