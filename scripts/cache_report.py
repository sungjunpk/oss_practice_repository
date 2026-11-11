"""Actions 실행의 시간 측정 집계.

사용:
  python scripts/cache_report.py bench <run_id>      # cache-benchmark 결과 표
  python scripts/cache_report.py wall <run_id>...    # 실행별 전체 소요 시간
"""
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime


def t(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def jobs(run_id):
    out = subprocess.run(["gh", "run", "view", run_id, "--json", "jobs,createdAt,updatedAt"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def bench(run_id):
    rows = {}   # (extras, kind) -> [(step_sec, job_sec)]
    for j in jobs(run_id)["jobs"]:
        m = re.match(r"(cold|warm) \((.+) n=\d\)", j["name"])
        if not m:
            continue
        step = next(s for s in j["steps"] if s["name"].startswith("Run ./.github/actions/setup-env"))
        rows.setdefault((m[2], m[1]), []).append(
            ((t(step["completedAt"]) - t(step["startedAt"])).total_seconds(),
             (t(j["completedAt"]) - t(j["startedAt"])).total_seconds()))
    print("| 시나리오 | 구분 | setup 단계 (초, 3회) | 중앙값 | 잡 전체 중앙값 |")
    print("|---|---|---|---|---|")
    for extras in sorted({k[0] for k in rows}):
        med = {}
        for kind in ("cold", "warm"):
            v = rows[(extras, kind)]
            med[kind] = (statistics.median(x[0] for x in v), statistics.median(x[1] for x in v))
            print(f"| `{extras}` | {kind} | {', '.join(f'{x[0]:.0f}' for x in v)} "
                  f"| {med[kind][0]:.1f} | {med[kind][1]:.1f} |")
        for i, name in enumerate(("setup 단계", "잡 전체")):
            c, w = med["cold"][i], med["warm"][i]
            print(f"\n- `{extras}` {name}: {c:.1f}s → {w:.1f}s, **{(c - w) / c * 100:+.1f}% 단축**")


def wall(ids):
    for rid in ids:
        d = jobs(rid)
        js = d["jobs"]
        wall_s = (max(t(j["completedAt"]) for j in js) - min(t(j["startedAt"]) for j in js)).total_seconds()
        total = sum((t(j["completedAt"]) - t(j["startedAt"])).total_seconds() for j in js)
        print(f"run {rid}: 잡 {len(js)}개, wall-clock {wall_s:.0f}s, 잡 시간 합 {total:.0f}s")


if __name__ == "__main__":
    {"bench": lambda a: bench(a[0]), "wall": wall}[sys.argv[1]](sys.argv[2:])
