"""DORA 4대 지표 수집기 — GitHub Actions 실행 이력 + git 로그 + incident 이슈로 계산.

정의 (trunk-based, main 푸시 = 배포):
  - Deployment        : dora.yml 워크플로우의 main push 실행 1건
  - Lead Time         : 배포에 포함된 커밋의 author 시각 → 배포(run 생성) 시각
  - Change Failure    : `incident` 라벨 이슈 수 / 배포 수
  - MTTR              : incident 이슈 open → close 시간

출력: dora/metrics.json, dora/dashboard.png, dora/REPORT.md
사용: GITHUB_REPOSITORY=owner/repo [GITHUB_TOKEN=...] python scripts/dora.py
"""
import json, os, statistics, subprocess, sys, urllib.request
from datetime import datetime, timedelta, timezone

REPO = os.environ.get("GITHUB_REPOSITORY", "sungjunpk/oss_practice_repository")
TOKEN = os.environ.get("GITHUB_TOKEN")
WORKFLOW = "dora.yml"
BOT = "github-actions[bot]"
WEEKS = 12
OUT = "dora"
NOW = datetime.now(timezone.utc)

# DORA 2023 기준 (elite, high, medium) 경계. 작을수록 좋은 지표는 lower=True.
TIERS = {
    "deploys_per_week": ((7, 1, 0.25), False),
    "lead_time_hours": ((24, 24 * 7, 24 * 30), True),
    "mttr_hours": ((1, 24, 24 * 7), True),
    "change_failure_rate": ((0.05, 0.10, 0.15), True),
}


def tier(metric, value):
    if value is None:
        return "N/A"
    bounds, lower = TIERS[metric]
    for name, b in zip(("Elite", "High", "Medium"), bounds):
        if (value < b) if lower else (value >= b):
            return name
    return "Low"


def api(path):
    """GitHub REST GET, 모든 페이지를 합쳐 반환."""
    items, url = [], f"https://api.github.com/repos/{REPO}/{path}"
    while url:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(req) as r:
            body = json.load(r)
            items += body["workflow_runs"] if isinstance(body, dict) else body
            nxt = [p for p in r.headers.get("Link", "").split(",") if 'rel="next"' in p]
            url = nxt[0][nxt[0].index("<") + 1 : nxt[0].index(">")] if nxt else None
    return items


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def commits(prev, head):
    """prev..head 범위 커밋의 author 시각 (봇 커밋 제외). prev 가 없으면 head 만."""
    rng = f"{prev}..{head}" if prev else f"-1 {head}"
    out = subprocess.run(f"git log --no-merges --format=%at%x09%an {rng}".split(),
                         capture_output=True, text=True).stdout
    return [datetime.fromtimestamp(int(t), timezone.utc)
            for t, a in (l.split("\t", 1) for l in out.splitlines()) if a != BOT]


def collect():
    runs = sorted(api(f"actions/workflows/{WORKFLOW}/runs?branch=main&event=push&per_page=100"),
                  key=lambda r: r["created_at"])
    deploys, prev = [], None
    for r in runs:
        at = ts(r["created_at"])
        leads = [(at - c).total_seconds() / 3600 for c in commits(prev, r["head_sha"])]
        deploys.append({"sha": r["head_sha"], "at": r["created_at"], "lead_hours": leads})
        prev = r["head_sha"]
    incidents = [{"number": i["number"], "title": i["title"], "opened": i["created_at"],
                  "closed": i["closed_at"]}
                 for i in api("issues?labels=incident&state=all&per_page=100")
                 if "pull_request" not in i]
    return deploys, incidents


def summarize(deploys, incidents, start, end):
    """[start, end) 구간의 4대 지표."""
    d = [x for x in deploys if start <= ts(x["at"]) < end]
    inc = [x for x in incidents if start <= ts(x["opened"]) < end]
    leads = [h for x in d for h in x["lead_hours"]]
    fixed = [(ts(x["closed"]) - ts(x["opened"])).total_seconds() / 3600 for x in inc if x["closed"]]
    m = {
        "deployments": len(d),
        "deploys_per_week": round(len(d) / ((end - start).days / 7), 2),
        "lead_time_hours": round(statistics.median(leads), 2) if leads else None,
        "mttr_hours": round(statistics.mean(fixed), 2) if fixed else None,
        "change_failure_rate": round(min(len(inc) / len(d), 1), 3) if d else None,
        "incidents": len(inc),
    }
    m["tiers"] = {k: tier(k, m[k]) for k in TIERS}
    return m


def dashboard(weekly, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    blue, ink, muted, surface = "#2a78d6", "#0b0b0b", "#52514e", "#fcfcfb"
    labels = [w["week_start"][5:] for w in weekly]
    panels = [
        ("deploys_per_week", "Deployment Frequency (deploys/week)", 1, True),
        ("lead_time_hours", "Lead Time for Changes (median, hours)", 1, False),
        ("mttr_hours", "MTTR (mean, hours)", 1, False),
        ("change_failure_rate", "Change Failure Rate (%)", 100, False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), facecolor=surface)
    for ax, (key, title, scale, bar) in zip(axes.flat, panels):
        ys = [w[key] * scale if w[key] is not None else float("nan") for w in weekly]
        if bar:
            ax.bar(labels, ys, color=blue, width=0.6)
        else:
            ax.plot(labels, ys, color=blue, linewidth=2, marker="o", markersize=6)
        latest = weekly[-1]
        val = "N/A" if latest[key] is None else f"{latest[key] * scale:g}"
        ax.set_title(f"{title}\nthis week: {val}  ·  {latest['tiers'][key]}",
                     loc="left", fontsize=11, color=ink)
        ax.set_facecolor(surface)
        ax.grid(axis="y", color="#e5e4e0", linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(colors=muted, labelsize=8, length=0)
        ax.set_ylim(bottom=0)
    fig.suptitle(f"DORA Metrics — {REPO}  (last {WEEKS} weeks, generated {NOW:%Y-%m-%d})",
                 x=0.01, ha="left", fontsize=13, color=ink)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def report(m, weekly):
    fmt = lambda v, u="": "N/A" if v is None else f"{v:g}{u}"
    pct = lambda v: "N/A" if v is None else f"{v:.0%}"
    rows = "\n".join(
        f"| {w['week_start']} | {w['deployments']} | {fmt(w['lead_time_hours'], 'h')} "
        f"| {fmt(w['mttr_hours'], 'h')} | {pct(w['change_failure_rate'])} |"
        for w in reversed(weekly))
    return f"""# DORA 주간 보고서

> 자동 생성: {NOW:%Y-%m-%d %H:%M} UTC · `.github/workflows/dora.yml` · 원본 데이터 [`metrics.json`](metrics.json)

## 이번 주 ({m['window']})

| 지표 | 값 | 등급 |
|---|---|---|
| Deployment Frequency | {m['deployments']}회 ({m['deploys_per_week']:g}/주) | {m['tiers']['deploys_per_week']} |
| Lead Time for Changes (중앙값) | {fmt(m['lead_time_hours'], '시간')} | {m['tiers']['lead_time_hours']} |
| MTTR (평균) | {fmt(m['mttr_hours'], '시간')} | {m['tiers']['mttr_hours']} |
| Change Failure Rate | {pct(m['change_failure_rate'])} ({m['incidents']}건 / {m['deployments']}배포) | {m['tiers']['change_failure_rate']} |

![DORA dashboard](dashboard.png)

## 최근 {WEEKS}주 추이

| 주 시작일 | 배포 | Lead Time | MTTR | CFR |
|---|---|---|---|---|
{rows}

## 측정 정의
- **배포**: `main` 브랜치 push 1회 (trunk-based). 워크플로우 실행 이력에서 수집.
- **Lead Time**: 배포에 포함된 커밋의 작성 시각 → push 시각.
- **장애**: `incident` 라벨이 붙은 이슈. CFR = 장애 수 / 배포 수, MTTR = 이슈 open → close.
- 등급 기준: DORA State of DevOps 2023 (Elite / High / Medium / Low).
"""


def main():
    deploys, incidents = collect()
    week_start = (NOW - timedelta(days=NOW.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    weekly = []
    for k in range(WEEKS - 1, -1, -1):
        s = week_start - timedelta(weeks=k)
        weekly.append({"week_start": f"{s:%Y-%m-%d}", **summarize(deploys, incidents, s, s + timedelta(weeks=1))})
    current = summarize(deploys, incidents, NOW - timedelta(days=7), NOW + timedelta(seconds=1))
    current["window"] = f"{NOW - timedelta(days=7):%Y-%m-%d} ~ {NOW:%Y-%m-%d}"
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/metrics.json", "w") as f:
        json.dump({"repo": REPO, "generated_at": NOW.isoformat(), "last_7_days": current,
                   "weekly": weekly, "deployments": deploys, "incidents": incidents},
                  f, ensure_ascii=False, indent=2)
    with open(f"{OUT}/REPORT.md", "w") as f:
        f.write(report(current, weekly))
    dashboard(weekly, f"{OUT}/dashboard.png")
    print(json.dumps(current, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        assert tier("deploys_per_week", 10) == "Elite" and tier("deploys_per_week", 0) == "Low"
        assert tier("lead_time_hours", 2) == "Elite" and tier("lead_time_hours", 48) == "High"
        assert tier("change_failure_rate", 0.12) == "Medium" and tier("mttr_hours", None) == "N/A"
        print("ok")
    else:
        main()
