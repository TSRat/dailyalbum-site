"""Build a compact CN lookup snapshot from ip2region's published source data.

Usage: python3 build_ranges.py /path/to/ip2region/data
The source data is licensed Apache-2.0 OR MIT. Retain the adjacent LICENSE file.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def country_ranges(source: Path, version: int) -> list[list[int]]:
    selected: list[list[int]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        columns = line.split("|")
        if len(columns) < 7 or columns[-1] != "CN":
            continue
        start = ipaddress.ip_address(columns[0])
        end = ipaddress.ip_address(columns[1])
        if start.version != version or end.version != version or start > end:
            raise ValueError(f"Invalid range in {source}: {line[:100]}")
        selected.append([int(start), int(end)])
    selected.sort()
    merged: list[list[int]] = []
    for start, end in selected:
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def main() -> None:
    directory = Path(sys.argv[1]).resolve()
    sources = (directory / "ipv4_source.txt", directory / "ipv6_source.txt")
    if not all(path.is_file() for path in sources):
        raise SystemExit("Expected ipv4_source.txt and ipv6_source.txt")
    result = {
        "source": "https://github.com/lionsoul2014/ip2region/tree/master/data",
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ipv4": country_ranges(sources[0], 4),
        "ipv6": country_ranges(sources[1], 6),
    }
    output = Path(__file__).with_name("cn_ranges.json")
    output.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {output}: {len(result['ipv4'])} IPv4, {len(result['ipv6'])} IPv6 ranges")


if __name__ == "__main__":
    main()
