import pygame
import numpy as np
from sys import exit
from scipy.io.wavfile import read as wavread
from scipy.io.wavfile import write as wavwrite
from scipy.fft import rfft
import sounddevice as sd


# class initializes screen elements as button objects
class Button():
    def __init__(self, height, width, position, text, color = "white"):
        self.color = color
        self.height = height
        self.width = width
        self.position = position
        self.text = font.render(text, False, "black")
        self.text_rectangle = self.text.get_rect(center = position)
        self.surface = pygame.Surface((height, width))
        self.rectangle = self.surface.get_rect(center = position)

    # draws button objects on the screen when called
    def draw_button(self, screen):
        self.surface.fill(self.color)
        screen.blit(self.surface, self.rectangle)
        screen.blit(self.text, self.text_rectangle)

# child class allows clicking the button to load a .wav file
class SongButton(Button):
    def __init__(self, height, width, position, text, file_path):
        super().__init__(height, width, position, text)
        self.file_path = file_path


# takes 20,000+ values and scales them using logs to appear visually in the same proportions our ears hear them
def modifyData(data):
    modified_data = []
    for entry in range(screen_height):
        total = 0
        # data entries are split logarithmically into {screen height in pixels} number of new data points
        start_index = int(len(data) ** (entry / screen_height)) - 1
        stop_index = int(len(data) ** (entry / screen_height))
        for index in range(start_index, stop_index):
            total += data[index]
        average = total / (stop_index - start_index)
        # modified data looks approximately like what we hear
        modified_data.append(average)

        #Now we convolve the modified data to help make peaks look more natural

        # Define a weighting distribution (mask) and store as an array
        weight = 5
        mask = np.ones(weight) / weight
        # Convolve the mask with the raw data, to 'blur' the raw data
        convolved_data = np.convolve(modified_data, mask, 'same')
    return convolved_data

def spectro(data,overlap):
    _data = []
    window = int(data.shape[0] / T)
    specL = []
    specR = []

    # draw loading bar
    pygame.draw.line(screen, "red", (screen_width / 2 - 163, 500), (screen_width / 2 + 163, 500), 3)
    pygame.draw.line(screen, "red", (screen_width / 2 - 163, 510), (screen_width / 2 + 163, 510), 3)
    pygame.draw.line(screen, "red", (screen_width / 2 - 163, 500), (screen_width / 2 - 163, 510), 3)
    pygame.draw.line(screen, "red", (screen_width / 2 + 163, 500), (screen_width / 2 + 163, 510), 3)
    pygame.display.update()
    bar_variable = 0


    loop_length = int((data.shape[0] - window - overlap) / window) + 1
    for frame in range(0, data.shape[0] - window - overlap, window):
        # Fast Fourier Transform taken over small windows, split into left and right channels 
        # Each frame is a whole representation of the frequency spectrum
        frame_specL = (rfft(data[frame:frame + window, 0]))
        frame_specR = (rfft(data[frame:frame + window, 1]))

        #modify 20,000+ data points into {screen height in pixels} data points
        frame_specL = modifyData(frame_specL)
        frame_specR = modifyData(frame_specR)

        #should end with two arrays of size T,
        # each containing RATE/2 entries (one for each frequency in sample range)
        #execpt we actually averaged out the RATE/2 frequency domain into HEIGHT many values (hopefully)
        specL.append(frame_specL)
        specR.append(frame_specR)

        # updates loading bar
        if bar_variable == 0:
            width = int(325 / loop_length / 2) + 1
            start_position = (screen_width / 2 - 162 + int(325 / loop_length / 4), 500)
            end_position = (screen_width / 2 - 162 + int(325 / loop_length / 4), 510)
        else:
            width = int(325 / loop_length) + 1
            start_position = (screen_width / 2 - 162 + int(bar_variable), 500)
            end_position = (screen_width / 2 - 162 + int(bar_variable), 510)
        pygame.draw.line(screen, "red", start_position, end_position, width)
        pygame.display.update()
        bar_variable += 325 / loop_length
        
    _data.append(specL)
    _data.append(specR)
    return _data


# initializes pygame and some basic variables
pygame.init()
screen_width, screen_height = 650, 650
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Capstone Project: Audio Visualization')
clock = pygame.time.Clock()
specSurface = pygame.Surface((screen_width,screen_height))
font = pygame.font.Font('freesansbold.ttf', 32)

program_state = "welcome"
audio_name = "ErrorMessage_NoAudioSelected.wav"
load_time_modifier = 0

# initializes every button once at the start 
start_button = Button(350, 100, (screen_width / 2, 100),  "Load / Play Audio")
options_button = Button(250, 100, (screen_width / 2, 250), "Options")
coloron_button = Button(150, 50, (screen_width / 7, 50), "Color On")
coloroff_button = Button(150, 50, (screen_width / 7, 115), "Color Off", "red")
axeson_button = Button(150, 50, (screen_width / 7, 535), "Axes On", "red")
axesoff_button = Button(150, 50, (screen_width / 7, 600), "Axes Off")
record_button = Button(300, 100, (screen_width / 2, 400),  "Record Audio")
exit_button = Button(150, 100, (screen_width / 2, 550), "Exit")
return_button = Button(115, 60, (7 * screen_width / 8, 50),  "Return")
recording_button = Button(250, 100, (screen_width / 2, 250), "Record")
recordinglength_button = Button(600, 100, (screen_width / 2, 450), "Length of Recording (in seconds)")
waittime_button = Button(600, 100, (screen_width / 2, 250), "")
loading_button = Button(200, 100, (screen_width / 2, 400), "Loading...")

# initializes buttons allowing user to choose recording length
recording_length = []
for index in range(6):
    recording_length.append(Button(50, 50, ((index + 1) * screen_width / 7, 550), f"{(index + 1) * 5}"))
recording_length[0].color = "red" 
selected_length = recording_length[0]   

# initializes buttons allowing user to choose what track to play
tracks = {"Fire" : "fire_demo", 
          "Liar" : "liar_demo", 
          "Lick" : "lick_demo", 
          "Reverb" : "reverb_demo", 
          "Strings Tremolo" : "strings_trem_demo", 
          "Sweep" : "sweep", 
          "Test Song" : "test_song", 
          "Test Song 2" : "test_song2", 
          "Tremolo" : "tremolo_demo", 
          "Recording" : "ErrorMessage_NoRecordingMade"}
# audio_choices is a list of SongButtons
audio_choices = []
track_number = 0
for track in tracks:
    audio_choices.append(SongButton(((len(track) + 3) * 20), 50, (screen_width / 2, 30 + track_number * 65),  f"{track_number + 1}: {track}", tracks[track]))
    track_number += 1
selected_track = audio_choices[0]

# initializes color values for drawing the data
colors = []
for i in range(256):
    colors.append((255 - i, i, 0))
for i in range(256):
    colors.append((0, 255 - i, i))
for i in range(256):
    colors.append((i, 0, 255 - i))
# this variable keeps track of color movement to ensure it is smooth
color_index_modifier = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # checks for button presses on welcome screen
        if program_state == "welcome":
            if event.type == pygame.MOUSEBUTTONUP:
                if start_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                    program_state = "loading"
                if options_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                    program_state = "options"
                if record_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                    program_state = "recording" 
                if exit_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                    pygame.quit()
                    exit()

        # checks for button presses on options screen
        elif program_state == "options":
            if event.type == pygame.MOUSEBUTTONUP: 
                if return_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                    program_state = "welcome"
                # toggles color
                if coloroff_button.rectangle.collidepoint(pygame.mouse.get_pos()) and coloroff_button.color == "white":
                    coloron_button.color = "white"
                    coloroff_button.color = "red"
                if coloron_button.rectangle.collidepoint(pygame.mouse.get_pos()) and coloron_button.color == "white":
                    coloroff_button.color = "white"
                    coloron_button.color = "red"
                # toggles axes
                if axesoff_button.rectangle.collidepoint(pygame.mouse.get_pos()) and axesoff_button.color == "white":
                    axeson_button.color = "white"
                    axesoff_button.color = "red"
                if axeson_button.rectangle.collidepoint(pygame.mouse.get_pos()) and axeson_button.color == "white":
                    axesoff_button.color = "white"
                    axeson_button.color = "red"
                # if a different audio is selected it highlights in red, the unselected one goes back to white
                for track in audio_choices:
                    if track.rectangle.collidepoint(pygame.mouse.get_pos()):
                        selected_track.color = "white"
                        selected_track = track
                        selected_track.color = "red"
                        audio_name = selected_track.file_path + ".wav"

        # checks for button presses on recording screen
        elif program_state == "recording":
            if event.type == pygame.MOUSEBUTTONUP:
                # if a different recording length is selected it highlights in red, the unselected one goes back to white
                for length in recording_length:
                    if length.rectangle.collidepoint(pygame.mouse.get_pos()):
                        selected_length.color = "white"
                        selected_length = length
                        selected_length.color = "red"

                # if the record button is selected, a recording of the given length is written to .wav file
                if recording_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                    for button in recording_length:
                        if button.color == "red":
                            recording_seconds = (recording_length.index(button) + 1) * 5

                    # the recording is taken here, the recording button updates to show this
                    recording = sd.rec(recording_seconds * 44100, samplerate = 44100, channels = 2)

                    recording_button.text = font.render("Recording...", False, "black")
                    recording_button.text_rectangle = recording_button.text.get_rect(center = recording_button.position)
                    recording_button.draw_button(screen)
                    pygame.display.update()

                    sd.wait()

                    # recording button updates to normal state
                    recording_button.text = font.render("Record", False, "black")
                    recording_button.text_rectangle = recording_button.text.get_rect(center = recording_button.position)
                    recording_button.draw_button(screen)
                    pygame.display.update()

                    # recording is stored as .wav and automatically selected as current track
                    wavwrite("user_recording.wav", 44100, recording)
                    selected_track.color = "white"
                    selected_track = audio_choices[-1]
                    selected_track.color = "red"
                    selected_track.file_path = "user_recording"
                    audio_name = selected_track.file_path + ".wav"
                if return_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                    program_state = "welcome"

    # at least 24 times per second the following code should run, starting by making the screen a blank slate
    screen.fill("black")

    # draws appropriate buttons for welcome screen
    if program_state == "welcome":
        start_button.draw_button(screen)
        options_button.draw_button(screen)
        record_button.draw_button(screen)
        exit_button.draw_button(screen)

    # draws appropriate buttons for options screen
    elif program_state == "options":
        return_button.draw_button(screen)
        coloron_button.draw_button(screen)
        coloroff_button.draw_button(screen)
        axeson_button.draw_button(screen)
        axesoff_button.draw_button(screen)
        for track_button in audio_choices:
            track_button.draw_button(screen)

    # draws appropriate buttons for recording screen
    elif program_state == "recording":
        recording_button.draw_button(screen)
        recordinglength_button.draw_button(screen)
        for button in recording_length:
            button.draw_button(screen)
        return_button.draw_button(screen)

    # loads .wav file audio, puts data into a useable array and draws appropriate buttons for loading screen
    elif program_state == "loading":
        # reads data file
        rate, data = wavread(audio_name)

        # loads audio
        pygame.mixer.init()
        pygame.mixer.music.load(audio_name)
        pygame.mixer.music.set_volume(1)

        # ascertains important values about the data
        FPS = 24
        MP = int(np.floor(screen_width/2))
        length = data.shape[0] / rate
        T = int(np.floor(length * FPS))

        # draws loading button and estimates the wait time based on data length
        loading_button.draw_button(screen)
        if load_time_modifier != 0:
            waittime_button.text = font.render(f"Approximant Wait: {int(T / load_time_modifier)} seconds", False, "black")
        else:
            waittime_button.text = font.render(f"Approximant Wait: Unknown", False, "black")
        waittime_button.text_rectangle = waittime_button.text.get_rect(center = waittime_button.position)
        waittime_button.draw_button(screen)
        pygame.display.update()

        # transforms data into usable and visualizable form, then switches to visuals screen
        start_load_time = pygame.time.get_ticks()
        specData = spectro(data,0)
        end_load_time = pygame.time.get_ticks()
        # this equation detemines a load time modifier to be used during the next load based on computer preformance during this load 
        load_time_modifier = T / ((end_load_time - start_load_time) / 1100)
        print(load_time_modifier)
        program_state = "visuals"

    # displays our modified spectrogram
    elif program_state == "visuals":
        # plays audio
        pygame.mixer.music.play()
        # determines number of data points to display
        bars = len(specData[0][0])
        # displays current amplitudes at each frame (approximately 24 times per second)
        for frame in range(T-1):
            specSurface.fill('black')
            color_index = 0 + color_index_modifier
            # draws each line/amplitude according to value in data array
            for i in range(bars):
                if coloroff_button.color == "red":
                    pygame.draw.line(specSurface, 'red', (MP - abs(specData[0][frame][i]), screen_height - i), (MP + abs(specData[0][frame][i]), screen_height - i))
                # if color is selected, the color of the lines is pulled from colors list
                else:
                    pygame.draw.line(specSurface, colors[color_index % len(colors)], (MP - abs(specData[0][frame][i]), screen_height - i), (MP + abs(specData[0][frame][i]), screen_height - i))
                    color_index += 1
            # changing this modifier makes the color move downwards
            color_index_modifier += 5
            # draws each line on the screen
            screen.blit(specSurface,(0,0))
            return_button.draw_button(screen)
            pygame.time.Clock().tick(FPS + FPS*(.2))
            # draws axes titles if "axes titles on" button is selected
            if axeson_button.color == "red":
                x_label = font.render("Amplitude >", False, "red" if  coloroff_button.color == "red" else colors[(color_index + int(len(colors) / 2)) % len(colors)])
                y_label = font.render("Frequency ^", False, "red" if  coloroff_button.color == "red" else colors[color_index % len(colors)])
                screen.blit(x_label, x_label.get_rect(center = (500, 550)))
                screen.blit(y_label, y_label.get_rect(center = (150, 100)))
            pygame.display.update()

            # is return button is clicked, the display and audio are interupted 
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP: 
                    if return_button.rectangle.collidepoint(pygame.mouse.get_pos()):
                        pygame.mixer.music.stop()
                        program_state = "welcome"
            if program_state == "welcome":
                break
    
    pygame.display.update()
