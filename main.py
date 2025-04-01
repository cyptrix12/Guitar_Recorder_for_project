import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tkinter as tk
import os
import time
import threading

# Recording parameters
SAMPLE_RATE = 48000  # Hz
CHANNELS = 1  # Mono
BUFER = 1024
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

recording = []
is_recording = False
stream = None
is_auto_mode = False
recording_discarded = False

# Get available drivers
def get_available_drivers():
    return {sd.query_hostapis(i)["name"]: i for i in range(len(sd.query_hostapis()))}

DRIVERS = get_available_drivers()

def get_input_devices(hostapi=None):
    devices = sd.query_devices()
    input_devices = [
        d['name'] for d in devices 
        if d['max_input_channels'] > 0 and (hostapi is None or d['hostapi'] == hostapi)
    ]
    return input_devices if input_devices else ["No available devices"]

def update_device_list(*args):
    selected_driver = driver_var.get()
    hostapi_index = DRIVERS.get(selected_driver, None)
    device_menu['menu'].delete(0, 'end')
    available_devices = get_input_devices(hostapi_index)
    for device in available_devices:
        device_menu['menu'].add_command(label=device, command=tk._setit(device_var, device))
    device_var.set(available_devices[0])

def count_existing_files():
    selected_model = model_var.get()
    selected_note = note_var.get()
    selected_position = position_var.get()
    selected_knobs = knobs_entry.get()
    selected_player = player_var.get()
    base_name = f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_ID{selected_player}"
    existing_files = [
        f for f in os.listdir(RECORDINGS_DIR)
        if os.path.isfile(os.path.join(RECORDINGS_DIR, f)) and f.startswith(base_name) and f.endswith(".wav")
    ]
    return len(existing_files)

def update_file_count():
    file_count_label.config(text=f"Existing files: {count_existing_files()}")

def toggle_recording(event=None):
    global is_recording
    if is_recording:
        stop_recording()
    else:
        start_recording()

def start_recording():
    global recording, is_recording, stream, recording_discarded
    is_recording = True
    recording = []
    recording_discarded = False
    selected_device = device_var.get()
    device_index = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == selected_device), None)
    
    def callback(indata, frames, time, status):
        if status:
            print(status)
        if is_recording:
            recording.append(indata.copy())
    
    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int32',
            callback=callback, device=device_index, blocksize=BUFER
        )
        stream.start()
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")
        return
    
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

def stop_recording():
    global is_recording, stream, recording_discarded
    if not is_recording:
        return
    
    is_recording = False
    if stream is not None:
        stream.stop()
        stream.close()
        stream = None
    
    if recording and not recording_discarded:
        final_recording = np.concatenate(recording, axis=0)
        selected_model = model_var.get()
        selected_note = note_var.get()
        selected_position = position_var.get()
        selected_knobs = knobs_entry.get()
        selected_player = player_var.get()
        file_name = os.path.join(RECORDINGS_DIR, f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_ID{selected_player}_1.wav")
        
        counter = 2
        while os.path.exists(file_name):
            file_name = os.path.join(
                RECORDINGS_DIR,
                f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_ID{selected_player}_{counter}.wav"
            )
            counter += 1

        wav.write(file_name, SAMPLE_RATE, final_recording.astype(np.int32))
        status_label.config(text=f"File saved: {file_name}", fg="green")
        update_file_count()
    else:
        status_label.config(text="Recording discarded!", fg="red")
    
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

def toggle_auto_mode():
    global is_auto_mode, recording_discarded
    is_auto_mode = not is_auto_mode
    if is_auto_mode:
        auto_mode_button.config(text="Disable auto mode")
        start_auto_mode()
    else:
        recording_discarded = True
        auto_mode_button.config(text="Enable auto mode")

def start_auto_mode():
    def auto_mode():
        while is_auto_mode:
            try:
                wait_time = int(number1_entry.get())
                record_time = int(number2_entry.get())
                for remaining in range(wait_time, 0, -1):
                    countdown_label.config(text=f"Waiting: {remaining} s", fg="green")
                    time.sleep(1)
                start_recording()
                for remaining in range(record_time, 0, -1):
                    countdown_label.config(text=f"Recording: {remaining} s", fg="red")
                    time.sleep(1)
                stop_recording()
            except ValueError:
                status_label.config(text="Please enter valid numbers!", fg="red")
                break
    threading.Thread(target=auto_mode, daemon=True).start()

# Creating the GUI
root = tk.Tk()
root.title("Sound Recorder")
root.geometry("350x900")

# Driver selection
driver_label = tk.Label(root, text="Select driver:")
driver_label.pack()
driver_var = tk.StringVar()
driver_var.set(next(iter(DRIVERS)))  # Default: first available driver
driver_menu = tk.OptionMenu(root, driver_var, *DRIVERS.keys(), command=update_device_list)
driver_menu.pack(pady=10)

# Input device list
device_label = tk.Label(root, text="Input device:")
device_label.pack()
device_var = tk.StringVar()
device_var.set(get_input_devices()[0])
device_menu = tk.OptionMenu(root, device_var, *get_input_devices())
device_menu.pack(pady=10)
update_device_list()

lists = [
    ("Guitar model", ["ArgSG", "HBTE52", "EpiSGBass", "Gretsch", "EpiSG"], "model_var"),
    ("Chord name", ["Am", "A", "C", "Dm", "D", "Em", "E", "G"], "note_var"),
    ("Position", ["open", "E", "A"], "position_var"),
    ("Knob settings", ["1", "2", "3", "4"], "knobs_var"),
    ("Player ID", ["1", "2", "3", "4", "5"], "player_var")
]

# Dropdown for guitar model
model_label = tk.Label(root, text="Guitar model:")
model_label.pack()
model_var = tk.StringVar()
model_var.set("ArgSG")  # Default value
model_options = ["ArgSG", "HBTE52", "EpiSGBass", "Gretsch", "EpiSG"]
model_menu = tk.OptionMenu(root, model_var, *model_options, command=lambda _: update_file_count())
model_menu.pack(pady=10)

# Dropdown for chord name
note_label = tk.Label(root, text="Chord name:")
note_label.pack()
note_var = tk.StringVar()
note_var.set("Am")  # Default value
note_options = ["Am", "A", "C", "Dm", "D", "Em", "E", "G"]
note_menu = tk.OptionMenu(root, note_var, *note_options, command=lambda _: update_file_count())
note_menu.pack(pady=10)

# Dropdown for position
position_label = tk.Label(root, text="Position:")
position_label.pack()
position_var = tk.StringVar()
position_var.set("open")  # Default value
position_options = ["open", "E", "A"]
position_menu = tk.OptionMenu(root, position_var, *position_options, command=lambda _: update_file_count())
position_menu.pack(pady=10)

# Entry field for knob settings
knobs_label = tk.Label(root, text="Knob settings (enter text):")
knobs_label.pack()
knobs_entry = tk.Entry(root)
knobs_entry.pack(pady=10)
knobs_entry.insert(0, "1")

# Dropdown for player ID
player_label = tk.Label(root, text="Player ID:")
player_label.pack()
player_var = tk.StringVar()
player_var.set("1")  # Default value
player_options = ["1", "2", "3", "4", "5"]
player_menu = tk.OptionMenu(root, player_var, *player_options, command=lambda _: update_file_count())
player_menu.pack(pady=10)

# Additional number fields in one row
numbers_frame = tk.Frame(root)
numbers_frame.pack(pady=10)

number1_label = tk.Label(numbers_frame, text="waiting time (s):")
number1_label.grid(row=0, column=0, padx=5)
number1_entry = tk.Entry(numbers_frame, width=10)
number1_entry.grid(row=0, column=1, padx=5)
number1_entry.insert(0, "2")

number2_label = tk.Label(numbers_frame, text="recording time (s):")
number2_label.grid(row=0, column=2, padx=5)
number2_entry = tk.Entry(numbers_frame, width=10)
number2_entry.grid(row=0, column=3, padx=5)
number2_entry.insert(0, "5")

# Button for auto mode
auto_mode_button = tk.Button(root, text="Enable auto mode", command=toggle_auto_mode)
auto_mode_button.pack(pady=10)

# Countdown label
countdown_label = tk.Label(root, text="", fg="blue")
countdown_label.pack(pady=10)

# Label to display the number of existing files
file_count_label = tk.Label(root, text=f"Existing files: {count_existing_files()}")
file_count_label.pack(pady=10)

# Other GUI elements
start_button = tk.Button(root, text="Start recording", command=start_recording)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop recording", command=stop_recording, state=tk.DISABLED)
stop_button.pack()

# Status label
status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=10)

root.bind("<Return>", toggle_recording)
root.mainloop()
