import pyaudio
import wave
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import keyboard

class Engine:
    def __init__(self):
        self.recording = []
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
        #pre-processing
        end_index = min(len(loaded_wav), start_index + chunk_size) # exclusive upper limit
        adsr = [1 * 44100, 0, 0, 0, 0 , 0] # ENVELOPE: [attack time, decay time, sustain amplitude, release time]
        attack_slope = 1.0 / float(adsr[0])
        buffer = np.copy(loaded_wav[start_index : end_index])
        #process buffer
        # print("length of buffer: ", len(buffer))
        for i in range(0, len(buffer)):
            #TODO: sample processing here
            #Attack
            if start_index < adsr[0]:
                # print("before: ", buffer[i], ", before float: ", float(buffer[i]), " attack_slope: ", attack_slope)
                buffer[i] = int(round(float(buffer[i]) * attack_slope * start_index))
                # print("after: ", buffer[i])
        #stream buffer
        stream.write(buffer)
        # self.recording.append(buffer.tolist())
        return end_index
        
    def start(self):
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
        wf = wave.open("note_signed_16bit.wav", 'rb')

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

        print("stream opened with: ",
            "format=", p.get_format_from_width(wf.getsampwidth()),
            ", channels=", wf.getnchannels(),
            ", rate=", wf.getframerate())
        current_index = 0
        while not keyboard.is_pressed('q'):
            if keyboard.is_pressed('a'):
                current_index = self.processing_block(stream, audio_arr, current_index, 128)
            else:
                current_index = 0
        # current_index = 0
        # print("nsamples: ", nsamples)
        # print("len(audio_arr): ", len(audio_arr))
        # while current_index < len(audio_arr):
        #     current_index = self.processing_block(stream, audio_arr, current_index, 512)


        # print(audio_arr)
        # print(len(arr))
        # plt.plot(audio_arr)
        # print(self.recording)
        # plt.plot(self.recording)
        # plt.show()
        # stream.write(arr * volume)
        print("closing stream")
        stream.stop_stream()
        stream.close()
        print("terminating pyaudio")
        p.terminate()
        print("Finished.")

if __name__ == "__main__":
    engine = Engine()
    engine.start()