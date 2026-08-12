#!/usr/bin/env python3
"""Update a token-free daily star-count history and render it as SVG."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def request_repository(repository: str) -> dict[str, Any]:
    """Read public repository metadata, optionally using a short-lived token."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "roboto-origin-star-history",
        "X-GitHub-Api-Version": API_VERSION,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"{API_ROOT}/repos/{repository}",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed ({error.code}): {body}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"GitHub API request failed: {error.reason}") from error

    if not isinstance(data, dict):
        raise RuntimeError("GitHub returned invalid repository metadata")
    return data


def load_history(path: Path, repository: str) -> tuple[date, list[tuple[date, int]]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read star history from {path}: {error}") from error

    if not isinstance(data, dict) or data.get("repository") != repository:
        raise RuntimeError(f"{path} does not describe {repository}")

    try:
        created_at = parse_date(data["created_at"])
        raw_snapshots = data["snapshots"]
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError(f"{path} has invalid metadata") from error

    if not isinstance(raw_snapshots, list):
        raise RuntimeError(f"{path} has invalid snapshots")

    snapshots: list[tuple[date, int]] = []
    for item in raw_snapshots:
        try:
            snapshot_day = parse_date(item["date"])
            stars = int(item["stars"])
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError(f"{path} has an invalid snapshot") from error
        if stars < 0 or snapshot_day < created_at:
            raise RuntimeError(f"{path} has an invalid snapshot")
        snapshots.append((snapshot_day, stars))

    if not snapshots:
        raise RuntimeError(f"{path} contains no snapshots")
    if snapshots != sorted(snapshots) or len({day for day, _ in snapshots}) != len(
        snapshots
    ):
        raise RuntimeError(f"{path} snapshots must be unique and sorted")
    return created_at, snapshots


def update_history(
    snapshots: list[tuple[date, int]], snapshot_day: date, stars: int
) -> list[tuple[date, int]]:
    if stars < 0:
        raise RuntimeError("Star count cannot be negative")
    if snapshot_day < snapshots[-1][0]:
        raise RuntimeError(
            f"Snapshot date {snapshot_day} precedes the latest stored snapshot "
            f"{snapshots[-1][0]}"
        )
    if snapshot_day == snapshots[-1][0]:
        return [*snapshots[:-1], (snapshot_day, stars)]
    return [*snapshots, (snapshot_day, stars)]


def write_history(
    path: Path,
    repository: str,
    created_at: date,
    snapshots: list[tuple[date, int]],
) -> None:
    data = {
        "repository": repository,
        "created_at": created_at.isoformat(),
        "snapshots": [
            {"date": snapshot_day.isoformat(), "stars": stars}
            for snapshot_day, stars in snapshots
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def y_axis(maximum: int, tick_count: int = 5) -> tuple[int, int]:
    if maximum <= 0:
        return 1, 1
    rough_step = maximum / tick_count
    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized = rough_step / magnitude
    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 5:
        nice = 5
    else:
        nice = 10
    step = max(1, int(nice * magnitude))
    ceiling = int(math.ceil(maximum / step) * step)
    return ceiling, step


def render_svg(
    repository: str,
    created_at: date,
    snapshots: list[tuple[date, int]],
) -> str:
    width, height = 960, 520
    left, right, top, bottom = 78, 28, 82, 66
    plot_width = width - left - right
    plot_height = height - top - bottom
    points = [(created_at, 0), *snapshots]
    first_day = created_at
    last_day = snapshots[-1][0]
    day_span = max(1, (last_day - first_day).days)
    maximum, y_step = y_axis(max(stars for _, stars in points))

    def x(day: date) -> float:
        return left + ((day - first_day).days / day_span) * plot_width

    def y(value: int) -> float:
        return top + plot_height - (value / maximum) * plot_height

    coordinates = [(x(day), y(value)) for day, value in points]
    line_points = " ".join(f"{px:.2f},{py:.2f}" for px, py in coordinates)
    area_points = (
        f"{left},{top + plot_height} {line_points} "
        f"{coordinates[-1][0]:.2f},{top + plot_height}"
    )

    y_grid: list[str] = []
    value = 0
    while value <= maximum:
        py = y(value)
        y_grid.append(
            f'<line x1="{left}" y1="{py:.2f}" x2="{left + plot_width}" '
            f'y2="{py:.2f}" class="grid"/>'
            f'<text x="{left - 14}" y="{py + 5:.2f}" class="axis" '
            f'text-anchor="end">{value}</text>'
        )
        value += y_step

    x_grid: list[str] = []
    for index in range(6):
        offset = round(day_span * index / 5)
        tick_day = date.fromordinal(first_day.toordinal() + offset)
        px = x(tick_day)
        label = tick_day.strftime("%Y-%m" if day_span > 180 else "%m-%d")
        x_grid.append(
            f'<line x1="{px:.2f}" y1="{top}" x2="{px:.2f}" '
            f'y2="{top + plot_height}" class="grid"/>'
            f'<text x="{px:.2f}" y="{top + plot_height + 32}" class="axis" '
            f'text-anchor="middle">{label}</text>'
        )

    safe_repository = escape(repository)
    latest_stars = snapshots[-1][1]
    last_x, last_y = coordinates[-1]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">Star history for {safe_repository}</title>
  <desc id="description">{latest_stars} stars as of {last_day.isoformat()}</desc>
  <defs>
    <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2f81f7" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="#2f81f7" stop-opacity="0.04"/>
    </linearGradient>
  </defs>
  <style>
    .axis {{ fill: #8b949e; font: 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .grid {{ stroke: #30363d; stroke-width: 1; }}
    .title {{ fill: #f0f6fc; font: 600 22px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .subtitle {{ fill: #8b949e; font: 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  </style>
  <rect width="100%" height="100%" rx="12" fill="#0d1117"/>
  <text x="{left}" y="36" class="title">Star History</text>
  <text x="{left}" y="60" class="subtitle">{safe_repository} · {latest_stars} stars · daily snapshots</text>
  {''.join(y_grid)}
  {''.join(x_grid)}
  <polygon points="{area_points}" fill="url(#area)"/>
  <polyline points="{line_points}" fill="none" stroke="#2f81f7" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="{last_x:.2f}" cy="{last_y:.2f}" r="5" fill="#58a6ff" stroke="#0d1117" stroke-width="2"/>
</svg>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        default="Roboparty/roboto_origin",
        help="GitHub repository in OWNER/REPO form",
    )
    parser.add_argument(
        "--history",
        default=".github/data/star-history.json",
        help="Daily snapshot JSON file to update",
    )
    parser.add_argument(
        "--output", default="assets/star-history.svg", help="SVG output path"
    )
    parser.add_argument(
        "--current-stars",
        type=int,
        help="Override the public API count for deterministic tests",
    )
    parser.add_argument(
        "--today", help="Override the UTC snapshot date for deterministic tests"
    )
    args = parser.parse_args()

    history_path = Path(args.history)
    output_path = Path(args.output)
    created_at, snapshots = load_history(history_path, args.repository)

    if args.current_stars is None:
        metadata = request_repository(args.repository)
        current_stars = int(metadata["stargazers_count"])
        repository_created_at = datetime.fromisoformat(
            metadata["created_at"].replace("Z", "+00:00")
        ).date()
        if repository_created_at != created_at:
            raise RuntimeError(
                f"Stored creation date {created_at} does not match GitHub "
                f"metadata {repository_created_at}"
            )
    else:
        current_stars = args.current_stars

    snapshot_day = (
        parse_date(args.today)
        if args.today
        else datetime.now(timezone.utc).date()
    )
    snapshots = update_history(snapshots, snapshot_day, current_stars)
    write_history(history_path, args.repository, created_at, snapshots)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_svg(args.repository, created_at, snapshots),
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"Wrote {output_path} and {history_path} with "
        f"{current_stars} stars for {snapshot_day}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
