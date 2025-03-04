import numpy as np
from scipy.io import wavfile
import imageio.v3 as imageio

# sampling frequency
FS = 44100  
# длина "точки" в секундах
BIT = 0.01

img_array = imageio.imread('img.png', mode='F')
print(img_array.shape)

data1 = []
data2 = []

ZERO = 0.7

for row in img_array:
    for i in row:
        el = 1 if i == 0 else ZERO
        data1 += [el] * int(BIT * FS)
        data2 += [ZERO] * int(BIT * FS)
    # возврат каретки в 2 раза быстрее, чем прямой ход
    data1 += [ZERO] * int(len(row) / 2.0 * BIT * FS)
    data2 += [1] * int(len(row) / 2.0 * BIT * FS)

data1 = np.array(data1, dtype=np.float32)
data2 = np.array(data2, dtype=np.float32)

t = np.arange(0, len(data1))

fc = 1000   # несущая
k = 0.15    # sensitivity
phi1 = (2 * np.pi * fc * t) + k * np.cumsum(data1)

fc = 2000   # несущая
k = 0.15    # sensitivity
phi2 = (2 * np.pi * fc * t) + k * np.cumsum(data2)

fm = np.cos(0.5 * phi1 + 0.5 * phi2)

wavfile.write('example.wav', FS, fm)
