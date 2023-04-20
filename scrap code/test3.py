import pygame
import numpy as np
from sys import exit
from scipy.io.wavfile import read as wavread
from scipy.io.wavfile import write as wavwrite
from scipy.fft import rfft, rfftfreq

audioName = 'sweep.wav'
rate, data = wavread(audioName)

WIDTH, HEIGHT = 256,256
FPS = 15
MP = int(np.floor(WIDTH/2))

length = data.shape[0] / rate
T = int(np.floor(length * FPS))

print(f"audio is {length} seconds long, so at {FPS}fps, we will show {T} frames total. Ish.")

def adv_spectro(data,overlap):
    _data = []
    window = int(data.shape[0] / T)
    specL = []
    specR = []
    for i in range(0, data.shape[0] - window - overlap, window):
        _specL = (rfft(data[i:i + window, 0]))
        _specR = (rfft(data[i:i + window, 1]))
        specL.append(dataFormat(_specL,HEIGHT)) #needs to be more robust...
        specR.append(dataFormat(_specR, HEIGHT))
        #should end with two arrays of size T, each containing RATE/2 entries (one for each frequency in sample range)
    _data.append(10 * np.log10(specL))
    _data.append(10 * np.log10(specR))
    #now we have L, R channels full of T arrays of (RATE/2)/HEIGHT frequency amplitudes
    return _data

def dataFormat(data,HEIGHT): #looking to average out the values across the Y axis (frequency values) over our limited HEIGHT
    gapSize = int((data.shape[0]) / HEIGHT)
    _data = []
    for i in range(0, data.shape[0], gapSize):
        _data.append(abs(np.average(data[i:(i + gapSize)])))
    return _data

specData = adv_spectro(data,0)

pygame.init()
screen = pygame.display.set_mode((800,700))
pygame.display.set_caption('Test')
clock = pygame.time.Clock()
specSurface = pygame.Surface((WIDTH,HEIGHT))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.blit(specSurface, (25, 0))
    for frame in range(T-1):
        specSurface.fill('Black')
        for i in range(HEIGHT):
            pygame.draw.line(specSurface, 'RED', (MP - abs(specData[0][frame][i]), i), (MP + abs(specData[0][frame][i]), i))
        clock.tick(FPS)
    pygame.display.update()
