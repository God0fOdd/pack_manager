from __future__ import annotations

import wave

SENTINEL = "<END_SECRET>"


def _to_bits(data: bytes) -> list[int]:
    bits: list[int] = []
    for byte in data:
        bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
    return bits


def _bits_to_bytes(bits: list[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i : i + 8]
        if len(chunk) < 8:
            break
        value = 0
        for bit in chunk:
            value = (value << 1) | bit
        out.append(value)
    return bytes(out)


def embed_secret_in_wav(input_wav: str, output_wav: str, secret_text: str) -> None:
    payload = (secret_text + SENTINEL).encode("utf-8")
    bits = _to_bits(payload)

    with wave.open(input_wav, "rb") as wav:
        params = wav.getparams()
        frames = bytearray(wav.readframes(wav.getnframes()))

    if len(bits) > len(frames):
        raise ValueError("Audio file is too small for this secret.")

    for i, bit in enumerate(bits):
        frames[i] = (frames[i] & 0xFE) | bit

    with wave.open(output_wav, "wb") as wav:
        wav.setparams(params)
        wav.writeframes(frames)


def extract_secret_from_wav(wav_file: str) -> str:
    with wave.open(wav_file, "rb") as wav:
        frames = bytearray(wav.readframes(wav.getnframes()))

    bits = [sample & 1 for sample in frames]
    data = _bits_to_bytes(bits)
    text = data.decode("utf-8", errors="ignore")
    if SENTINEL not in text:
        raise ValueError("No embedded secret found.")
    return text.split(SENTINEL, 1)[0]


def can_embed(input_wav: str, secret_text: str) -> bool:
    with wave.open(input_wav, "rb") as wav:
        capacity = wav.getnframes() * wav.getnchannels() * wav.getsampwidth()
    needed = len((secret_text + SENTINEL).encode("utf-8")) * 8
    return needed <= capacity
