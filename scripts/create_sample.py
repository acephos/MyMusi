"""Generate an original one-second 440 Hz tone; no downloaded music required."""
import math
from pathlib import Path
import struct
import wave
path=Path(__file__).resolve().parents[1]/'music'/'sample tone.wav'
path.parent.mkdir(exist_ok=True)
with wave.open(str(path),'wb') as output:
 output.setnchannels(1);output.setsampwidth(2);output.setframerate(16000)
 output.writeframes(b''.join(struct.pack('<h',int(8000*math.sin(2*math.pi*440*i/16000))) for i in range(16000)))
print(path)
