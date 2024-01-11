from monitor import PitchMonitor
import time
import pyaudio

def main():
    monitor = PitchMonitor()

    try:
        while True:
            monitor.read_and_update()
            if monitor.is_closed():
                break
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("程序终止")
    finally:
        monitor.close()
        
def audio_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"Device {i}: {dev['name']}")

if __name__ == "__main__":
    main()