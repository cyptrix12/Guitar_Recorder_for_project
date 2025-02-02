import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tkinter as tk
from tkinter import messagebox
import os

# Parametry nagrywania
SAMPLE_RATE = 48000  # Hz
CHANNELS = 1  # Mono
BUFOR = 1024

recording = []
is_recording = False
stream = None

def get_input_devices():
    devices = sd.query_devices()
    input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0]
    return input_devices

def count_existing_files():
    selected_note = note_var.get()
    selected_position = position_var.get()
    base_name = f"{selected_note}_{selected_position}"
    existing_files = [f for f in os.listdir() if f.startswith(base_name) and f.endswith(".wav")]
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
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32', callback=callback, device=device_index, blocksize=BUFOR)
        stream.start()
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można rozpocząć nagrywania: {e}")
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
        # Konwersja do formatu numpy
        final_recording = np.concatenate(recording, axis=0)
        
        # Pobranie wybranej opcji z listy rozwijanej
        selected_note = note_var.get()
        selected_position = position_var.get()
        file_name = f"{selected_note}_{selected_position}.wav"
        
        # Sprawdzenie czy plik już istnieje, jeśli tak - dodaj numerowanie
        counter = 1
        while os.path.exists(file_name):
            file_name = f"{selected_note}_{selected_position}_{counter}.wav"
            counter += 1

        # Zapis do pliku WAV
        wav.write(file_name, SAMPLE_RATE, final_recording.astype(np.float32))
        messagebox.showinfo("Nagranie", f"Plik zapisano: {file_name}")
        update_file_count()
    else:
        messagebox.showwarning("Nagranie", "Brak nagranych danych!")
    
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Tworzenie GUI
root = tk.Tk()
root.title("Rejestrator Dźwięku")
root.geometry("300x350")

# Lista rozwijana z wyborem urządzenia
device_var = tk.StringVar()
device_var.set(get_input_devices()[0])  # Domyślnie pierwsze urządzenie

device_menu = tk.OptionMenu(root, device_var, *get_input_devices())
device_menu.pack(pady=10)

# Lista rozwijana z wyborem nazwy pliku
note_var = tk.StringVar()
note_var.set("A")  # Domyślna wartość
note_options = ["a", "A", "C", "d", "D", "e", "E", "G"]
note_menu = tk.OptionMenu(root, note_var, *note_options, command=lambda _: update_file_count())
note_menu.pack(pady=10)

# Lista rozwijana z wyborem pozycji
position_var = tk.StringVar()
position_var.set("otwarta")  # Domyślna wartość
position_options = ["otwarta", "barowe_e", "barowe_a"]
position_menu = tk.OptionMenu(root, position_var, *position_options, command=lambda _: update_file_count())
position_menu.pack(pady=10)

# Label do wyświetlania liczby istniejących plików
file_count_label = tk.Label(root, text=f"Istniejące pliki: {count_existing_files()}")
file_count_label.pack(pady=10)

start_button = tk.Button(root, text="Rozpocznij nagrywanie", command=start_recording) 
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Zakończ nagranie", command=stop_recording, state=tk.DISABLED)
stop_button.pack()

# Przypisanie klawisza Enter do start/stop nagrywania
root.bind("<Return>", toggle_recording)

root.mainloop()
