"""Offline opt-in STT transcript correction review.

Only explicitly supplied JSONL records are processed. This tool never captures
microphones, stores audio, or uploads data. Reviewed examples can be exported
to the STT baseline evaluator. Do not include personal secrets.
"""
import argparse
import json
from pathlib import Path

REQUIRED = {"reference", "hypothesis", "reviewed", "consent"}


def approved(records):
    output = []
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict) or not REQUIRED.issubset(record):
            raise ValueError(f"Invalid record {index}")
        if record["consent"] is not True or record["reviewed"] is not True:
            continue
        reference, hypothesis = record["reference"], record["hypothesis"]
        if not isinstance(reference, str) or not isinstance(hypothesis, str):
            raise ValueError(f"Invalid transcripts at record {index}")
        if not reference.strip():
            continue
        result = {"reference": reference, "hypothesis": hypothesis}
        if "room" in record:
            if not isinstance(record["room"], str):
                raise ValueError(f"Invalid room at record {index}")
            result["room"] = record["room"]
        if "command_success" in record:
            if not isinstance(record["command_success"], bool):
                raise ValueError(f"Invalid command_success at record {index}")
            result["command_success"] = record["command_success"]
        output.append(result)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Locally maintained JSONL review records")
    parser.add_argument("output", type=Path, help="Output JSON for stt_baseline.py")
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    # Refuse to overwrite an existing dataset.
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(approved(records), handle, indent=2)


if __name__ == "__main__":
    main()
