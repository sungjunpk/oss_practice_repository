# DORA 주간 보고서

> 자동 생성: 2026-10-14 06:17 UTC · `.github/workflows/dora.yml` · 원본 데이터 [`metrics.json`](metrics.json)

## 이번 주 (2026-10-07 ~ 2026-10-14)

| 지표 | 값 | 등급 |
|---|---|---|
| Deployment Frequency | 1회 (1/주) | High |
| Lead Time for Changes (중앙값) | 0시간 | Elite |
| MTTR (평균) | N/A | N/A |
| Change Failure Rate | 0% (0건 / 1배포) | Elite |

![DORA dashboard](dashboard.png)

## 최근 12주 추이

| 주 시작일 | 배포 | Lead Time | MTTR | CFR |
|---|---|---|---|---|
| 2026-10-12 | 1 | 0h | N/A | 0% |
| 2026-10-05 | 0 | N/A | N/A | N/A |
| 2026-09-28 | 0 | N/A | N/A | N/A |
| 2026-09-21 | 0 | N/A | N/A | N/A |
| 2026-09-14 | 0 | N/A | N/A | N/A |
| 2026-09-07 | 0 | N/A | N/A | N/A |
| 2026-08-31 | 0 | N/A | N/A | N/A |
| 2026-08-24 | 0 | N/A | N/A | N/A |
| 2026-08-17 | 0 | N/A | N/A | N/A |
| 2026-08-10 | 0 | N/A | N/A | N/A |
| 2026-08-03 | 0 | N/A | N/A | N/A |
| 2026-07-27 | 0 | N/A | N/A | N/A |

## 측정 정의
- **배포**: `main` 브랜치 push 1회 (trunk-based). 워크플로우 실행 이력에서 수집.
- **Lead Time**: 배포에 포함된 커밋의 작성 시각 → push 시각.
- **장애**: `incident` 라벨이 붙은 이슈. CFR = 장애 수 / 배포 수, MTTR = 이슈 open → close.
- 등급 기준: DORA State of DevOps 2023 (Elite / High / Medium / Low).
