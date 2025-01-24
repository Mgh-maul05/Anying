import pyaudio
import numpy as np
import time

# Parameter audio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Inisialisasi PyAudio
p = pyaudio.PyAudio()

# Fungsi untuk mendeteksi tepukan
def detect_clap(data):
    # Menghitung amplitudo rata-rata
    amplitude = np.frombuffer(data, dtype=np.int16)
    avg_amplitude = np.mean(np.abs(amplitude))

    # Threshold untuk mendeteksi tepukan
    threshold = 500  # Anda mungkin perlu menyesuaikan nilai ini

    if avg_amplitude > threshold:
        return True
    return False

# Membuka stream audio
stream = p.open(format=FORMAT, channels=CHANNELS,
                 rate=RATE, input=True,
                 frames_per_buffer=CHUNK)

print("Mendengarkan suara...")

try:
    while True:
        # Membaca data dari stream
        data = stream.read(CHUNK, exception_on_overflow=False)

        # Mendeteksi tepukan
        if detect_clap(data):
            print("Tepukan tangan terdeteksi!")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Program dihentikan.")

# Menutup stream dan PyAudio
stream.stop_stream()
stream.close()
p.terminate()