# CI 최적화 전후 비교 리포트

측정일 2026-11-11 · 러너 GitHub-hosted · 재현: `gh workflow run cache-benchmark.yml` → `python scripts/cache_report.py bench <run_id>`

## 1. 요약
| 항목 | 결과 |
|---|---|
| 중복 제거 | `setup-python` 단계가 4곳 → 2곳(Composite Action 1개 + deploy). lint·test·build·benchmark 가 `setup-env` 공유 |
| Matrix 확장 | 9조합 → 13조합 (Python 3.13 추가, `ubuntu-22.04`+3.10 include) |
| **캐싱 효과** | **측정 결과 개선 없음** — 시나리오 3종 모두 오차 범위(−3% ~ +17%) |
| 선택적 배포 | 변경 파일 감지로 문서·스크립트만 바뀐 커밋은 CI **7초**에 종료 (전체 실행 97~117초) |

## 2. 중복 제거 (Reusable Workflow · Composite Action)
| | 이전 (`e08a053`) | 이후 |
|---|---|---|
| 파일 | `ci.yml` 107줄 1개 | `ci.yml` 89 + `_test.yml` 29 + `_deploy.yml` 52 + `actions/setup-env` 40 = 210줄 |
| Python 설치+캐시+의존성 설치 | lint·test·build·deploy 4곳에 복붙 | `setup-env` 1곳 (lint·`_test`·build·벤치마크 3개 잡이 호출) |
| 테스트 정의 | `ci.yml` 안에 인라인 | `_test.yml` (OS·Python 을 입력으로 받는 단일 정의, matrix 가 호출) |
| 배포 정의 | `ci.yml` 안에 인라인 | `_deploy.yml` (환경 이름을 입력으로 받음, staging/production 공용) |

총 줄 수는 오히려 늘었다(210 vs 107). 줄어든 것은 **같은 로직이 복사된 횟수**이고, 늘어난 것은 입력·권한 선언 같은 재사용 인터페이스다.

## 3. 캐싱 전후 측정
**방법**: `cache-benchmark.yml` 이 같은 단계(`setup-env`: Python 설치 + `pip install -e ".[extras]"`)를
캐시 없음(cold) / 있음(warm, 사전에 캐시를 채운 뒤) 으로 시나리오당 3회씩 돌리고, 해당 단계의 소요 시간을 Actions API 의 단계 시작·종료 시각으로 집계한다.

| 시나리오 | 설치 대상 | 구분 | setup 단계 (초, 3회) | 중앙값 | 변화 |
|---|---|---|---|---|---|
| small | `.[dev]` (pytest, ruff) | cold | 6, 5, 6 | 6.0 | |
| | | warm | 5, 5, 6 | 5.0 | **+16.7%** (노이즈 수준) |
| large | `.[dev,ml]` (+numpy, pandas, scikit-learn) | cold | 20, 13, 20 | 20.0 | |
| | | warm | 20, 20, 21 | 20.0 | **0.0%** |
| torch | `.[dev,torch]` (+PyTorch) | cold | 63, 84, 79 | 79.0 | |
| | | warm | 93, 81, 76 | 81.0 | **−2.5%** |

기준 실행: [42969669490](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42969669490). 같은 설정으로 앞서 돌린 두 실행에서도 방향이 일정하지 않았다.

| 이전 실행 | small | large |
|---|---|---|
| [42969299845](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42969299845) | 6.0 → 7.0초 (−16.7%) | 16.0 → 21.0초 (−31.2%) |
| [42969474409](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42969474409) | 6.0 → 6.0초 (0%) | 19.0 → 21.0초 (−10.5%) |

**해석**
- 개선률을 한 숫자로 말할 수 없다. 반복 간 편차(예: torch cold 63~84초)가 평균 차이보다 크다.
- 가설(검증하지 않음): GitHub-hosted 러너에서 PyPI 휠 다운로드가 충분히 빨라, 캐시 복원(tar 해제) 비용이 절약분과 비슷하거나 더 크다. 캐시가 유리해지는 조건은 소스 빌드가 필요한 패키지, 느린 네트워크, 외부 장애 대비다.
- 이 프로젝트 현재 규모에서는 `setup-env` 의 `cache` 입력을 `"false"` 로 두어도 손해가 없다. 기본값은 과제 요구에 맞춰 `"true"` 로 두었고, 의존성이 소스 빌드 위주로 바뀔 때 다시 측정한다.

## 4. 전체 파이프라인 실행 시간
| 실행 | 구성 | 잡 수 | wall-clock | 잡 시간 합 |
|---|---|---|---|---|
| [42967658738](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42967658738) 이전 | 9조합 | 12 | 102초 | 276초 |
| [42968779623](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42968779623) 이후 첫 실행 | 13조합 | 17 | 109초 | 399초 |
| [42969123353](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42969123353) 이후 | 13조합 | 17 | 97초 | 355초 |
| [42969473223](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42969473223) 이후 | 13조합 | 17 | 117초 | 383초 |

조합이 44% 늘었지만 wall-clock 은 병렬 실행 덕에 같은 범위(97~117초)다. 잡 시간 합(과금 기준)은 조합 수에 비례해 늘었다.

## 5. 선택적 배포
| 조건 | 동작 | 검증 |
|---|---|---|
| 코드·테스트·`pyproject.toml`·CI 설정 변경 | lint → test → build → deploy | ✅ [42969473223](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42969473223) (main → staging) |
| 문서·스크립트·벤치마크 워크플로우만 변경 | `changes` 만 실행, 나머지 건너뜀 | ✅ [42969298464](https://github.com/sungjunpk/oss_practice_repository/actions/runs/42969298464) — 7초, 잡 시간 합 4초 |
| Pull Request | lint·test·build, **deploy 안 함** (Secrets 보호) | ⚠️ 조건식만 작성, PR 로 실행해 보지 않음 |
| `main` push | deploy → `staging` 환경 | ✅ 위 실행 |
| `v*` 태그 | deploy → `production` + GitHub Release | ⚠️ 조건식만 작성, 태그를 만들지 않아 미실행 |
| 수동 실행 | 전체 실행, `main` 에서만 deploy | — |

변경 파일 감지는 [`dorny/paths-filter@v3`](https://github.com/dorny/paths-filter) 를 쓴다. 감지 대상 경로는 `ci.yml` 의 `changes` 잡에 있다.

## 6. 한계
- 시나리오당 표본이 3개라 통계적 결론은 못 낸다.
- 러너 성능·PyPI 상태는 시점마다 다르다. 다른 시간대에 다시 측정하면 값이 바뀔 수 있다.
- `scripts/` 는 린트 대상이 아니다(기존 스타일 위반 다수).
