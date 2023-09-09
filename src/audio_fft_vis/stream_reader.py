from typing import Optional
import time
import numpy as np

from audio_fft_vis.utils import NumpyDataBuffer
from .audio_stream import AudioStream
from .utils import NumpyDataBuffer, round_up_to_even
from .pyaudio_stream import create_stream


class StreamReader:
    _stream: AudioStream
    _data_buffer: NumpyDataBuffer

    def __init__(
        self,
        device: Optional[int] = None,
        rate: Optional[int] = None,
        updates_per_second: int = 1000,
    ):
        self._stream_start_time = None
        self._new_data = False
        self._stream = create_stream(self.on_data, device, rate, updates_per_second)

    @property
    def rate(self):
        """The rate property."""
        return self._stream.rate

    @property
    def frames_per_buffer(self):
        """The rate property."""
        return self._stream.frames_per_buffer

    @property
    def stream_start_time(self):
        """The stream_start_time property."""
        return self._stream_start_time

    def get_most_recent_data(self, read_size: int):
        self._new_data = False
        return self._data_buffer.get_most_recent(read_size)

    def has_new_data(self) -> bool:
        return self._new_data

    def on_data(self, in_data):
        self._data_buffer.append_data(np.frombuffer(in_data, dtype=np.int16))
        self._new_data = True

    def start(self):
        buff_size = round_up_to_even(self._stream.updates_per_second / 2)
        self._data_buffer = NumpyDataBuffer(buff_size, self._stream.frames_per_buffer)
        self._stream.start()
        self._stream_start_time = time.time()

    def stop(self):
        self._stream.stop()
