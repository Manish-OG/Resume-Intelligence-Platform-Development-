"""
Benchmark utility for the PDF parser.

This module benchmarks the PDF parser by executing it multiple times
and reporting summary timing statistics.
"""

from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path

from src.parser.pdf_parser import extract_text


def benchmark(pdf_path: Path, runs: int = 10) -> dict[str, float | int | str]:
    """
    Benchmark the PDF parser.

    Parameters
    ----------
    pdf_path : Path
        Path to the PDF file.
    runs : int, optional
        Number of benchmark iterations.

    Returns
    -------
    dict
        Benchmark summary statistics.
    """

    extract_text(pdf_path)  # warm-up run, excluded: first call is consistently ~2x slower

    timings: list[float] = []

    for _ in range(runs):
        start = time.perf_counter()

        extract_text(pdf_path)

        elapsed_ms = (time.perf_counter() - start) * 1000
        timings.append(elapsed_ms)

    return {
        "file": pdf_path.name,
        "runs": runs,
        "average_ms": statistics.mean(timings),
        "minimum_ms": min(timings),
        "maximum_ms": max(timings),
        "std_dev_ms": statistics.stdev(timings) if runs > 1 else 0.0,
    }


def print_report(results: dict[str, float | int | str]) -> None:
    """
    Print benchmark results.
    """

    print("\n" + "=" * 50)
    print("PDF Parser Benchmark")
    print("=" * 50)

    print(f"File      : {results['file']}")
    print(f"Runs      : {results['runs']}")
    print(f"Average   : {results['average_ms']:.2f} ms")
    print(f"Minimum   : {results['minimum_ms']:.2f} ms")
    print(f"Maximum   : {results['maximum_ms']:.2f} ms")
    print(f"Std. Dev. : {results['std_dev_ms']:.2f} ms")

    print("=" * 50)


def main() -> None:
    """
    Command-line entry point.
    """

    parser = argparse.ArgumentParser(
        description="Benchmark the PDF parser."
    )

    parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF file.",
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of benchmark iterations (default: 10).",
    )

    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1.")

    results = benchmark(args.pdf, args.runs)

    print_report(results)


if __name__ == "__main__":
    main()