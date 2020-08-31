import pyaudio
import wave
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import keyboard

class Engine:
    def play_note_wf(self, stream, wf, CHUNK):
        print("press")
        start_time = time.time()
        data = wf.readframes(CHUNK)
        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)
        end_time = time.time()
        print(end_time - start_time)

    
    def processing_block(self, stream, loaded_wav, start_index, chunk_size):
        """
            Parameters:
                stream: initialized PyAudio output stream
                loaded_wav: numpy array initialized with audio frames
                start_index: long data type indicating where to start playing sample
                chunk_size: number of samples to stream in one block
            Returns:
                end_index: long containing last sample played
        """
        end_index = min(len(loaded_wav), start_index + chunk_size) # exclusive upper limit
        for i in range(start_index, end_index):
            #TODO: sample processing here
            pass
        stream.write(loaded_wav[start_index: end_index])
        return end_index
        
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

        # load into numpy array
        nframes = wf.getnframes()
        audio = wf.readframes(nframes)
        nsamples = nframes * 1
        # Convert buffer to float32 using NumPy                                                                                 
        audio_arr = np.frombuffer(audio, dtype=np.int8)

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        print("stream opened with: ", "format=", p.get_format_from_width(wf.getsampwidth()), ", channels=", wf.getnchannels(),  ", rate=", wf.getframerate())
        current_index = 0
        while not keyboard.is_pressed('q'):
            if keyboard.is_pressed('a'):
                current_index = self.processing_block(stream, audio_arr, current_index, 64)
            else:
                current_index = 0
        # current_index = 0
        # print("nsamples: ", nsamples)
        # print("len(audio_arr): ", len(audio_arr))
        # while current_index < len(audio_arr):
        #     current_index = self.processing_block(stream, audio_arr, current_index, 512)


        print(audio_arr)
        # print(len(arr))
        plt.plot(audio_arr)
        plt.show()
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