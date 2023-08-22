import wave
import struct
import winsound
import numpy as np


class Music:
    def __init__(self, channels, sampleRate, sampleWidth, data, normalized=False):
        self.channels = channels
        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth
        self.data: np.ndarray = data if normalized else self.normalize(data)
        print(len(data))
        print(len(self.data))

    @classmethod
    def from_file(cls, wavfile):
        with wave.open(wavfile, "rb") as music:
            return Music(music.getnchannels(), music.getframerate(), music.getsampwidth(),
                         music.readframes(music.getnframes()))

    @classmethod
    def copy(cls, music):
        return Music(music.channels, music.sampleRate, music.sampleWidth, music.data, normalized=True)

    def play(self):
        winsound.PlaySound(self.towav(), winsound.SND_MEMORY)

    def normalize(self, data: bytes) -> np.ndarray:
        normalized = np.frombuffer(data, dtype=float)

        map(lambda x: x / self.sampleWidth, normalized)
        return normalized

    def denormalize(self) -> bytes:
        denorm = np.copy(self.data)
        map(lambda x: x * self.sampleWidth, denorm)
        return denorm.tobytes()

    def towav(self):
        wav = [struct.pack('<4s', b'RIFF'), struct.pack('I', len(self.data) + 36), struct.pack('4s', b'WAVE'),
               struct.pack('4s', b'fmt '), struct.pack('IHHIIHH', 16, 1, self.channels,
                                                       self.sampleRate,
                                                       self.sampleWidth * self.sampleRate * self.channels,
                                                       self.sampleWidth * self.channels,
                                                       self.sampleWidth * 8),
               struct.pack('<4s', b'data'), struct.pack('I', len(self.data)), self.denormalize()]
        return b''.join(wav)

    def inverse_phase(self):
        denormalized = self.denormalize()
        data = bytearray(len(denormalized))
        for i in range(0, int(len(denormalized) / 2)):
            sample = int.from_bytes([denormalized[2 * i], denormalized[2 * i + 1]], "little", signed=True) * -1
            if sample < -32768:
                sample = 32768
            elif sample > 32767:
                sample = 32767
            samples = sample.to_bytes(2, "little", signed=True)
            data[2 * i] = samples[0]
            data[2 * i + 1] = samples[1]
        self.data = self.normalize(data)

    def integrate_pcm(self, lay):
        denormalized = self.denormalize()
        data = bytearray(len(denormalized))
        for i in range(0, int(len(denormalized) / 2)):
            sample1 = int.from_bytes([denormalized[2 * i], denormalized[2 * i + 1]], "little", signed=True)
            if sample1 < -32768:
                sample1 = 32768
            elif sample1 > 32767:
                sample1 = 32767
            sample2 = int.from_bytes([lay[2 * i], lay[2 * i + 1]], "little", signed=True)
            if sample2 < -32768:
                sample2 = 32768
            elif sample2 > 32767:
                sample2 = 32767

            samples = (sample1 + sample2).to_bytes(2, "little", signed=True)
            data[2 * i] = samples[0]
            data[2 * i + 1] = samples[1]
        self.data = self.normalize(data)
