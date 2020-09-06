import pyaudio
import wave
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import keyboard
import sounddevice as sd
# from scipy.io import wavfile

class Sampler:
    def __init__(self):
        self.recording = []
        self.samples = {} #key: String, value: loaded sample (numpy array)
        self.chunk_size = 128 # number of samples to process/stream at once
        self.sample_rate = None # set in start method
        self.output_device_index = 4
        self.dtype = np.int16
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
            audio_arr = np.frombuffer(audio, dtype=self.dtype)
            print("ndim: ", audio_arr.ndim, " shape: ", audio_arr.shape)
            print("loaded ", path_map[key], " nframes=", nframes, " nsamples=", nsamples, " samplewidth (in bytes)=", samplewidth, " channels=", channels)
            self.samples[key] = audio_arr
        print("self.samples = ", self.samples)

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
            figs, axs = plt.subplots(2, sharex=True)
            figs.suptitle("Recording")
            axs[0].plot(recording_L)
            axs[1].plot(recording_R)
            plt.show()

    def play_note_wf(self, stream, path, CHUNK):
        print("play_note_wf")
        start_time = time.time()
        wf = wave.open(path, 'rb')
        data = wf.readframes(wf.getnframes())
        audio_arr = np.frombuffer(data, dtype=self.dtype)
        audio_arr.reshape(int(len(audio_arr)/2), 2)
        print("audio_arr ndim:", audio_arr.ndim)
        print("audio_arr shape:", audio_arr.shape)
        print("audio_arr:", audio_arr)
        obj = wave.open('output.wav','w')
        obj.setnchannels(2)
        obj.setsampwidth(2)
        obj.setframerate(44100)
        i = 0
        while i < len(audio_arr):
            stream.write(audio_arr[i:i+CHUNK], num_frames=CHUNK, exception_on_underflow=True)
            obj.writeframesraw(audio_arr[i:i+CHUNK])
            i = i + CHUNK
            # print("playing", i, "to", i + 128)
        end_time = time.time()
        print(end_time - start_time)
        obj.close()
        self.visualize(audio_arr.tolist())
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
        #pre-processing
        end_index = min(len(loaded_wav), start_index + chunk_size) # exclusive upper limit
        adsr = [.01 * float(self.sample_rate), 0, 0, 0, 0, 0] # ENVELOPE: [attack time, decay time, sustain amplitude, release time]
        attack_slope = 1.00 / float(adsr[0])
        buffer = np.copy(loaded_wav[start_index : end_index])
        #process buffer
        # print("length of buffer: ", len(buffer))
        for i in range(0, len(buffer)):
            pass
            # #Attack
            # if start_index < adsr[0]:
            #     buffer[i] = int(round(float(buffer[i]) * attack_slope * (i + start_index)))
            # buffer[i] = int(.99 * buffer[i]) #reduce volume
        # self.recording.append(buffer.tolist())
        return end_index, buffer
        
    def start(self):
        p = pyaudio.PyAudio()
        #print host api info
        info = p.get_host_api_info_by_index(0)
        print(info)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i))
        # set sample rate
        self.sample_rate = p.get_device_info_by_host_api_device_index(0, self.output_device_index)['defaultSampleRate']
        # self.sample_rate = 48000
        print("Opening stream with device:", p.get_device_info_by_host_api_device_index(0, self.output_device_index)['name'])
        print("Setting stream sample rate:", self.sample_rate)

        # read wavefile
        wf = wave.open("note.wav", 'rb')
        # load into numpy array
        nframes = wf.getnframes()
        audio = wf.readframes(nframes)
        nsamples = nframes * 1
        # Convert buffer using NumPy                                                                                 
        audio_arr = np.frombuffer(audio, dtype=self.dtype)
        
        stream = p.open(format=8,
                        channels=2,
                        output_device_index=4,
                        rate=int(self.sample_rate),
                        output=True)
        print("stream opened with: ",
            "format=", p.get_format_from_width(wf.getsampwidth()),
            ", channels=", wf.getnchannels(),
            ", rate=", self.sample_rate)

        # Debugging -------
        # self.play_note_wf(stream, "fork2.wav", 44100)
        self.play_note_wf(stream, "note_R.wav", 32)

        while True:
            pass
        # ----------------

        # initialize current index
        current_index = self.samples.copy()
        for key in current_index:
            current_index[key] = 0
        chunks = self.samples.copy()
        # initialize chunks
        for key in chunks:
            chunks[key] = np.zeros(1, dtype=self.dtype)
        print("chunks: ", chunks)
        sum_of_chunks = np.zeros(self.chunk_size, dtype=self.dtype)
        while not keyboard.is_pressed('q'):
            for key in self.samples:
                if keyboard.is_pressed(key):
                    current_index[key], chunks[key] = self.process_note_chunk(stream, self.samples[key], current_index[key], self.chunk_size)
                else:
                    current_index[key] = 0
                    chunks[key] = np.zeros(1, dtype=self.dtype)
            for i in range(0, self.chunk_size):
                sum_of_chunks[i] = 0
                for key in chunks:
                    # print("sum_of_chunks: ", sum_of_chunks, ", chunk[key]: ", chunks[key])
                    if i < len(chunks[key]):
                        sum_of_chunks[i] = sum_of_chunks[i] + chunks[key][i]
            stream.write(np.array(sum_of_chunks, dtype=self.dtype))
            self.recording.append(sum_of_chunks.tolist())
        recording = [item for sublist in self.recording for item in sublist]
        print("recording size: ", len(recording))
        self.visualize(recording)
        print("playing recording...")
        stream.write(np.array(recording, dtype=self.dtype))
        print("closing stream")
        stream.stop_stream()
        stream.close()
        print("terminating pyaudio")
        p.terminate()
        print("Finished.")

    def start_sounddevice(self):
        print(sd.query_devices())
        sd.default.samplerate = 44100
        sd.default.channels = 2
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
        # obj = wave.open('output.wav','w')
        # obj.setnchannels(2)
        # obj.setsampwidth(2)
        # obj.setframerate(44100)
        start_time = time.time()
        sd.play(L_R, blocking=True, samplerate=44100)
        status = sd.wait()
        end_time = time.time()
        print(end_time - start_time)
        # obj.close()
        self.visualize(audio_arr.tolist())
if __name__ == "__main__":
    sampler = Sampler()
    sampler.load({"a":"note.wav", "s":"note2.wav", "d": "note3.wav", "f": "note_R.wav"})
    # sampler.start()
    sampler.start_sounddevice()