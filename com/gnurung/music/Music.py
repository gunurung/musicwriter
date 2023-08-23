import wave
import struct
import winsound
import numpy as np

class Music:
    def __init__(self, channels, sampleRate, sampleWidth, data, normalized=False):
        self.channels = channels
        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth  # byte 몇개가 필요한지
        self.amps: np.ndarray = data if normalized else self.normalize(data)

    @classmethod
    def from_file(cls, wavfile):
        with wave.open(wavfile, "rb") as music:
            return Music(music.getnchannels(), music.getframerate(), music.getsampwidth(),
                         music.readframes(music.getnframes()))

    @classmethod
    def copy(cls, music):
        return Music(music.channels, music.sampleRate, music.sampleWidth, music.amps.copy(), normalized=True)

    def play(self):
        winsound.PlaySound(self.towav(), winsound.SND_MEMORY)

    def normalize(self, data: bytes) -> np.ndarray:
        size = int(len(data) / self.sampleWidth)
        max_height = 2 ** (self.sampleWidth * 8) / 2
        normalized = np.empty(size)
        for i in range(0, size):
            sample = int.from_bytes(data[self.sampleWidth * i: self.sampleWidth * (i+1)], "little", signed=True)
            normalized[i] = sample / max_height
        print(normalized)
        return normalized

    def denormalize(self) -> bytearray:
        denorm = bytearray(len(self.amps) * self.sampleWidth)
        max_height = int(2 ** (self.sampleWidth * 8) / 2)
        for i in range(0, len(self.amps)):
            sample = int(self.amps[i] * (2 ** (self.sampleWidth * 8)))
            if sample < -max_height:
                sample = -max_height
            elif sample >= max_height:
                sample = max_height-1

            samples = sample.to_bytes(self.sampleWidth, "little", signed=True)

            for j in range(0, len(samples)):
                denorm[self.sampleWidth * i + j] = samples[j]
        return denorm

    def towav(self):
        wav = [struct.pack('<4s', b'RIFF'), struct.pack('I', len(self.amps) * self.sampleWidth + 36), struct.pack('4s', b'WAVE'),
               struct.pack('4s', b'fmt '), struct.pack('IHHIIHH', 16, 1, self.channels,
                                                       self.sampleRate,
                                                       self.sampleWidth * self.sampleRate * self.channels,
                                                       self.sampleWidth * self.channels,
                                                       self.sampleWidth * 8),
               struct.pack('<4s', b'data'), struct.pack('I', len(self.amps) * self.sampleWidth), self.denormalize()]
        return b''.join(wav)

    def inverse_phase(self):
        for i in range(0, len(self.amps)):
            self.amps[i] *= -1

    def integrate_pcm(self, music):
        self.amps = self.amps + music.amps
