"""Local opt-in voiceprint enrolment and conservative identification.

Voice embeddings are biometric data. Store privately and never use for access
control. Unenrolled speakers and model failures always return Unknown.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
import threading
import wave
from pathlib import Path
from typing import Protocol


class Embedder(Protocol):
    def embed(self, pcm: bytes) -> list[float]: ...


def normalise(values: list[float]) -> list[float]:
    if not values or not all(math.isfinite(x) for x in values):
        raise ValueError("invalid embedding")
    length = math.sqrt(sum(x * x for x in values))
    if length <= 1e-8:
        raise ValueError("empty embedding")
    return [x / length for x in values]


class WeSpeakerEmbedder:
    """Use a locally provisioned WeSpeaker ONNX model, without silent downloads."""

    def __init__(self, model_path: str):
        import wespeakerruntime as wespeaker
        if not Path(model_path).is_file():
            raise FileNotFoundError(f"Speaker model missing: {model_path}")
        self._model = wespeaker.Speaker(lang="en", onnx_path=model_path)
        self._lock = threading.Lock()

    def embed(self, pcm: bytes) -> list[float]:
        if len(pcm) < 16000 * 2:
            raise ValueError("at least one second of speech required")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            filename = f.name
        try:
            with wave.open(filename, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(pcm)
            # Decode PCM WAV with SoundFile to avoid TorchCodec's optional
            # dependency in newer TorchAudio releases.
            import soundfile as sf
            import torch
            import torchaudio

            def load_pcm_wav(path, *args, **kwargs):
                audio, sample_rate = sf.read(path, dtype="float32", always_2d=True)
                return torch.from_numpy(audio.T.copy()), sample_rate

            with self._lock:
                original_load = torchaudio.load
                try:
                    torchaudio.load = load_pcm_wav
                    result = self._model.extract_embedding(filename)
                finally:
                    torchaudio.load = original_load
            return normalise([float(x) for x in result.flatten()])
        finally:
            Path(filename).unlink(missing_ok=True)


class SpeakerStore:
    """Persist embeddings only, no raw audio; replace profile file atomically."""

    def __init__(self, path: str, embedder: Embedder | None,
                 *, threshold: float = .75, margin: float = .08):
        if not 0 <= threshold <= 1 or not 0 <= margin <= 1:
            raise ValueError("invalid speaker thresholds")
        self.path = Path(path)
        self.embedder = embedder
        self.threshold = threshold
        self.margin = margin
        self._lock = threading.Lock()
        self._profiles = self._load()

    def _load(self) -> dict[str, list[list[float]]]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not set(data).issubset({"Jaco", "Edd"}):
            raise ValueError("invalid profile file")
        return {name: [normalise([float(x) for x in sample]) for sample in samples]
                for name, samples in data.items()}

    def enrol(self, name: str, samples: list[bytes]) -> int:
        if name not in {"Jaco", "Edd"}:
            raise ValueError("only Jaco and Edd may be enrolled")
        if self.embedder is None:
            raise RuntimeError("speaker model unavailable")
        if len(samples) < 3:
            raise ValueError("provide at least three recordings")
        embeddings = [normalise(self.embedder.embed(pcm)) for pcm in samples]
        if len({len(x) for x in embeddings}) != 1:
            raise ValueError("embedding dimensions differ")
        with self._lock:
            updated = {**self._profiles, name: embeddings}
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w", dir=self.path.parent, prefix=".speakers-",
                delete=False, encoding="utf-8"
            ) as stream:
                filename = stream.name
                os.chmod(filename, 0o600)
                json.dump(updated, stream)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.replace(filename, self.path)
            finally:
                Path(filename).unlink(missing_ok=True)
            self._profiles = updated
        return len(embeddings)

    def identify(self, pcm: bytes) -> tuple[str, float]:
        if self.embedder is None or not self._profiles:
            return "Unknown", 0.0
        try:
            query = normalise(self.embedder.embed(pcm))
        except Exception:
            return "Unknown", 0.0
        scores = []
        for name, samples in self._profiles.items():
            matching = [sum(a*b for a, b in zip(query, sample))
                        for sample in samples if len(query) == len(sample)]
            if matching:
                scores.append((max(matching), name))
        scores.sort(reverse=True)
        if not scores:
            return "Unknown", 0.0
        best, name = scores[0]
        second = scores[1][0] if len(scores) > 1 else -1.0
        if best < self.threshold or best - second < self.margin:
            return "Unknown", 0.0
        return name, max(0.0, min(1.0, best))
