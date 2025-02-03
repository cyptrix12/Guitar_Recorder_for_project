import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tkinter as tk
import os

# Parametry nagrywania
SAMPLE_RATE = 48000  # Hz
CHANNELS = 1  # Mono
BUFOR = 1024
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

recording = []
is_recording = False
stream = None

# Pobieranie dostępnych sterowników
def get_available_drivers():
    return {sd.query_hostapis(i)["name"]: i for i in range(len(sd.query_hostapis()))}

DRIVERS = get_available_drivers()

def get_input_devices(hostapi=None):
    devices = sd.query_devices()
    input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0 and (hostapi is None or d['hostapi'] == hostapi)]
    return input_devices if input_devices else ["Brak dostępnych urządzeń"]

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
    selected_knobs = knobs_var.get()
    selected_player = player_var.get()
    base_name = f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_{selected_player}"
    existing_files = [f for f in os.listdir(RECORDINGS_DIR) if os.path.isfile(os.path.join(RECORDINGS_DIR, f)) and f.startswith(base_name) and f.endswith(".wav")]
    return len(existing_files)

def update_file_count():
    file_count_label.config(text=f"Istniejące pliki: {count_existing_files()}")

def toggle_recording(event=None):
    global is_recording
    if is_recording:
        stop_recording()
    else:
        start_recording()

def start_recording():
    global recording, is_recording, stream
    is_recording = True
    recording = []
    selected_device = device_var.get()
    device_index = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == selected_device), None)
    
    def callback(indata, frames, time, status):
        if status:
            print(status)
        if is_recording:
            recording.append(indata.copy())
    
    try:
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int32', callback=callback, device=device_index, blocksize=BUFOR)
        stream.start()
    except Exception as e:
        status_label.config(text=f"Błąd: {e}", fg="red")
        return
    
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

def stop_recording():
    global is_recording, stream
    if not is_recording:
        return
    
    is_recording = False
    if stream is not None:
        stream.stop()
        stream.close()
        stream = None
    
    if recording:
        final_recording = np.concatenate(recording, axis=0)
        selected_model = model_var.get()
        selected_note = note_var.get()
        selected_position = position_var.get()
        selected_knobs = knobs_var.get()
        selected_player = player_var.get()
        file_name = os.path.join(RECORDINGS_DIR, f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_{selected_player}_1.wav")
        
        counter = 2
        while os.path.exists(file_name):
            file_name = os.path.join(RECORDINGS_DIR, f"{selected_model}_{selected_note}_{selected_position}_{selected_knobs}_{selected_player}_{counter}.wav")
            counter += 1

        wav.write(file_name, SAMPLE_RATE, final_recording.astype(np.int32))
        status_label.config(text=f"Zapisano plik: {file_name}", fg="green")
        update_file_count()
    else:
        status_label.config(text="Brak nagranych danych!", fg="red")
    
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Tworzenie GUI
root = tk.Tk()
root.title("Rejestrator Dźwięku")
root.geometry("300x700")

# Suwak wyboru sterownika
driver_label = tk.Label(root, text="Wybór sterownika:")
driver_label.pack()
driver_var = tk.StringVar()
driver_var.set(next(iter(DRIVERS)))  # Domyślnie pierwszy dostępny sterownik
driver_menu = tk.OptionMenu(root, driver_var, *DRIVERS.keys(), command=update_device_list)
driver_menu.pack(pady=10)

# Lista urządzeń
device_label = tk.Label(root, text="Urządzenie wejściowe:")
device_label.pack()
device_var = tk.StringVar()
device_var.set(get_input_devices()[0])
device_menu = tk.OptionMenu(root, device_var, *get_input_devices())
device_menu.pack(pady=10)
update_device_list()

lists = [
    ("Model gitary", ["ArgSG", "HBTE52", "EpiSGBass", "Gretsch", "EpiSG"], "model_var"),
    ("Nazwa akordu", ["Am", "A", "C", "Dm", "D", "Em", "E", "G"], "note_var"),
    ("Pozycja", ["otwarta", "E", "A"], "position_var"),
    ("Ustawienia pokręteł", ["1", "2", "3", "4"], "knobs_var"),
    ("ID grającego", ["1", "2", "3", "4", "5"], "player_var")
]

# Lista rozwijana z wyborem modelu gitary
model_label = tk.Label(root, text="Model gitary:")
model_label.pack()
model_var = tk.StringVar()
model_var.set("ArgSG")  # Domyślna wartość
model_options = ["ArgSG", "HBTE52", "EpiSGBass", "Gretsch", "EpiSG"]
model_menu = tk.OptionMenu(root, model_var, *model_options, command=lambda _: update_file_count())
model_menu.pack(pady=10)

# Lista rozwijana z wyborem nazwy akordu
note_label = tk.Label(root, text="Nazwa akordu:")
note_label.pack()
note_var = tk.StringVar()
note_var.set("Am")  # Domyślna wartość
note_options = ["Am", "A", "C", "Dm", "D", "Em", "E", "G"]
note_menu = tk.OptionMenu(root, note_var, *note_options, command=lambda _: update_file_count())
note_menu.pack(pady=10)

# Lista rozwijana z wyborem pozycji
position_label = tk.Label(root, text="Pozycja:")
position_label.pack()
position_var = tk.StringVar()
position_var.set("otwarta")  # Domyślna wartość
position_options = ["otwarta", "E", "A"]
position_menu = tk.OptionMenu(root, position_var, *position_options, command=lambda _: update_file_count())
position_menu.pack(pady=10)

# Lista rozwijana z wyborem ustawień pokręteł
knobs_label = tk.Label(root, text="Ustawienia pokręteł:")
knobs_label.pack()
knobs_var = tk.StringVar()
knobs_var.set("1")  # Domyślna wartość
knobs_options = ["1", "2", "3", "4"]
knobs_menu = tk.OptionMenu(root, knobs_var, *knobs_options, command=lambda _: update_file_count())
knobs_menu.pack(pady=10)

# Lista rozwijana z wyborem ID grającego
player_label = tk.Label(root, text="ID grającego:")
player_label.pack()
player_var = tk.StringVar()
player_var.set("1")  # Domyślna wartość
player_options = ["1", "2", "3", "4", "5"]
player_menu = tk.OptionMenu(root, player_var, *player_options, command=lambda _: update_file_count())
player_menu.pack(pady=10)

# Label do wyświetlania liczby istniejących plików
file_count_label = tk.Label(root, text=f"Istniejące pliki: {count_existing_files()}")
file_count_label.pack(pady=10)

# Pozostałe elementy GUI
start_button = tk.Button(root, text="Rozpocznij nagrywanie", command=start_recording)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Zakończ nagranie", command=stop_recording, state=tk.DISABLED)
stop_button.pack()

# Label do wyświetlania statusu
status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=10)

root.bind("<Return>", toggle_recording)
root.mainloop()
