# 非模块化版本，已不再更新
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import matplotlib.ticker as ticker

def get_pitch(data, fs, buffer_size):
    # FFT
    fft_data = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(buffer_size, 1.0/fs)
    # 找到最大峰值
    peak, _ = find_peaks(fft_data)
    if len(peak) == 0:
        return 0
    return freqs[peak[np.argmax(fft_data[peak])]]

# 频率转音符名称的函数
def freq_to_note(freq):
    if freq <= 0:
        return ''
    A4 = 440
    C0 = A4 * np.power(2, -4.75)
    h = round(12 * np.log2(freq / C0))
    octave = h // 12
    n = h % 12
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return notes[n] + str(octave)

# 计算从C2到C6的音符频率，并取对数
note_frequencies = {}
note_frequencies_log = {}
for octave in range(2, 7):
    for n, note in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']):
        frequency = 440 * np.power(2, (n - 9 + (octave - 4) * 12) / 12)
        note_frequencies[note + str(octave)] = frequency
        note_frequencies_log[note + str(octave)] = np.log2(frequency)

# 初始化PyAudio
p = pyaudio.PyAudio()

# 打开流
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024)

# 设置matplotlib
plt.ion()
fig, ax = plt.subplots()
x = np.linspace(0, 5, 5*44100//1024)  # 5秒的时间轴
y = np.zeros(5*44100//1024)
line, = ax.plot(x, y)
ax.set_ylim(np.log2(65), np.log2(1000))  # 对数频率范围

# 设置y轴刻度和网格线
ax.set_yticks(list(note_frequencies_log.values()))
ax.set_yticklabels(list(note_frequencies_log.keys()))
ax.grid(True)

# 滚轮缩放功能
def on_scroll(event):
    ax.set_ylim(ax.get_ylim()[0] - event.step, ax.get_ylim()[1] + event.step)
    fig.canvas.draw_idle()

# 光标平移功能
press = None
def on_press(event):
    global press
    press = event.ydata

def on_motion(event):
    global press
    if press is not None:
        dy = press - event.ydata
        press = event.ydata
        ax.set_ylim(ax.get_ylim()[0] + dy, ax.get_ylim()[1] + dy)
        fig.canvas.draw_idle()

def on_release(event):
    global press
    press = None

fig.canvas.mpl_connect('scroll_event', on_scroll)
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

# 更新图表的函数
def update_chart(pitches):
    line.set_ydata(pitches)
    fig.canvas.draw()
    fig.canvas.flush_events()

# 存储音高信息
pitch_history = np.zeros(5*44100//1024)

try:
    while True:
        data = stream.read(1024)
        samples = np.frombuffer(data, dtype=np.float32)
        pitch = get_pitch(samples, 44100, 1024)
        pitch_history = np.roll(pitch_history, -1)
        pitch_history[-1] = pitch
        update_chart(pitch_history)
except KeyboardInterrupt:
    print("Stopped")

stream.stop_stream()
stream.close()
p.terminate()