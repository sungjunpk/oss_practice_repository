# Troubleshooting

| 증상 | 원인 | 해결 |
|---|---|---|
| `git push` 가 `Permission denied (publickey)` | SSH 키 미등록 | `ssh -T git@github.com` 로 확인 → GitHub Settings › SSH keys 에 공개키 등록 |
| `scripts/dora.py` 가 401/403 | `GITHUB_TOKEN` 없음·권한 부족 | `export GITHUB_TOKEN=$(gh auth token)` |
| `ModuleNotFoundError: matplotlib` | venv 미활성화 | `source .venv/bin/activate && pip install matplotlib` |
| 대시보드 x축 라벨이 비어 있음 | 수집 데이터가 1건 이하 | 배포(main push)가 쌓인 뒤 다시 실행 |
| 주간 보고서 커밋이 `push rejected` | 동시에 다른 push 발생 | 워크플로우는 `git pull --rebase` 후 재시도하므로 Actions 재실행 |
| 워크플로우가 이슈에 댓글을 못 닮 | `issues: write` 권한 누락 | 워크플로우 `permissions` 확인 |
| 한국투자증권 모의투자 API 인증 실패 | 앱키·시크릿 오류, 토큰 만료 | 모의투자용 키인지 확인(실계좌 키 사용 금지), 토큰 재발급 |

해결되지 않으면 [Issue](https://github.com/sungjunpk/oss_practice_repository/issues/new/choose) 를 열고, 해결법을 이 표에 추가한다.

[[Home]] · [[Getting Started]] · [[Development Guide]]
