#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.ranking.dataset import load_rows
from ml.ranking.trainer import train_ranker


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a versioned LightGBM recommendation ranker.")
    parser.add_argument("--input", type=Path, default=Path("ml/artifacts/features/v001/training.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("ml/artifacts/ranker/v001"))
    parser.add_argument("--version", default="ranker-v001")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-boost-round", type=int, default=80)
    args = parser.parse_args()

    rows = load_rows(args.input)
    metrics = train_ranker(
        rows,
        args.output,
        version=args.version,
        seed=args.seed,
        num_boost_round=args.num_boost_round,
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
