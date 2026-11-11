# Getting Started

처음 합류한 사람이 30분 안에 저장소를 받아 스크립트를 돌려 보는 것이 목표.

## 준비물
- Git, SSH 키(GitHub 등록)
- Python 3.11
- [GitHub CLI](https://cli.github.com) (`gh auth login` 완료)

## 설치
```bash
git clone git@github.com:sungjunpk/oss_practice_repository.git
cd oss_practice_repository
python3.11 -m venv .venv && source .venv/bin/activate
pip install matplotlib        # 현재 scripts/ 가 쓰는 유일한 외부 패키지
```

## 첫 실행: DORA 지표 수집
```bash
export GITHUB_TOKEN=$(gh auth token)
python scripts/dora.py        # dora/metrics.json, dora/dashboard.png 갱신
```

## 다음 단계
- 작업 규칙은 [[Development Guide]] 를 읽는다.
- 막히면 [[Troubleshooting]] 을 먼저 본다.
- 질문·제안은 Discussions, 버그는 Issue 로 올린다.

[[Home]]
