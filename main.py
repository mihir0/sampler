import pyaudio
import wave
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import keyboard

class Engine:
    def play_note(self, stream, wf, CHUNK):
        print("press")
        start_time = time.time()
        data = wf.readframes(CHUNK)
        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)
        end_time = time.time()
        print(end_time - start_time)

    def main(self):
        CHUNK = 1024
        p = pyaudio.PyAudio()
        # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
        #                 channels=wf.getnchannels(),
        #                 rate=wf.getframerate(),
        #                 output=True)
        volume = 1.0     # range [0.0, 1.0]
        fs = 44100       # sampling rate, Hz, must be integer
        duration = 5.0   # in seconds, may be float
        f = 440.0        # sine frequency, Hz, may be float

        # generate samples, note conversion to float32 array
        # arr = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

        # read wavefile
        wf = wave.open("note.wav", 'rb')

        # for paFloat32 sample values must be in range [-1.0, 1.0]
        # stream = p.open(format=pyaudio.paFloat32,
        #                 channels=1,
        #                 rate=fs,
        #                 output=True)

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        # start_time = time.time()
        # data = wf.readframes(CHUNK)
        # while data != b'':
        #     stream.write(data)
        #     data = wf.readframes(CHUNK)
        # end_time = time.time()
        # print(end_time - start_time)
        # keyboard.on_press_key('a', self.play_note(stream, wf, CHUNK))
        while not keyboard.is_pressed('q'):
            if keyboard.is_pressed('a'):
                self.play_note(stream, wf, CHUNK)
        # print(arr)
        # print(len(arr))
        # plt.plot(arr)
        # plt.show()
        # stream.write(arr * volume)
        print("closing stream")
        stream.stop_stream()
        stream.close()
        print("terminating pyaudio")
        p.terminate()
        print("Finished.")

if __name__ == "__main__":
    # print("starting")
    # while True:
    #     pass
    engine = Engine()
    engine.main()