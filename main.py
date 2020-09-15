import keyboard
from sampler import Sampler
import threading
keys_pressed = []
run_sampler = True
def sampler_loop(sampler):
    global keys_pressed
    while run_sampler:
        sampler.update(keys_pressed)
        # print("running sampler with keys:", keys_pressed)
def keyboard_loop():
    global keys_pressed
    while not keyboard.is_pressed('q'):
        keys_pressed = []
        for key in sample_map:
            if keyboard.is_pressed(key):
                keys_pressed.append(key)
        print("key pressed:", keys_pressed)

if __name__ == "__main__":
    sampler = Sampler()
    sample_map = {"a":"note.wav", "s":"note2.wav", "d": "note3.wav", "f": "note_R.wav"}
    sampler.load(sample_map)
    sampler.start()
    print("starting t2")
    t2 = threading.Thread(target=keyboard_loop, daemon=True)
    print("starting t1")
    t1 = threading.Thread(target=sampler_loop, daemon=True, args=(sampler,))
    t1.start()
    t2.start()
    t2.join()
    run_sampler = False
    t1.join()

    sampler.close()
    
    # sampler.start()
    # while not keyboard.is_pressed('q'):
    #     keys_pressed = []
    #     for key in sample_map:
    #         if keyboard.is_pressed(key):
    #             keys_pressed.append(key)
        # sampler.update(keys_pressed)
    # sampler.close()