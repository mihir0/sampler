# Sampler
This Sampler was initially built to support [lego-pi-ano](https://debkbanerji.com/lego-pi-ano/) and supports 16-bit .wav files.
* Max number of samples is bound by memory limitiations of the Python execution environment. Currently all testing is done with 36 16 bit samples, each sized at 2.18 MB.
* Debug mode records and visualizes which samples are played. Silent gaps are not recorded.
* KeyListener class which allows you to trigger samples from your computer keyboard.
* Fast, simultaneous playback of the samples. I am using `Cython` to offload the audio processing into a C-compiled routine which allows for continous playback of over 25 pressed keys without breaking a sweat.

# Setting up and building the sampler
Since this module uses Cython to create a C-compiled build for efficient audio playback, you will need to have a C compiler on your system.
1. Run `pip install requirements.txt`
2. Build the cython module with `python setup.py build_ext --inplace`. You will need a C compiler for this step.

# Using the sampler with your computer keyboard
1. Initialize the sampler in a python file by setting a playback sample rate. You will need to check what your current sound card is running. Most PCs run either 44100Hz or 48000Hz.
```
    from sampler import Sampler
    sampler = Sampler(sample_rate=48000, record_enabled=False)
```
2. Load the samples by feeding in a python dictionary of [key: note name, value: file name]. If you want to use the keyboard listener, the key names control which keyboard keys will trigger which file.
```
    sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav", "g": "05.wav", "h": "06.wav", "j": "07.wav", "k": "08.wav", "l": "09.wav", ":": "10.wav", "'":"11.wav", "w":"12.wav", "e":"13.wav", "r":"14.wav", "t":"15.wav", "y":"16.wav", "u":"17.wav", "i":"18.wav", "o":"19.wav", "p":"20.wav", "[": "21.wav", "]":"22.wav"}
    sampler.load(sample_map, "samples/legopiano1/")
```
3. Start the sampler.
```
    sampler.start()
```
4. Initialize and start the key listener. This uses the `keyboard` python module to detect keypresses.
```
    listener = KeyListener(sampler)
    listener.start_listening()
```
5. Once the key listener terminates, close the sampler. If you are running the sampler in debug mode, this is when the recorded audio will display.
```
    sampler.close()
```

#Future Enhancements
My development is currently focused on supporting the lego-pi-ano project but this module can be used for many more purposes as well. Here are some of the enhancements I have in store:
1. Supporting different file formats and bit-depth
2. Adding a nice ADSR envelope that's fully customizable