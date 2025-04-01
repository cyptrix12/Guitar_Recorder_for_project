import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tkinter as tk
import os
import time
import threading

class SoundRecorderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Recording parameters
        self.SAMPLE_RATE = 48000  # Hz
        self.CHANNELS = 1  # Mono
        self.BUFER = 1024
        self.RECORDINGS_DIR = "recordings"
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)

        self.recording = []
        self.is_recording = False
        self.stream = None
        self.is_auto_mode = False
        self.recording_discarded = False

        # Get available drivers
        self.DRIVERS = self.get_available_drivers()

        self.title("Sound Recorder")
        
        self._create_widgets()
        self.update_idletasks()
        self.geometry(f"{self.winfo_width()}x{self.winfo_height()}")

    def get_available_drivers(self):
        return {sd.query_hostapis(i)["name"]: i for i in range(len(sd.query_hostapis()))}

    def get_input_devices(self, hostapi=None):
        devices = sd.query_devices()
        input_devices = [
            d['name'] for d in devices
            if d['max_input_channels'] > 0 and (hostapi is None or d['hostapi'] == hostapi)
        ]
        return input_devices if input_devices else ["No available devices"]

    def update_device_list(self, *args):
        selected_driver = self.driver_var.get()
        hostapi_index = self.DRIVERS.get(selected_driver, None)
        self.device_menu['menu'].delete(0, 'end')
        available_devices = self.get_input_devices(hostapi_index)
        for device in available_devices:
            self.device_menu['menu'].add_command(label=device, command=tk._setit(self.device_var, device))
        self.device_var.set(available_devices[0])

    def count_existing_files(self):
        selected_model = self.model_var.get()
        selected_note = self.note_var.get()
        selected_position = self.position_var.get()
        selected_knobs = self.knobs_entry.get()
        selected_player = self.player_var.get()
        base_name = f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_ID{selected_player}"
        existing_files = [
            f for f in os.listdir(self.RECORDINGS_DIR)
            if os.path.isfile(os.path.join(self.RECORDINGS_DIR, f)) and f.startswith(base_name) and f.endswith(".wav")
        ]
        return len(existing_files)

    def update_file_count(self):
        self.file_count_label.config(text=f"Existing files: {self.count_existing_files()}")

    def toggle_recording(self, event=None):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.recording = []
        self.recording_discarded = False
        selected_device = self.device_var.get()
        device_index = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == selected_device), None)

        def callback(indata, frames, time_info, status):
            if status:
                print(status)
            if self.is_recording:
                self.recording.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype='int32',
                callback=callback,
                device=device_index,
                blocksize=self.BUFER
            )
            self.stream.start()
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            return

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if self.recording and not self.recording_discarded:
            final_recording = np.concatenate(self.recording, axis=0)
            selected_model = self.model_var.get()
            selected_note = self.note_var.get()
            selected_position = self.position_var.get()
            selected_knobs = self.knobs_entry.get()
            selected_player = self.player_var.get()
            file_name = os.path.join(
                self.RECORDINGS_DIR,
                f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_ID{selected_player}_1.wav"
            )
            counter = 2
            while os.path.exists(file_name):
                file_name = os.path.join(
                    self.RECORDINGS_DIR,
                    f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_ID{selected_player}_{counter}.wav"
                )
                counter += 1

            wav.write(file_name, self.SAMPLE_RATE, final_recording.astype(np.int32))
            self.status_label.config(text=f"File saved: {file_name}", fg="green")
            self.update_file_count()
        else:
            self.status_label.config(text="Recording discarded!", fg="red")

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def toggle_auto_mode(self):
        self.is_auto_mode = not self.is_auto_mode
        if self.is_auto_mode:
            self.auto_mode_button.config(text="Disable auto mode")
            self.start_auto_mode()
        else:
            self.recording_discarded = True
            self.auto_mode_button.config(text="Enable auto mode")

    def start_auto_mode(self):
        def auto_mode():
            while self.is_auto_mode:
                try:
                    wait_time = int(self.number1_entry.get())
                    record_time = int(self.number2_entry.get())
                    for remaining in range(wait_time, 0, -1):
                        self.countdown_label.config(text=f"Waiting: {remaining} s", fg="green")
                        time.sleep(1)
                    self.start_recording()
                    for remaining in range(record_time, 0, -1):
                        self.countdown_label.config(text=f"Recording: {remaining} s", fg="red")
                        time.sleep(1)
                    self.stop_recording()
                except ValueError:
                    self.status_label.config(text="Please enter valid numbers!", fg="red")
                    break
        threading.Thread(target=auto_mode, daemon=True).start()

    def _create_widgets(self):
        # Driver selection
        driver_label = tk.Label(self, text="Select driver:")
        driver_label.pack()
        self.driver_var = tk.StringVar()
        self.driver_var.set(next(iter(self.DRIVERS)))  # Default: first available driver
        driver_menu = tk.OptionMenu(
            self, self.driver_var, *self.DRIVERS.keys(),
            command=lambda *args: self.update_device_list()
        )
        driver_menu.pack(pady=10)

        # Input device list
        device_label = tk.Label(self, text="Input device:")
        device_label.pack()
        self.device_var = tk.StringVar()
        self.device_var.set(self.get_input_devices()[0])
        self.device_menu = tk.OptionMenu(self, self.device_var, *self.get_input_devices())
        self.device_menu.pack(pady=10)
        self.update_device_list()

        # Dropdown for guitar model
        model_label = tk.Label(self, text="Guitar model:")
        model_label.pack()
        self.model_var = tk.StringVar()
        self.model_var.set("ArgSG")  # Default value
        model_options = ["ArgSG", "HBTE52", "EpiSGBass", "Gretsch", "EpiSG"]
        model_menu = tk.OptionMenu(
            self, self.model_var, *model_options,
            command=lambda _: self.update_file_count()
        )
        model_menu.pack(pady=10)

        # Dropdown for chord name
        note_label = tk.Label(self, text="Chord name:")
        note_label.pack()
        self.note_var = tk.StringVar()
        self.note_var.set("Am")  # Default value
        note_options = ["Am", "A", "C", "Dm", "D", "Em", "E", "G"]
        note_menu = tk.OptionMenu(
            self, self.note_var, *note_options,
            command=lambda _: self.update_file_count()
        )
        note_menu.pack(pady=10)

        # Dropdown for position
        position_label = tk.Label(self, text="Position:")
        position_label.pack()
        self.position_var = tk.StringVar()
        self.position_var.set("open")  # Default value
        position_options = ["open", "E", "A"]
        position_menu = tk.OptionMenu(
            self, self.position_var, *position_options,
            command=lambda _: self.update_file_count()
        )
        position_menu.pack(pady=10)

        # Entry field for knob settings
        knobs_label = tk.Label(self, text="Knob settings (enter text):")
        knobs_label.pack()
        self.knobs_entry = tk.Entry(self)
        self.knobs_entry.pack(pady=10)
        self.knobs_entry.insert(0, "1")

        # Dropdown for player ID
        player_label = tk.Label(self, text="Player ID:")
        player_label.pack()
        self.player_var = tk.StringVar()
        self.player_var.set("1")  # Default value
        player_options = ["1", "2", "3", "4", "5"]
        player_menu = tk.OptionMenu(
            self, self.player_var, *player_options,
            command=lambda _: self.update_file_count()
        )
        player_menu.pack(pady=10)

        # Additional number fields in one row
        numbers_frame = tk.Frame(self)
        numbers_frame.pack(pady=10)

        number1_label = tk.Label(numbers_frame, text="waiting time (s):")
        number1_label.grid(row=0, column=0, padx=5)
        self.number1_entry = tk.Entry(numbers_frame, width=10)
        self.number1_entry.grid(row=0, column=1, padx=5)
        self.number1_entry.insert(0, "2")

        number2_label = tk.Label(numbers_frame, text="recording time (s):")
        number2_label.grid(row=0, column=2, padx=5)
        self.number2_entry = tk.Entry(numbers_frame, width=10)
        self.number2_entry.grid(row=0, column=3, padx=5)
        self.number2_entry.insert(0, "5")

        # Button for auto mode
        self.auto_mode_button = tk.Button(self, text="Enable auto mode", command=self.toggle_auto_mode)
        self.auto_mode_button.pack(pady=10)

        # Countdown label
        self.countdown_label = tk.Label(self, text="", fg="blue")
        self.countdown_label.pack(pady=10)

        # Label to display the number of existing files
        self.file_count_label = tk.Label(self, text=f"Existing files: {self.count_existing_files()}")
        self.file_count_label.pack(pady=10)

        # Other GUI elements
        self.start_button = tk.Button(self, text="Start recording", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Stop recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack()

        # Status label
        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack(pady=10)

        self.bind("<Return>", self.toggle_recording)

if __name__ == "__main__":
    app = SoundRecorderApp()
    app.mainloop()
