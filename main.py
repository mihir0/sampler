import pyaudio
import wave
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import keyboard
import sounddevice as sd

class Sampler:
    def __init__(self, record_enabled=False):
        self.recording = []
        self.record_enabled = record_enabled # Used for debugging purposes only.
        self.samples = {} # key: String note name, value: loaded sample (numpy array)
        self.pos = {} # key: String note name, value integer indicating current playback position
        self.chunk_size = 64 # number of samples to process/stream at once
        self.dtype = np.int16
        self.stream = None
        self.channels = 2
        self.output_buffer = None # numpy array containing output samples to be streamed. size = self.channels x self.chunk_size
        # sd defaults
        # sd.default.samplerate = 44100
        # sd.default.channels = 2
        sd.default.dtype = 'int16'
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
            np_data = np.frombuffer(audio, dtype=self.dtype)
            # reduce volume
            audio_arr = np.zeros(np_data.size, dtype=self.dtype)
            for i in range(np_data.size):
                audio_arr[i] = int(round(np_data[i] * .5))
            print("ndim: ", audio_arr.ndim, " shape: ", audio_arr.shape)
            print("loaded ", path_map[key], " nframes=", nframes, " nsamples=", nsamples, " samplewidth (in bytes)=", samplewidth, " channels=", channels)
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
    def visualize(self, recording):
            recording_L = recording[::2]
            recording_R = recording[1::2]
            # recording_L = []
            # recording_R = []
            # for i in range(0, len(recording)):
            #     if i % 2 == 0:
            #         recording_L.append(recording[i])
            #     else:
            #         recording_R.append(recording[i])
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
        # ZERO the output buffer
        # for i in range(self.output_buffer.size):
        #     self.output_buffer[i] = 0
        self.output_buffer.fill(0)
        for note in self.samples: #NOTE: can decrease iterations by only going through notes_pressed list. Currently this implementation will detect when a "keyup" event happens...in this case, the sample position will be set back to 0
            if note in notes_pressed:
                sound_playing = True
                for i in range(min(self.output_buffer.size, self.samples[note].size - self.pos[note])):
                    self.output_buffer[i] = self.output_buffer[i] + self.samples[note][i + self.pos[note]]
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
if __name__ == "__main__":
    sampler = Sampler()
    sample_map = {"a":"note.wav", "s":"note2.wav", "d": "note3.wav", "f": "note_R.wav"}
    sampler.load(sample_map)
    sampler.start()
    while not keyboard.is_pressed('q'):
        keys_pressed = []
        for key in sample_map:
            if keyboard.is_pressed(key):
                keys_pressed.append(key)
        sampler.update(keys_pressed)
    sampler.close()
    # sampler.start_sounddevice()