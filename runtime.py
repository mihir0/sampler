from sampler import Sampler
import time

sampler = None


def setup():
    global sampler
    sampler = Sampler(sample_rate=41000)
    sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav"}
    sampler.load(sample_map, "samples/legopiano1/")
    sampler.start()

def close():
    sampler.close()

def time_block():
    keys_pressed = ["a", "b", "c"]
    start = time.time_ns()
    sampler.update(keys_pressed)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_1_sec():
    pass

if __name__ == "__main__":
    setup()

# Target benchmarks
# current time for 64 * 2 sample block: 96858200 ns = 0.0968582
# target for 48khz sample rate: 
#   48000 samples per sec / 64 samples = 750 blocks per second
#   Avg time for blocks = 1333333.33 ns per block = 0.00133333333 second per block
