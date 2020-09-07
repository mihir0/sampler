import keyboard
from sampler import Sampler

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