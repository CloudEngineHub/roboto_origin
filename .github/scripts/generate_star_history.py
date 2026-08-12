#!/usr/bin/env python3
"""Generate an SVG star-history chart for a GitHub repository."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime
from html import escape
from pathlib import Path
from typing import Any


API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
PER_PAGE = 100


def parse_github_date(value: str) -> date:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def request_json(url: str, token: str, accept: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "Authorization": f"Bearer {token}",
            "User-Agent": "roboto-origin-star-history",
            "X-GitHub-Api-Version": API_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed ({error.code}) for {url}: {body}"
        ) from error


def fetch_repository(repository: str, token: str) -> dict[str, Any]:
    data = request_json(
        f"{API_ROOT}/repos/{repository}", token, "application/vnd.github+json"
    )
    if not isinstance(data, dict):
        raise RuntimeError("GitHub returned invalid repository metadata")
    return data


def fetch_stargazer_dates(repository: str, token: str) -> list[date]:
    dates: list[date] = []
    page = 1
    while True:
        url = (
            f"{API_ROOT}/repos/{repository}/stargazers"
            f"?per_page={PER_PAGE}&page={page}"
        )
        data = request_json(url, token, "application/vnd.github.star+json")
        if not isinstance(data, list):
            raise RuntimeError("GitHub returned an invalid stargazers response")

        for item in data:
            starred_at = item.get("starred_at") if isinstance(item, dict) else None
            if not starred_at:
                raise RuntimeError(
                    "The stargazers response has no timestamps. Ensure the workflow "
                    "token can read repository metadata."
                )
            dates.append(parse_github_date(starred_at))

        if len(data) < PER_PAGE:
            break
        page += 1

    return dates


def fetch_history(repository: str, token: str) -> tuple[date, list[date]]:
    # A star can be added or removed during pagination. Retry once rather than
    # publishing a chart that silently contains an incomplete history.
    for attempt in range(2):
        metadata = fetch_repository(repository, token)
        created_at = parse_github_date(metadata["created_at"])
        starred_dates = fetch_stargazer_dates(repository, token)
        current_metadata = fetch_repository(repository, token)
        expected_count = int(current_metadata["stargazers_count"])
        if len(starred_dates) == expected_count:
            return created_at, starred_dates
        if attempt == 0:
            continue
        raise RuntimeError(
            "Stargazer history changed while it was being fetched: "
            f"received {len(starred_dates)} entries, expected {expected_count}."
        )
    raise AssertionError("unreachable")


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


def history_points(created_at: date, starred_dates: list[date]) -> list[tuple[date, int]]:
    points: list[tuple[date, int]] = [(created_at, 0)]
    total = 0
    for day, count in sorted(Counter(starred_dates).items()):
        total += count
        points.append((day, total))
    return points


def render_svg(repository: str, created_at: date, starred_dates: list[date]) -> str:
    width, height = 960, 520
    left, right, top, bottom = 78, 28, 82, 66
    plot_width = width - left - right
    plot_height = height - top - bottom
    points = history_points(created_at, starred_dates)
    first_day = min(day for day, _ in points)
    last_day = max(day for day, _ in points)
    day_span = max(1, (last_day - first_day).days)
    maximum, y_step = y_axis(len(starred_dates))

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
    last_x, last_y = coordinates[-1]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">Star history for {safe_repository}</title>
  <desc id="description">{len(starred_dates)} stars since {created_at.isoformat()}</desc>
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
  <text x="{left}" y="60" class="subtitle">{safe_repository} · {len(starred_dates)} stars</text>
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
        default=os.environ.get("GITHUB_REPOSITORY", "Roboparty/roboto_origin"),
        help="GitHub repository in OWNER/REPO form",
    )
    parser.add_argument(
        "--output", default="assets/star-history.svg", help="SVG output path"
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return 2

    created_at, starred_dates = fetch_history(args.repository, token)
    svg = render_svg(args.repository, created_at, starred_dates)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(svg, encoding="utf-8", newline="\n")
    temporary.replace(output)
    print(f"Wrote {output} with {len(starred_dates)} stars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
