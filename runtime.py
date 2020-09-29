from sampler import Sampler
import cython_helloworld as hw
import time

sampler = None
sample_map = None

def setup():
    global sampler, sample_map
    sampler = Sampler(sample_rate=48000, record_enabled=True)
    # sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav"}
    sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav", "g": "05.wav", "h": "06.wav", "j": "07.wav", "k": "08.wav", "l": "09.wav", ":": "10.wav", "'":"11.wav", "w":"12.wav", "e":"13.wav", "r":"14.wav", "t":"15.wav", "y":"16.wav", "u":"17.wav", "i":"18.wav", "o":"19.wav", "p":"20.wav", "[": "21.wav", "]":"22.wav"}
    sampler.load(sample_map, "samples/legopiano1/")
    sampler.start()

def close():
    sampler.close()

def time_block(repetitions=1):
    # keys_pressed = ["a", "s", "d", "f"]
    keys_pressed = list(sample_map.keys())
    start = time.time_ns()
    for i in range(repetitions):
        sampler.update(keys_pressed)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_block_opt(repetitions=1):
    # keys_pressed = ["a", "s", "d", "f"]
    keys_pressed = list(sample_map.keys())
    start = time.time_ns()
    for i in range(repetitions):
        sampler.update_optimized(keys_pressed)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_arr_fill(repetitions=1):
    start = time.time_ns()
    for i in range(repetitions):
        hw.set_array(20000)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_arr_fill_opt(repetitions=1):
    start = time.time_ns()
    for i in range(repetitions):
        hw.set_array_optimized(20000)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

    
if __name__ == "__main__":
    setup()
    # time_block(750)
    # time.sleep(6)
    time_block_opt(750)
    # time_arr_fill(1000)
    # time_arr_fill_opt(1000)

# Target benchmarks for 48khz sample rate
# current time for 64 * 2 sample block: 96858200 ns = 0.0968582
# target for 48khz sample rate: 
#   48000 samples per sec / 64 samples = 750 blocks per second
#   Avg time for blocks = 1333333.33 ns per block = 0.00133333333 second per block
