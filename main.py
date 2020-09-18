import keyboard
from sampler import Sampler
from typing import List, Tuple, Dict
import threading
import multiprocessing
keys_pressed = []
run_sampler = True
sample_map = {}
sample_list = []
keys = []
def sampler_loop(keys_pressed):
    global sample_map
    sampler = Sampler()
    sampler.load(sample_map)
    # sampler.load_from_list(sample_list)
    sampler.start()
    while run_sampler:
        # sampler.update(keys_pressed)
        # print("running sampler with keys:", keys_pressed)
        # print("running sampler with keys: ", keys_pressed_arr)
        pass
def keyboard_loop(keys_pressed):
    global sample_map
    keys = ["a", "s", "d", "f"]
    while not keyboard.is_pressed('q'):
        # keys_pressed = []
        # for key in sample_map:
        #     if keyboard.is_pressed(key):
        #         keys_pressed.append(key)
        for i in range(len(keys)):
            if keyboard.is_pressed(keys[i]):
                keys_pressed[i] = 1
            else:
                keys_pressed[i] = 0
        print("key pressed:", keys_pressed[:])
    run_sampler = False

if __name__ == "__main__":
    sample_map = {"a":"note.wav", "s":"note2.wav", "d": "note3.wav", "f": "note_R.wav"}
    sample_list = [("a", "note.wav"), ("s", "note2.wav"), ("d", "note3.wav"), ("f", "note_R.wav")]
    keys = ["a", "s", "d", "f"]
    # keys_pos_map = {"a":0, "b":1, "c":2, "d":3, "f": 4}
    # keys_pressed = multiprocessing.Manager().list()
    # for i in range(len(keys)):
    #     keys_pos_map[keys[i]] = i
    keys_pressed = multiprocessing.Array('i', [0, 0, 0, 0])

    # for i in range(len(keys_pressed_arr)):
    #     keys_pressed_arr[i] = False
    print("starting t2")
    t2 = multiprocessing.Process(target=keyboard_loop, args=(keys_pressed,))
    t2.daemon = True
    print("starting t1")
    t1 = multiprocessing.Process(target=sampler_loop, args=(keys_pressed,))
    t1.daemon = True
    t1.start()
    t2.start()
    # sampler_loop(sampler)
    t2.join()
    run_sampler = False
    t1.join()
    # sampler.close()
    
    # sampler.start()
    # while not keyboard.is_pressed('q'):
    #     keys_pressed = []
    #     for key in sample_map:
    #         if keyboard.is_pressed(key):
    #             keys_pressed.append(key)
        # sampler.update(keys_pressed)
    # sampler.close()