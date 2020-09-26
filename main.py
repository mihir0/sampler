import keyboard
from sampler import Sampler

if __name__ == "__main__":
    sampler = Sampler(sample_rate=48000)
    sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav"}
    sampler.load(sample_map, "samples/legopiano1/")
    sampler.start()
    while not keyboard.is_pressed('q'):
        keys_pressed = []
        for key in sample_map:
            if keyboard.is_pressed(key):
                keys_pressed.append(key)
        sampler.update(keys_pressed)
    sampler.close()
    # sampler.start_sounddevice()