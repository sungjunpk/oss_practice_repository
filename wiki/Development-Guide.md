# Development Guide

## 작업 흐름
1. Issue 를 고르거나 만든다 (템플릿: Bug / Feature). 라벨은 `type:*`, `area:*`, `priority:*` 를 붙인다.
2. `main` 에서 브랜치를 딴다: `feat/<이슈번호>-<요약>`, `fix/…`, `docs/…`.
3. 작은 단위로 커밋하고 PR 을 연다. 본문에 `Closes #번호`.
4. 리뷰 1명 승인 후 `main` 에 병합 — **`main` push 1건 = 배포 1건** (DORA 집계 기준).

## 커밋 메시지
한국어 한 줄 제목, "무엇 — 왜" 형태. 본문은 필요할 때만.
```
피처 생성 모듈 추가 — RSI·MACD 를 모델 입력으로 쓰기 위해
```

## 라벨
| 접두 | 값 |
|---|---|
| `type:` | bug, feature, docs, chore |
| `area:` | data, model, backtest, infra |
| `priority:` | high, medium, low |
| `incident` | 장애 — DORA MTTR·CFR 집계 대상 |

## 의사결정 기록 (ADR)
되돌리기 어려운 기술 결정(모델 구조, 데이터 소스, 저장소 등)은 [`docs/adr/`](https://github.com/sungjunpk/oss_practice_repository/tree/main/docs/adr) 에
`0000-template.md` 를 복사해 남긴다. 논의가 필요하면 Discussions 의 **RFC** 카테고리에서 먼저 의견을 받는다.

## 자동화
| 워크플로우 | 역할 |
|---|---|
| `dora.yml` | DORA 4대 지표 수집·주간 보고서 |
| `issue-autoreply.yml` | 새 이슈에 접수 안내 댓글 |
| `sla.yml` | 48시간 무응답 이슈에 `sla:breach` 표시 |
| `weekly-summary.yml` | 매주 월요일 활동 요약 이슈 생성 |

[[Home]] · [[Getting Started]] · [[Troubleshooting]]
