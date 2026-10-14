"""칸반 보드 일괄 구성 — 라벨, 마일스톤 2개, 이슈, GitHub Project(Status 5단계 + Estimate).

사용: gh auth login -s project 후  python scripts/setup_board.py
재실행 안전: 라벨은 덮어쓰고, 같은 제목의 마일스톤·이슈·프로젝트는 건너뛴다.
"""
import json, subprocess

OWNER = "sungjunpk"
REPO = f"{OWNER}/oss_practice_repository"
PROJECT = "DeepTrader Kanban"

LABELS = {
    "type:bug": ("d73a4a", "기대와 다르게 동작"),
    "type:feature": ("a2eeef", "새 기능"),
    "type:docs": ("0075ca", "문서·조사·보고서"),
    "type:chore": ("cfd3d7", "환경·설정·CI"),
    "area:data": ("fbca04", "수집·전처리·피처"),
    "area:model": ("5319e7", "예측 모델·평가"),
    "area:backtest": ("1d76db", "백테스트·매매 엔진"),
    "area:infra": ("bfdadc", "저장소·CI·지표"),
    "priority:high": ("b60205", "이번 스프린트 필수"),
    "priority:medium": ("e99695", "가능하면 이번 스프린트"),
    "priority:low": ("f9d0c4", "여유 있을 때"),
    "incident": ("000000", "장애 — DORA MTTR·CFR 집계 대상"),
}
# 기본 라벨 중 type:* 와 겹치는 것 — 쓰는 이슈가 없을 때만 삭제
DEFAULT_DUPES = ["bug", "documentation", "enhancement"]

# 제목, 설명, 시작일, 마감일 (시작일은 burndown 계산용으로 설명에 기록)
MILESTONES = [
    ("Sprint 1 — 기획·환경·데이터 수집", "2026-10-14", "2026-10-27"),
    ("Sprint 2 — 전처리·베이스라인", "2026-10-28", "2026-11-10"),
]
S1, S2 = (m[0] for m in MILESTONES)

STATUSES = [("Backlog", "GRAY"), ("To Do", "BLUE"), ("In Progress", "YELLOW"), ("Review", "PURPLE"), ("Done", "GREEN")]

# 제목, 라벨, 마일스톤, Estimate(SP), Status, 본문
ISSUES = [
    ("[Chore] Git/GitHub 환경 구축 및 저장소 생성", "type:chore,area:infra,priority:high", S1, 1, "Done",
     "SSH 설정, 저장소 생성, 첫 커밋 (1주차)."),
    ("[Docs] 학기 프로젝트 제안서 작성", "type:docs,priority:high", S1, 2, "Done",
     "README.md 제안서 — 문제 정의, 핵심 기능, 기술 스택, 16주 마일스톤 (2주차)."),
    ("[Feature] DORA 4대 지표 수집 워크플로우", "type:feature,area:infra,priority:medium", S1, 3, "Done",
     "`.github/workflows/dora.yml` + `scripts/dora.py` — 배포 빈도·리드타임·MTTR·CFR 자동 측정."),
    ("[Bug] DORA 대시보드 라인 차트 x축 누락", "type:bug,area:infra,priority:medium", S1, 1, "Done",
     "`dora/dashboard.png` 라인 차트에 x축 라벨이 표시되지 않음. da17cd4 에서 수정."),
    ("[Chore] 칸반 보드·이슈 템플릿·라벨 체계 구성", "type:chore,area:infra,priority:high", S1, 2, "Review",
     "GitHub Project(Backlog/To Do/In Progress/Review/Done), Bug/Feature 템플릿, 라벨, 마일스톤 2개."),
    ("[Docs] 시계열 예측·퀀트 논문 및 증권 API 조사", "type:docs,area:model,priority:medium", S1, 3, "To Do",
     "LSTM/Transformer 시계열 예측 사례, 한국투자증권 모의투자 API 호출 제한·인증 방식 정리 (3주차)."),
    ("[Feature] 일봉 시세 수집 스크립트", "type:feature,area:data,priority:high", S1, 3, "To Do",
     "FinanceDataReader 로 대상 종목 일봉 OHLCV 수집 (4주차)."),
    ("[Feature] 시세 SQLite 저장 스키마", "type:feature,area:data,priority:high", S1, 2, "To Do",
     "수집한 시세를 SQLite 에 저장, 중복 날짜는 upsert."),
    ("[Feature] 결측치 처리·정규화 전처리", "type:feature,area:data,priority:high", S2, 3, "Backlog",
     "휴장일·결측 처리, 학습 구간 기준 정규화 (미래 데이터 누수 방지)."),
    ("[Feature] 기술적 지표 피처 생성 (RSI·MACD·볼린저밴드)", "type:feature,area:data,priority:high", S2, 5, "Backlog",
     "pandas 로 기술적 지표 컬럼 생성 (5주차)."),
    ("[Docs] 피처 데이터셋 EDA", "type:docs,area:data,priority:medium", S2, 2, "Backlog",
     "분포·상관관계·라벨 불균형 확인."),
    ("[Feature] 시간순 train/val/test 분할 + walk-forward", "type:feature,area:model,priority:high", S2, 3, "Backlog",
     "과적합·누수 방지용 시간순 분할."),
    ("[Feature] 규칙 기반 베이스라인 (이동평균 교차)", "type:feature,area:model,priority:medium", S2, 2, "Backlog",
     "골든/데드 크로스 신호 (6주차)."),
    ("[Feature] 로지스틱 회귀 베이스라인", "type:feature,area:model,priority:medium", S2, 3, "Backlog",
     "scikit-learn 로지스틱 회귀로 N일 뒤 상승·하락 분류."),
    ("[Feature] 평가 지표 정의 (정확도·F1·수익률·MDD·샤프)", "type:feature,area:model,priority:high", S2, 3, "Backlog",
     "모델·전략 공통 평가 함수."),
    ("[Feature] LSTM 가격 방향 예측 모델 v1", "type:feature,area:model,priority:medium", None, 8, "Backlog",
     "PyTorch LSTM (7주차)."),
    ("[Feature] 백테스트 엔진 (수수료·슬리피지 반영)", "type:feature,area:backtest,priority:medium", None, 8, "Backlog",
     "10주차."),
    ("[Chore] GitHub Actions pytest CI", "type:chore,area:infra,priority:low", None, 2, "Backlog",
     "push/PR 마다 pytest 실행."),
    ("[Chore] 모의투자 API 연동 사전 테스트", "type:chore,area:backtest,priority:low", None, 3, "Backlog",
     "리스크 대응 — 인증·호출 제한을 초기에 확인."),
]


def gh(*args, parse=False):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out) if parse else out.strip()


def graphql(query, **vars):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in vars.items():
        args += ["-f", f"{k}={v}"]
    return gh(*args, parse=True)["data"]


def main():
    for name, (color, desc) in LABELS.items():
        gh("label", "create", name, "--repo", REPO, "--color", color, "--description", desc, "--force")
    for name in DEFAULT_DUPES:
        if not gh("issue", "list", "--repo", REPO, "--state", "all", "--label", name, "--json", "number", parse=True):
            subprocess.run(["gh", "label", "delete", name, "--repo", REPO, "--yes"], capture_output=True)

    have = {m["title"] for m in gh("api", f"repos/{REPO}/milestones?state=all", parse=True)}
    for title, start, due in MILESTONES:
        if title not in have:
            gh("api", f"repos/{REPO}/milestones", "-f", f"title={title}",
               "-f", f"description=시작: {start}", "-f", f"due_on={due}T23:59:59+09:00")

    projects = gh("project", "list", "--owner", OWNER, "--format", "json", parse=True)["projects"]
    proj = next((p for p in projects if p["title"] == PROJECT), None)
    if not proj:
        proj = gh("project", "create", "--owner", OWNER, "--title", PROJECT, "--format", "json", parse=True)
        gh("project", "link", str(proj["number"]), "--owner", OWNER, "--repo", REPO)
        gh("project", "field-create", str(proj["number"]), "--owner", OWNER,
           "--name", "Estimate", "--data-type", "NUMBER")
    num, pid = str(proj["number"]), proj["id"]

    fields = {f["name"]: f for f in gh("project", "field-list", num, "--owner", OWNER, "--format", "json", parse=True)["fields"]}
    status = fields["Status"]
    if [o["name"] for o in status["options"]] != [s for s, _ in STATUSES]:
        opts = ",".join(f'{{name:"{s}",color:{c},description:""}}' for s, c in STATUSES)
        res = graphql(f"""mutation($id:ID!){{updateProjectV2Field(input:{{fieldId:$id,singleSelectOptions:[{opts}]}})
            {{projectV2Field{{... on ProjectV2SingleSelectField{{options{{id name}}}}}}}}}}""", id=status["id"])
        status["options"] = res["updateProjectV2Field"]["projectV2Field"]["options"]
    opt = {o["name"]: o["id"] for o in status["options"]}

    existing = {i["title"]: i for i in gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "500",
                                          "--json", "title,url", parse=True)}
    for title, labels, ms, est, st, body in ISSUES:
        if title in existing:
            continue
        args = ["issue", "create", "--repo", REPO, "--title", title, "--body", body, "--label", labels]
        url = gh(*args, *(["--milestone", ms] if ms else []))
        item = gh("project", "item-add", num, "--owner", OWNER, "--url", url, "--format", "json", parse=True)["id"]
        gh("project", "item-edit", "--id", item, "--project-id", pid,
           "--field-id", status["id"], "--single-select-option-id", opt[st])
        gh("project", "item-edit", "--id", item, "--project-id", pid,
           "--field-id", fields["Estimate"]["id"], "--number", str(est))
        if st == "Done":
            gh("issue", "close", url, "--reason", "completed")
        print(f"{st:12} {est}SP  {url}")

    print(f"\nhttps://github.com/users/{OWNER}/projects/{num}")


if __name__ == "__main__":
    main()
