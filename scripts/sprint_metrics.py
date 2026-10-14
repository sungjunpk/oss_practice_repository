"""스프린트 지표 — Cycle Time, Velocity, Burndown.

데이터: 마일스톤 = 스프린트(설명의 "시작: YYYY-MM-DD" ~ due), Project 의 Estimate = 스토리 포인트.
  - Cycle Time : 보드에서 처음 In Progress 로 옮긴 시각 → 이슈 close 시각
                 (In Progress 를 거치지 않은 이슈는 이슈 생성 시각을 시작으로 본다)
  - Velocity   : 스프린트 마감 전에 close 된 이슈의 SP 합
  - Burndown   : 스프린트 기간 일자별 남은 SP (현재 마일스톤 소속 이슈 기준)

출력: sprint/REPORT.md, sprint/burndown.png, sprint/velocity.png
사용: gh auth login -s project 후  python scripts/sprint_metrics.py
"""
import json, os, statistics, subprocess
from datetime import date, datetime, timedelta, timezone

OWNER, NAME = "sungjunpk", "oss_practice_repository"
OUT = "sprint"
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).date()

QUERY = """query($owner:String!,$name:String!,$cursor:String){repository(owner:$owner,name:$name){
  issues(first:100,after:$cursor){pageInfo{hasNextPage endCursor} nodes{
    number title createdAt closedAt
    milestone{title description dueOn}
    projectItems(first:5){nodes{estimate:fieldValueByName(name:"Estimate"){... on ProjectV2ItemFieldNumberValue{number}}}}
    timelineItems(first:50,itemTypes:[PROJECT_V2_ITEM_STATUS_CHANGED_EVENT]){nodes{
      ... on ProjectV2ItemStatusChangedEvent{createdAt status}}}}}}}"""


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def fetch():
    issues, cursor = [], ""
    while True:
        args = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"owner={OWNER}", "-f", f"name={NAME}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        page = json.loads(subprocess.run(args, check=True, capture_output=True, text=True).stdout)
        page = page["data"]["repository"]["issues"]
        issues += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return issues
        cursor = page["pageInfo"]["endCursor"]


def parse(raw):
    out = []
    for i in raw:
        est = next((n["estimate"]["number"] for n in i["projectItems"]["nodes"] if n["estimate"]), None)
        if est is None:
            continue  # 보드에 없거나 SP 미지정 — 지표 대상 아님
        started = [ts(e["createdAt"]) for e in i["timelineItems"]["nodes"] if e and e["status"] == "In Progress"]
        out.append({
            "number": i["number"], "title": i["title"], "sp": int(est),
            "created": ts(i["createdAt"]), "closed": ts(i["closedAt"]),
            "started": min(started) if started else ts(i["createdAt"]),
            "via_board": bool(started),
            "sprint": i["milestone"],
        })
    return out


def sprints(issues):
    found = {}
    for i in issues:
        m = i["sprint"]
        if m and m["title"] not in found and "시작:" in (m["description"] or ""):
            start = date.fromisoformat(m["description"].split("시작:")[1].split()[0])
            found[m["title"]] = (start, ts(m["dueOn"]).astimezone(KST).date())
    return dict(sorted(found.items(), key=lambda kv: kv[1][0]))


def burndown(items, start, end):
    days = [start + timedelta(d) for d in range((end - start).days + 1)]
    total = sum(i["sp"] for i in items)
    actual = [sum(i["sp"] for i in items if not (i["closed"] and i["closed"].astimezone(KST).date() <= d))
              for d in days if d <= TODAY]
    ideal = [total * (1 - k / (len(days) - 1)) for k in range(len(days))]
    return days, actual, ideal


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    issues = parse(fetch())
    sp = sprints(issues)
    os.makedirs(OUT, exist_ok=True)

    # Cycle time
    done = [i for i in issues if i["closed"]]
    hours = [(i["closed"] - i["started"]).total_seconds() / 3600 for i in done]

    # Velocity
    vel = {}
    for name, (start, end) in sp.items():
        vel[name] = sum(i["sp"] for i in issues if i["sprint"] and i["sprint"]["title"] == name
                        and i["closed"] and i["closed"].astimezone(KST).date() <= end)

    # Burndown 차트 (스프린트별 subplot)
    fig, axes = plt.subplots(1, max(len(sp), 1), figsize=(6 * max(len(sp), 1), 4), squeeze=False)
    bd_rows = []
    for ax, (name, (start, end)) in zip(axes[0], sp.items()):
        items = [i for i in issues if i["sprint"] and i["sprint"]["title"] == name]
        days, actual, ideal = burndown(items, start, end)
        ax.plot(days, ideal, "--", color="#9ca3af", label="Ideal")
        if actual:
            ax.plot(days[:len(actual)], actual, marker="o", color="#2563eb", label="Remaining SP")
        ax.set_title(name.split(" — ")[0], fontsize=10)  # 한글 폰트 없는 환경 대비
        ax.set_ylim(bottom=0)
        ax.tick_params(axis="x", labelrotation=45)
        ax.legend()
        bd_rows.append((name, start, end, sum(i["sp"] for i in items), actual[-1] if actual else None))
    fig.tight_layout()
    fig.savefig(f"{OUT}/burndown.png", dpi=120)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar([n.split(" — ")[0] for n in vel], list(vel.values()), color="#2563eb")
    ax.set_ylabel("Completed SP")
    ax.set_title("Velocity")
    fig.tight_layout()
    fig.savefig(f"{OUT}/velocity.png", dpi=120)

    fmt = lambda h: f"{h:.1f}h" if h < 48 else f"{h / 24:.1f}d"
    lines = [f"# 스프린트 지표 ({TODAY})", "",
             "`python scripts/sprint_metrics.py` 로 생성. 정의는 스크립트 상단 docstring 참고.", "",
             "## Velocity", "", "![velocity](velocity.png)", "",
             "| 스프린트 | 기간 | 계획 SP | 완료 SP |", "|---|---|---|---|"]
    for name, start, end, total, _ in bd_rows:
        lines.append(f"| {name} | {start} ~ {end} | {total} | {vel[name]} |")
    finished = [v for n, v in vel.items() if sp[n][1] < TODAY]
    lines += ["", f"평균 Velocity (종료된 스프린트): {statistics.mean(finished):.1f} SP" if finished
              else "종료된 스프린트 없음 — 평균 Velocity 는 Sprint 1 마감 후 산출.",
              "", "## Burndown", "", "![burndown](burndown.png)", "",
              "| 스프린트 | 오늘 남은 SP |", "|---|---|"]
    lines += [f"| {n} | {'-' if r is None else r} |" for n, _, _, _, r in bd_rows]
    lines += ["", "## Cycle Time", ""]
    if hours:
        lines += [f"- 완료 이슈 {len(done)}건, 중앙값 {fmt(statistics.median(hours))}, 평균 {fmt(statistics.mean(hours))}",
                  "", "| # | 이슈 | SP | 시작 | 완료 | Cycle Time |", "|---|---|---|---|---|---|"]
        for i, h in sorted(zip(done, hours), key=lambda x: x[0]["number"]):
            src = "In Progress" if i["via_board"] else "생성"
            lines.append(f"| #{i['number']} | {i['title']} | {i['sp']} | {i['started'].astimezone(KST):%m-%d %H:%M} ({src}) "
                         f"| {i['closed'].astimezone(KST):%m-%d %H:%M} | {fmt(h)} |")
    else:
        lines.append("완료된 이슈 없음.")
    open(f"{OUT}/REPORT.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
