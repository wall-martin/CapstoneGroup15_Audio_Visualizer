

    # Project outline

    # IDEAS FROM: https://www.youtube.com/watch?v=spUNpyF58BY < 3b1b video on fourier transforms

    # code: import packages: numpy, scipy, tinker(?)
    # what if we used pygame or something to visualize
    # looking for an easy-to-implement graphics system
    # ideally it would have a button for "start sample" and a window where the illustration happens
    # interactability would be cool but it would require us to do a certain amount of file i/o
    # like if users could input their own sample .wav, it could be loaded in by prompts like
    # "what file would you like to load" : "guitar_clean.wav" which the user would have already
    # added to the project library i guess. Maybe a display menu of different existing samples to choose from
    # a menu for performing different functions on samples, previewing how they altered the sound, and the export the
    # newly written .wav file (maybe export associated video?)

    # other notes:
    # our frames don't need to update at each and every pitch value, so maybe after we apply the fourier transform
    # to get the full data information for the audio, we select only every 24 bits per second to become the frames of our
    # animation? Sample rate is often several thousand a second so we don't want to try and draw every single sample lol

    # code: menu prompts and such, calling functions such as playback, altering the file, writing the new wav, etc.

    # code: functions for the graphics visualization
    # First load file,
    # get array of data values,
    # apply fourier transform
    # Create graphics for the 24fps animation
    # apply normalization?
    # map pixles using (x,y) = (amplitude, frequency)
    # we might want to filter out change by comparing (xi,yi) in our array of pixles to (xi-1,yi-1) and (xi+1,yi+1)
    # idea: using color to emphasize change
    # pixles range from (0,1), where 1 is white and 0 is black (or maybe these colors can be chosen in the menu lol)
    # values in-between are grey. or just the midpoint of those two selected colors. ie if 1 is chosen red (255,0,0) and 0 is chosen
    # dark blue(20,20,90), .5 is (.5)(255,0,0) + (20,20,90). actually there's a more sophisticated way to apply this using screen
    # math bc color has a lot of fun linear algebra hiding in it. lol.

    # code: manipulation functions
    # for data[:,0] and [:,1] (left and write channels) we do newdata[i,0] = f(data[i,0]) etc
    # different calls n stuff

    import numpy as np
    from scipy.io.wavfile import read as wavread
    from scipy.io.wavfile import write as wavwrite
    from scipy.fft import rfft, rfftfreq

    FPS = 15

    audioName = 'riff_clean.wav'
    rate, data = wavread(audioName)

    length = data.shape[0] / rate
    T = np.floor(length * FPS)
    print(f"audio is {length} seconds long, so at {FPS}fps, we will show {T} frames total. Ish.")


    def audioNoise(data, noise):
        noisyData = data
        noisyData += noise * np.random(0, 1)  # needs to be adjusted for actual range of appropriate values
        name = 'noisy' + 'riff_clean.wav'
        wavwrite(name, rate, data.astype(np.int16))
        return noisyData


    # create a spec using window size 1/FPSth of the sample rate
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
            _dataL = rfft(data[start:start + window_length, 0])
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
    windows, specL, specR = spectro(data, rate, overlap)
    print(specL[0, 1])
    print(specL[:5, windows[0]])

    # display customization????
    # note: how to take our values and scale them (sensibly) to the visual scale of a 256x256 window.
    # the obvious choice is to average out the values from the stuff?
    # "windows" correlate to frames
    # amplitude information (stored within the array) correlate to the X axis
    # frequencies correlate to the Y values, and each index of the array is one area of frequencies lol

    WIDTH = 256
    HEIGHT = 256
    MP = WIDTH / 2

    #  TODO: format windows, array values of specL,R to fit dimensions of the screen display
    # some sort of button to assign true/false on playback
    playback = True

    # while(playback):
    # audio.play()
    # for w in windows:
    # draw in a line from [MP] - abs(specL[:, w]) to [MP] + abs(specR[:, w]) -> loop?
    # for i in specL.shape[0]:
    # line( [MP] - abs(specL[i, w]), [MP] + abs(specR[i, w]) )
    # some sort of wait function for length/widows.len() seconds
    # canvas.wait(length/windows.len())

    # idea: displaying different