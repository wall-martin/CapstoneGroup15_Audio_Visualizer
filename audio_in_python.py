import pygame
import numpy as np
from sys import exit
from scipy.io.wavfile import read as wavread
from scipy.io.wavfile import write as wavwrite
from scipy.fft import rfft

audioName = 'lick_demo.wav'
rate, data = wavread(audioName)

pygame.mixer.init()
pygame.mixer.music.load(audioName)
pygame.mixer.music.set_volume(1)

WIDTH, HEIGHT = 900,900
FPS = 24
MP = int(np.floor(WIDTH/2))

length = data.shape[0] / rate
T = int(np.floor(length * FPS))

print(f"audio is {length} seconds long, so at {FPS}fps, we will show {T} frames total. Ish.")

def modifyData(data):
    modified_data = []
    for entry in range(HEIGHT):
        total = 0
        start_index = int(len(data) ** (entry / HEIGHT)) - 1 # this uses log properties without the log
        stop_index = int(len(data) ** (entry / HEIGHT))
        for index in range(start_index, stop_index):
            total += data[index]

        average = total / (stop_index - start_index)
        modified_data.append(average)

        #AND NOW A CONVOLUTION FOR NO REASON OTHER THAN I REALLY WANTED TO
        #JK it smoothes out the data to help make peaks look more natural
        #and helps to define the shapes we hope to see from the audio in the first place

        # Define mask and store as an array
        w = 5
        mask = np.ones((1, w)) / w
        mask = mask[0, :]
        # Convolve the mask with the raw data
        convolved_data = np.convolve(modified_data, mask, 'same')
    return convolved_data

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
        _specL = modifyData(_specL)
        _specL = modifyData(_specR)

        #should end with two arrays of size T,
        # each containing RATE/2 entries (one for each frequency in sample range)
        #execpt we actually averaged out the RATE/2 frequency domain into HEIGHT many values (hopefully)
        specL.append(_specL)
        specR.append(_specR)
    _data.append(specL)
    _data.append(specR)
    return _data

specData = spectro(data,0)

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Test')
clock = pygame.time.Clock()
specSurface = pygame.Surface((WIDTH,HEIGHT))
font = pygame.font.Font('freesansbold.ttf', 32)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.mixer.music.play()
    bars = len(specData[0][0])
    for frame in range(T-1):
        specSurface.fill('Black')
        for i in range(bars):
            pygame.draw.line(specSurface, 'RED', (MP - abs(specData[0][frame][i]), HEIGHT - i), (MP + abs(specData[0][frame][i]), HEIGHT - i))
        screen.blit(specSurface,(0,0))
        pygame.display.update()
        pygame.time.Clock().tick(FPS + FPS*(.2))