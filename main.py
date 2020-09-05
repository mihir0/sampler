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
        self.sample_rate = None # set in start method
        self.output_device_index = 4
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
            # buffer[i] = int(round(.5 * buffer[i])) #reduce volume
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
        self.sample_rate = 48000
        print("Opening stream with device:", p.get_device_info_by_host_api_device_index(0, self.output_device_index)['name'])
        print("Setting stream sample rate:", self.sample_rate)

        # read wavefile
        wf = wave.open("note.wav", 'rb')
        # load into numpy array
        nframes = wf.getnframes()
        audio = wf.readframes(nframes)
        nsamples = nframes * 1
        # Convert buffer to float32 using NumPy                                                                                 
        audio_arr = np.frombuffer(audio, dtype=np.int8)
        
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        output_device_index=4,
                        rate=int(self.sample_rate),
                        output=True)

        print("stream opened with: ",
            "format=", p.get_format_from_width(wf.getsampwidth()),
            ", channels=", wf.getnchannels(),
            ", rate=", self.sample_rate)
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
            for i in range(0, self.chunk_size):
                sum_of_chunks[i] = 0
                for key in chunks:
                    # print("sum_of_chunks: ", sum_of_chunks, ", chunk[key]: ", chunks[key])
                    if i < len(chunks[key]):
                        sum_of_chunks[i] = sum_of_chunks[i] + chunks[key][i]
            stream.write(sum_of_chunks)
        recording = [item for sublist in self.recording for item in sublist]
        print("recording size: ", len(recording))
        plt.plot(recording)
        plt.show()
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