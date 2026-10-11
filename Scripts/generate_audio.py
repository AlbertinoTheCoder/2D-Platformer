"""Generate original, short placeholder cues using Python's standard library."""
import math
import random
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "Assets/Audio"


def cue(name, duration, start, end, noise=0.0):
    rate = 22050
    rng = random.Random(name)
    phase = 0.0
    samples = bytearray()
    for i in range(int(duration * rate)):
        t = i / rate
        progress = t / duration
        frequency = start + (end - start) * progress
        phase += 2 * math.pi * frequency / rate
        envelope = min(1.0, t / .008) * (1 - progress) ** 1.5
        value = (math.sin(phase) * .65 + math.sin(phase * 2) * .1 + rng.uniform(-1, 1) * noise) * envelope * .25
        samples.extend(struct.pack("<h", int(max(-1, min(1, value)) * 32767)))
    with wave.open(str(DEST / f"S_{name}.wav"), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(samples)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for spec in [("Jump", .16, 280, 750, 0), ("Land", .1, 100, 50, .2),
                 ("Energy", .18, 750, 1500, 0), ("Damage", .22, 250, 60, .35),
                 ("EnemyDeath", .2, 170, 35, .3), ("Checkpoint", .4, 450, 1000, 0),
                 ("Complete", 1.1, 330, 990, 0)]:
        cue(*spec)
    print("Generated 7 original placeholder sound cues.")


if __name__ == "__main__":
    main()
