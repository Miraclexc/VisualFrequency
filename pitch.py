import numpy as np
import scipy.signal as signal

# notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
notes = ['C', '', 'D', '', 'E', 'F', '', 'G', '', 'A', '', 'B']

def get_pitch(samples, rate=44100, buffer_size=1024):
    fft_data = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(buffer_size, 1.0/rate)
    peak, _ = signal.find_peaks(fft_data)
    if len(peak) == 0:
        return 0
    return freqs[peak[np.argmax(fft_data[peak])]]

def freq_to_note(freq):
    if freq <= 0:
        return ''
    A4 = 440
    C0 = A4 * np.power(2, -4.75)
    h = round(12 * np.log2(freq / C0))
    octave = h // 12
    n = h % 12
    return notes[n] + str(octave)

def generate_note_frequencies():
    # 计算从C2到C6的音符频率，并取对数
    note_frequencies = {}
    note_frequencies_log = {}
    for octave in range(2, 7):
        for n, note in enumerate(notes):
            if note == '':
                continue
            frequency = 440 * np.power(2, (n - 9 + (octave - 4) * 12) / 12)
            note_frequencies[note + str(octave)] = frequency
            note_frequencies_log[note + str(octave)] = np.log2(frequency)
            
    return note_frequencies, note_frequencies_log
    
    # 高通滤波器
def highpass_filter(data, cutoff=300, fs=44100, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    y = signal.lfilter(b, a, data)
    return y

def noise_gate(signal, threshold):
    gated_signal = np.where(np.abs(signal) > threshold, signal, 0)
    return gated_signal