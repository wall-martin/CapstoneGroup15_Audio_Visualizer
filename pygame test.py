import pygame
import numpy as np
from sys import exit
from scipy.io.wavfile import read as wavread
from scipy.io.wavfile import write as wavwrite
from scipy.fft import rfft, rfftfreq

WIDTH, HEIGHT = 256,256
FPS = 15

MP = int(np.floor(WIDTH/2))

audioName = 'sweep.wav'
rate, data = wavread(audioName)

length = data.shape[0] / rate
T = np.floor(length * FPS)
print(f"audio is {length} seconds long, so at {FPS}fps, we will show {T} frames total. Ish.")

def spectro(data, rate, overlap):
    window_length = np.floor(rate / FPS)
    window_length = int(window_length)
    overlap = int(overlap)
    windows = np.arange(0, data.shape[0], window_length - overlap, dtype=int)
    windows = windows[windows + window_length < data.shape[0]]

    dataL = []
    dataR = []
    for start in windows:
        # short term discrete fourier transform
        _dataL = rfft(data[start:start + window_length,0])
        _dataR = rfft(data[start:start + window_length, 1])
        dataL.append(_dataL)
        dataR.append(_dataR)

    _specL = np.array(dataL).T
    _specR = np.array(dataR).T
    # rescale the absolute value of the spectrogram as rescaling is standard
    specL = 10 * np.log10(_specL)
    specR = 10 * np.log10(_specR)
    return (windows, specL, specR)



overlap = 84
windows, specL, specR = spectro(data,rate,overlap)
print(specL[0,1])
print(specL[:5, windows[0]])

pygame.init()
screen = pygame.display.set_mode((800,700))
pygame.display.set_caption('Test')
clock = pygame.time.Clock()

test_surface = pygame.Surface((WIDTH,HEIGHT))


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.blit(test_surface, (25, 0))
    for j in range(0,specL.shape[1]):
        test_surface.fill('Black')
        for i in range(0,HEIGHT):
            pygame.draw.line(test_surface, 'RED', (MP - abs(specL[i, j]), i), (MP + abs(specR[i, j]), i))
        pygame.display.update()
        clock.tick(FPS)