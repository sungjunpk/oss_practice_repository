# 기여 가이드

## 1. 작업 흐름 (Feature 브랜치 전략)

```
main ──●────────────●────────────●──   항상 배포 가능한 상태, 직접 push 금지
        \          /  \          /
         ●──●──●──●    ●──●──●──●      feat/7-daily-ohlcv, docs/... 등 작업 브랜치
```

1. 이슈를 먼저 만든다 (`.github/ISSUE_TEMPLATE/` 의 Bug / Feature).
2. 최신 `main` 에서 브랜치를 딴다.
   ```bash
   git switch main && git pull
   git switch -c feat/7-daily-ohlcv
   ```
3. 작은 단위로 커밋하고 push → PR 생성 (템플릿 자동 적용).
4. 리뷰 → `[MUST]` 반영 → **Squash merge** → 브랜치 삭제.

> 예외: DORA 워크플로우(`github-actions[bot]`)는 매주 `dora/` 보고서를 `main` 에 직접 커밋한다. 브랜치 보호 규칙에서 이 봇만 bypass 로 허용한다.

### 브랜치 이름

`<type>/<이슈번호>-<짧은-설명>` — 이슈가 없으면 번호 생략. `type` 은 아래 커밋 타입과 같다.

| 예시 | 용도 |
|---|---|
| `feat/7-daily-ohlcv` | 새 기능 |
| `fix/21-rsi-nan` | 버그 수정 |
| `docs/contributing-review-guide` | 문서 |
| `chore/pr-template-codeowners` | 설정·잡무 |

## 2. 커밋 메시지 (Conventional Commits)

```
<type>(<scope>): <무엇> — <왜>
```

- `type`: `feat` · `fix` · `docs` · `refactor` · `test` · `chore` · `ci` · `perf` · `revert` (GitHub Revert 버튼의 `Revert "..."` 제목도 허용)
- `scope`(선택): `data` · `model` · `backtest` · `infra` · `github` · `dora` · `sprint`
- 제목은 한국어 한 줄, 마침표 없음. 본문은 필요할 때만.
- 호환되지 않는 변경은 `feat(model)!: ...` 처럼 `!` 를 붙이고 본문에 `BREAKING CHANGE:` 를 적는다.

```
feat(data): 일봉 시세 수집 스크립트 추가 — 피처 생성의 입력 데이터 확보
fix(dora): 리드타임 음수 값 제외 — 리베이스된 커밋이 지표를 왜곡
docs: 기여 가이드 추가 — 브랜치·커밋 규칙 통일
```

Squash merge 시 **PR 제목이 `main` 의 커밋 메시지**가 되므로 PR 제목도 같은 형식을 따른다.

## 3. Pull Request

- 하나의 PR = 하나의 목적. 리뷰 가능한 크기(대략 변경 400줄 이하)로 나눈다.
- 본문에 `Closes #이슈번호` 를 적어 머지 시 이슈를 자동으로 닫는다.
- 리뷰 규칙은 [리뷰 가이드](docs/REVIEW_GUIDE.md) 참고.
