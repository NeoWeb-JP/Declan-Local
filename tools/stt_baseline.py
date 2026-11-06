"""Offline, dependency-free baseline metrics for consented STT transcripts.

Input is a local JSON list of records with reference, hypothesis, and optional
room and command_success. No audio or personal data is uploaded or logged.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


def words(text):
    return re.findall(r"[\w']+", text.casefold())


def edit_distance(reference, hypothesis):
    previous = list(range(len(hypothesis) + 1))
    for i, word in enumerate(reference, 1):
        current = [i]
        for j, candidate in enumerate(hypothesis, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (word != candidate)))
        previous = current
    return previous[-1]


def evaluate(records):
    groups = defaultdict(lambda: {"utterances": 0, "words": 0, "errors": 0,
                                  "command_attempts": 0, "command_successes": 0})
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Every record must be an object")
        if not isinstance(record.get("reference"), str) or not isinstance(record.get("hypothesis"), str):
            raise ValueError("Records require reference and hypothesis strings")
        room = record.get("room", "unspecified")
        if not isinstance(room, str):
            raise ValueError("Room must be a string")
        reference, hypothesis = words(record["reference"]), words(record["hypothesis"])
        for key in ("all", "room:" + room):
            metrics = groups[key]
            metrics["utterances"] += 1
            metrics["words"] += len(reference)
            metrics["errors"] += edit_distance(reference, hypothesis)
            if "command_success" in record:
                if not isinstance(record["command_success"], bool):
                    raise ValueError("command_success must be boolean")
                metrics["command_attempts"] += 1
                metrics["command_successes"] += int(record["command_success"])
    return {key: {**value,
                  "wer": round(value["errors"] / value["words"], 4) if value["words"] else None,
                  "command_success_rate": round(value["command_successes"] / value["command_attempts"], 4)
                  if value["command_attempts"] else None}
            for key, value in sorted(groups.items())}


def main():
    parser = argparse.ArgumentParser(description="Evaluate consented STT transcript pairs locally")
    parser.add_argument("input", type=Path, help="JSON array of reviewed reference/hypothesis pairs")
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.input.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
