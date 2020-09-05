import pyaudio
import wave
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import keyboard

class Sampler:
    def __init__(self):
        self.recording = []
        self.samples = {} #key: String, value: loaded sample (numpy array)
        self.chunk_size = 64 # number of samples to process/stream at once
    def load(self, path_map):
        """
            path_map (Python Dict)
                key: String keyname
                value: String path_to_wav_file
                example: {"a":"c1.wav", ...}
        """
        for key in path_map:
            # read wavefile by loading into numpy array
            wf = wave.open(path_map[key], 'rb')
            nframes = wf.getnframes()
            audio = wf.readframes(nframes)
            samplewidth = wf.getsampwidth()
            nsamples = nframes * 1
            channels = wf.getnchannels()
            audio_arr = np.frombuffer(audio, dtype=np.int8)
            print("ndim: ", audio_arr.ndim, " shape: ", audio_arr.shape)
            print("loaded ", path_map[key], " nframes=", nframes, " nsamples=", nsamples, " samplewidth=", samplewidth, " channels=", channels)
            self.samples[key] = audio_arr
        print("self.samples = ", self.samples)
    def play_note_wf(self, stream, wf, CHUNK):
        print("press")
        start_time = time.time()
        data = wf.readframes(CHUNK)
        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)
        end_time = time.time()
        print(end_time - start_time)
    
    def process_note_chunk(self, stream, loaded_wav, start_index, chunk_size):
        """
            Parameters:
                loaded_wav: numpy array initialized with audio frames
                start_index: indicating where to start playing sample
                chunk_size: number of samples to stream in one block
            Returns:
                end_index: long containing last sample played
                buffer: rendered samples for the wav file
        """
        # sum_of_notes = np.zeros(chunk_size)
        #pre-processing
        end_index = min(len(loaded_wav), start_index + chunk_size) # exclusive upper limit
        adsr = [.01 * 44100.0, 0, 0, 0, 0 , 0] # ENVELOPE: [attack time, decay time, sustain amplitude, release time]
        attack_slope = 1.00 / float(adsr[0])
        buffer = np.copy(loaded_wav[start_index : end_index])
        #process buffer
        # print("length of buffer: ", len(buffer))
        for i in range(0, len(buffer)):
            pass
            # #Attack
            # if start_index < adsr[0]:
            #     buffer[i] = int(round(float(buffer[i]) * attack_slope * (i + start_index)))
            # buffer[i] = int(round(.5 * buffer[i])) #reduce volume
        # print("buffer: ", buffer)
        # sum_of_notes = np.add(sum_of_notes, buffer)
        #stream buffer
        # stream.write(buffer)
        # stream.write(sum_of_notes)

        # self.recording.append(buffer.tolist())
        return end_index, buffer
        
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

        print("stream opened with: ",
            "format=", p.get_format_from_width(wf.getsampwidth()),
            ", channels=", wf.getnchannels(),
            ", rate=", wf.getframerate())
        # current_index = 0
        #initialize current index
        current_index = self.samples.copy()
        for key in current_index:
            current_index[key] = 0
        chunks = self.samples.copy()
        for key in chunks:
            chunks[key] = np.zeros(1, dtype=np.int8)
        print("chunks: ", chunks)
        sum_of_chunks = np.zeros(self.chunk_size, dtype=np.int8)
        while not keyboard.is_pressed('q'):
            for key in self.samples:
                if keyboard.is_pressed(key):
                    current_index[key], chunks[key] = self.process_note_chunk(stream, self.samples[key], current_index[key], self.chunk_size)
                else:
                    current_index[key] = 0
                    chunks[key] = np.zeros(1, dtype=np.int8)
                # if chunks[key] != -1:
                # print("chunks[key]: ", chunks[key])
                # if len(chunks[key]) > 0:
            for i in range(0, self.chunk_size):
                sum_of_chunks[i] = 0
                for key in chunks:
                    # print("sum_of_chunks: ", sum_of_chunks, ", chunk[key]: ", chunks[key])
                    if i < len(chunks[key]):
                        sum_of_chunks[i] = sum_of_chunks[i] + chunks[key][i]
            stream.write(sum_of_chunks)
        # current_index = 0
        # print("nsamples: ", nsamples)
        # print("len(audio_arr): ", len(audio_arr))
        # while current_index < len(audio_arr):
        #     current_index = self.processing_block(stream, audio_arr, current_index, 512)


        # print(audio_arr)
        # print(len(arr))
        # plt.plot(audio_arr)
        recording = [item for sublist in self.recording for item in sublist]
        print("recording size: ", len(recording))
        # print(recording)
        plt.plot(recording)
        plt.show()
        # stream.write(arr * volume)
        print("playing recording...")
        stream.write(np.array(recording, dtype=np.int8))
        print("closing stream")
        stream.stop_stream()
        stream.close()
        print("terminating pyaudio")
        p.terminate()
        print("Finished.")

if __name__ == "__main__":
    sampler = Sampler()
    sampler.load({"a":"note.wav", "s":"note2.wav", "d": "note3.wav"})
    sampler.start()