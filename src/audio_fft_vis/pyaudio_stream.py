from abc import abstractmethod
import pyaudio
from typing import Optional, Callable
import time

from .audio_stream import AudioStream


class PyAudioStream(AudioStream):
    pa: pyaudio.PyAudio
    stream_start_time: float

    def start(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            input_device_index=self.device,
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            output=False,
            frames_per_buffer=self.frames_per_buffer,
            stream_callback=self.non_blocking_stream_read,
        )
        self.stream.start_stream()
        self.stream_start_time = time.time()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def detect_default_device(self) -> int:
        return self.input_device()

    def detect_rate(self, device: int) -> int:
        return self.valid_low_rate(device)

    def non_blocking_stream_read(self, in_data, frame_count, time_info, status):
        self.on_data(in_data)
        return None, pyaudio.paContinue

    def input_device(self):
        """
        See which devices can be opened for microphone input.
        Return the first valid device
        """
        pa = pyaudio.PyAudio()
        mics = []
        for device in range(pa.get_device_count()):
            if self.test_device(device):
                mics.append(device)

        if len(mics) == 0:
            raise Exception("No suitable device found")

        print("Found %d working microphone device(s): " % len(mics))
        for mic in mics:
            self.print_mic_info(mic)

        pa.terminate()
        print(f"Using Mic {mics[0]}")
        return mics[0]

    def valid_low_rate(self, device, test_rates=[44100, 22050]):
        """Set the rate to the lowest supported audio rate."""
        pa = pyaudio.PyAudio()
        for testrate in test_rates:
            if self.test_device(device, rate=testrate):
                return testrate

        # If none of the test_rates worked, try the default rate:
        self.info = pa.get_device_info_by_index(device)
        default_rate = int(self.info["defaultSampleRate"])

        if self.test_device(device, rate=default_rate):
            return default_rate

        print(
            "SOMETHING'S WRONG! I can't figure out a good sample-rate for DEVICE =>",
            device,
        )
        pa.terminate()
        return default_rate

    def test_device(self, device, rate=None):
        """given a device ID and a rate, return True/False if it's valid."""
        pa = pyaudio.PyAudio()
        try:
            info = pa.get_device_info_by_index(device)
            if not int(info["maxInputChannels"]) > 0:
                return False

            if rate is None:
                rate = int(info["defaultSampleRate"])

            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                input_device_index=device,
                frames_per_buffer=1024,
                rate=rate,
                input=True,
            )
            stream.close()
            return True
        except Exception:
            return False
        finally:
            pa.terminate()

    def print_mic_info(self, mic):
        pa = pyaudio.PyAudio()
        mic_info = pa.get_device_info_by_index(mic)
        print("\nMIC %s:" % (str(mic)))
        for k, v in sorted(mic_info.items()):
            print("%s: %s" % (k, v))
        pa.terminate()


def create_stream(
    on_data: Callable,
    device: Optional[int] = None,
    rate: Optional[int] = None,
    updates_per_second: int = 100,
):
    return PyAudioStream(on_data, device, rate, updates_per_second)
