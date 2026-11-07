"""Enrol Jaco or Edd from at least three consented 16-kHz mono PCM16 WAV files."""
import argparse
import wave
from .speakers import SpeakerStore, WeSpeakerEmbedder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("speaker", choices=["Jaco", "Edd"])
    parser.add_argument("recordings", nargs="+")
    parser.add_argument("--profiles", default="/opt/declan-stt/speakers.json")
    parser.add_argument("--model", required=True, help="Locally provisioned WeSpeaker ONNX model")
    args = parser.parse_args()
    if len(args.recordings) < 3:
        parser.error("At least three different WAV recordings are required")
    samples = []
    for path in args.recordings:
        with wave.open(path, "rb") as wav:
            if (wav.getframerate(), wav.getsampwidth(), wav.getnchannels(),
                wav.getcomptype()) != (16000, 2, 1, "NONE"):
                parser.error(f"{path}: expected 16-kHz mono PCM16 WAV")
            samples.append(wav.readframes(wav.getnframes()))
    store = SpeakerStore(args.profiles, WeSpeakerEmbedder(args.model))
    count = store.enrol(args.speaker, samples)
    print(f"Enrolled {args.speaker} with {count} recordings")


if __name__ == "__main__":
    main()
