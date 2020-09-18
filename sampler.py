import wave
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import sounddevice as sd
from typing import List, Tuple

class Sampler:
    def __init__(self, record_enabled=False):
        self.recording = [] # Use for debug recording mode
        self.record_enabled = record_enabled # Used for debugging purposes only.
        self.samples = {} # key: String note name, value: loaded sample (numpy array)
        self.keys = None # Np array of strings. Only set when load_from_list is called
        self.pos = {} # key: String note name, value integer indicating current playback position
        self.chunk_size = 64 # number of samples to process/stream at once
        self.dtype = np.int16
        self.stream = None
        self.channels = 2
        self.output_buffer = None # numpy array containing output samples to be streamed. size = self.channels x self.chunk_size
        # sd default
        sd.default.samplerate = 44100
        sd.default.channels = 2
        sd.default.dtype = 'int16'
    def load(self, path_map: dict):
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
            np_data = np.frombuffer(audio, dtype=self.dtype)
            # reduce volume
            audio_arr = np.zeros(np_data.size, dtype=self.dtype)
            iter = np.nditer(np_data, flags=['f_index'])
            for i in iter:
                audio_arr[iter.index] = i * .5 + .5
            # audio_arr = np_data * .5 #NOTE: fastest way but has lower quality due to truncation
            print("ndim:", audio_arr.ndim, "shape:", audio_arr.shape)
            print("loaded", path_map[key], "nframes=", nframes, "nsamples=", nsamples, "samplewidth (in bytes)=", samplewidth, "channels=", channels)
            self.samples[key] = audio_arr
        print("self.samples = ", self.samples)
        # intialize sample playback positions
        self.pos = self.samples.copy()
        for key in self.pos:
            self.pos[key] = 0
        # initialize output buffer
        self.output_buffer =  np.zeros(self.channels * self.chunk_size, dtype=self.dtype)
        # print("output_buffer initialized:", self.output_buffer)
        # print("output_buffer dtype:", self.output_buffer.dtype)
    def load_from_list(self, path_list:List[Tuple[str, str]]):
        """
        load sampler using list of tuples
        """
        path_map = {}
        key_list = []
        for x, y in path_list:
            path_map[x] = y
            key_list.append(x)
        self.load(path_map)
        try:
            self.keys = np.array(key_list, dtype=np.dtype('U4'))
            print("loaded keys:", self.keys)
        except:
            print("An exception occured when filling up keys array. The key names must be a list of string no longer than 4 characters.")
            exit()
    def visualize(self, recording):
        recording_L = recording[::2]
        recording_R = recording[1::2]
        figs, axs = plt.subplots(2, sharex=True, sharey=True)
        figs.suptitle("Recording")
        axs[0].plot(recording_L)
        axs[1].plot(recording_R)
        plt.show()
    def update(self, notes_pressed):
        """
            Sends samples to output stream based on incoming events
            Parameters:
                notes_pressed: List of notes pressed. Notes are strings that must match the keys of self.samples exactly.
        """
        sound_playing = False
        # Zero the output buffer
        self.output_buffer.fill(0)
        for note in self.samples: #NOTE: can decrease iterations by only going through notes_pressed list. Currently this implementation will detect when a "keyup" event happens...in this case, the sample position will be set back to 0
            if note in notes_pressed:
                sound_playing = True
                sample = self.samples[note]
                iter = np.nditer(self.output_buffer, flags=['f_index'])
                for s in iter:
                    sample_index = iter.index + self.pos[note]
                    if sample_index < sample.size:
                        self.output_buffer[iter.index] = s + sample[sample_index]
                self.pos[note] = self.pos[note] + self.output_buffer.size
            else:
                self.pos[note] = 0
        # DEBUGGING-------
        # print(self.output_buffer)
        # print(self.samples[note][:self.chunk_size * 2])
        # print("buffer dtype:", self.output_buffer.dtype, "sample dtype:", self.samples[note].dtype)
        # exit()
        # self.stream.write(self.samples[note])
        #-----------------
        if sound_playing:
            self.stream.write(self.output_buffer)
            if self.record_enabled:
                self.recording.append(np.array(self.output_buffer, dtype=self.dtype))
    def start(self):
        print(sd.query_devices())
        self.stream = sd.OutputStream()
        self.stream.start()
        print("Sample rate:", sd.default.samplerate, "channels:", sd.default.channels, "chunk size:", self.chunk_size, "debug recording mode:", self.record_enabled)
        print("Sampler started...")
    def close(self):
        if self.record_enabled:
            recording = [item for sublist in self.recording for item in sublist]
            self.visualize(recording)
            print("Playing recording...")
            self.stream.write(recording)
        self.stream.stop()
        print("Sampler stopped.")
    def start_sounddevice(self):
        print(sd.query_devices())
        sd.default.samplerate = 44100
        sd.default.channels = 2
        sd.default.dtype = 'int16'
        wf = wave.open("note_R.wav", 'rb')
        data = wf.readframes(wf.getnframes())
        audio_arr = np.frombuffer(data, dtype=self.dtype)
        # audio_arr.reshape(int(len(audio_arr)/2), 2)
        L = audio_arr[::2]
        R = audio_arr[1::2]
        L_R = np.array((L.tolist(), R.tolist()), dtype=self.dtype)
        L_R = np.reshape(L_R, (L_R[0].size, 2))
        # L_R = np.array(L.tolist(), dtype=self.dtype)
        print("L_R ndim:", L_R.ndim)
        print("L_R shape:", L_R.shape)
        print("L_R:", L_R)
        self.stream = sd.OutputStream(channels=2) #NOTE: !IMPORTANT! output stream is expecting INTERLEAVED array
        self.stream.start()
        # for i in range(L_R.shape[0], 128):
        self.stream.write(audio_arr)
        self.stream.stop()
        start_time = time.time()
        # sd.play(L_R, blocking=True, samplerate=44100)
        status = sd.wait()
        end_time = time.time()
        print(end_time - start_time)
        self.visualize(audio_arr.tolist())