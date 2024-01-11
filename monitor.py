import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import pitch

class PitchMonitor:
    def __init__(self, device_index=None, rate=44100, buffer_size=1024, history_size=5*44100//1024, scroll_speed=20):
        self.rate = rate
        self.buffer_size = buffer_size
        self.history_size = history_size
        self.scroll_speed = scroll_speed

        self.pitch_history = np.zeros(history_size)  # 初始化音高历史记录

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=rate,
                                  input=True,
                                  input_device_index=device_index,
                                  frames_per_buffer=buffer_size)

        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(np.linspace(0, 5, history_size), self.pitch_history)

        _, note_frequencies_log = pitch.generate_note_frequencies()
        self.ax.set_ylim(np.log2(65), np.log2(1000))  # 对数频率范围

        # 设置y轴刻度和网格线
        self.ax.set_yticks(list(note_frequencies_log.values()))
        self.ax.set_yticklabels(list(note_frequencies_log.keys()))
        self.ax.grid(True)

        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

        self.press_y = None

    def on_scroll(self, event):
        if event.inaxes == self.ax:
            ymin, ymax = self.ax.get_ylim()
            range = ymax - ymin
            # 调整滚动速度以依赖于当前y轴的范围
            scroll_speed = self.scroll_speed * range / 2000  # 2000是一个基准值，可以根据需要调整

            # 更新y轴范围
            self.ax.set_ylim(ymin + scroll_speed * event.step, ymax - scroll_speed * event.step)
            self.fig.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes == self.ax:
            self.press_y = event.ydata

    def on_motion(self, event):
        if self.press_y is not None and event.inaxes == self.ax:
            dy = self.press_y - event.ydata
            ymin, ymax = self.ax.get_ylim()
            self.ax.set_ylim(ymin + dy, ymax + dy)
            self.press_y = event.ydata
            self.fig.canvas.draw_idle()

    def on_release(self, event):
        self.press_y = None

    def read_and_update(self):
        data = self.stream.read(self.buffer_size, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.float32)
        samples = pitch.noise_gate(samples, 0.01)
        fpitch = pitch.get_pitch(samples, self.rate, self.buffer_size)
        
        self.pitch_history = np.roll(self.pitch_history, -1)
        self.pitch_history[-1] = fpitch
        self.line.set_ydata(np.log2(self.pitch_history))
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
            
    def is_closed(self):
        return not plt.fignum_exists(self.fig.number)

    def close(self):
        if self.is_closed():
            return
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        plt.close(self.fig)