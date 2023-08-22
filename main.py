import numpy as np
import tensorflow as tf
import keras
import asyncio
from com.gnurung.music.Music import Music

print(tf.version)
music = Music.from_file("C:\\Users\\gw712\\Desktop\\Project-V\\input.wav")
music_inv = Music.copy(music)
music_inv.inverse_phase()

print("play")
music_inv.play()
music.sampleWidth = 8
music.play()