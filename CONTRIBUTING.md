# 기여 가이드

DeepTrader 에 관심 가져 주셔서 감사합니다. 버그 신고, 문서 개선, 코드 기여 모두 환영합니다.
참여하는 모두는 [행동 강령](CODE_OF_CONDUCT.md)을 따릅니다.

## 시작하기
설치·첫 실행: [Wiki › Getting Started](https://github.com/sungjunpk/oss_practice_repository/wiki/Getting-Started)

## 기여 방법
| 하고 싶은 일 | 방법 |
|---|---|
| 질문·아이디어 | [Discussions](https://github.com/sungjunpk/oss_practice_repository/discussions) |
| 버그 신고 / 기능 제안 | [Issue](https://github.com/sungjunpk/oss_practice_repository/issues/new/choose) (Bug / Feature 템플릿) |
| 큰 설계 변경 | Discussions 의 RFC 로 의견 수렴 → 합의되면 [ADR](docs/adr/) 작성 |
| 코드·문서 수정 | 아래 PR 절차 |

처음이라면 [`good first issue`](https://github.com/sungjunpk/oss_practice_repository/labels/good%20first%20issue) 라벨부터 보세요.

## PR 절차
1. 저장소를 Fork 하고 브랜치를 만든다: `feat/<이슈번호>-<요약>`, `fix/…`, `docs/…`
2. 변경은 작게, 한 PR 에 한 가지 목적만 담는다.
3. 커밋 메시지는 한국어 한 줄 제목, "무엇 — 왜" 형태. 예: `RSI 피처 추가 — 모델 입력 다양화`
4. PR 본문에 `Closes #번호` 를 적는다.
5. 리뷰 1명 이상 승인 후 병합한다. 리뷰 요청 후 48시간 안에 1차 응답을 목표로 한다.

세부 규칙(라벨·자동화)은 [Wiki › Development Guide](https://github.com/sungjunpk/oss_practice_repository/wiki/Development-Guide).

## 주의
- **실계좌 키·토큰을 절대 커밋하지 않는다.** 이 프로젝트는 모의투자 전용이다.
- 투자 권유가 아닌 학습·연구 목적 프로젝트다.

## 라이선스
기여하신 내용은 이 저장소와 같은 [MIT 라이선스](LICENSE)로 배포되는 것에 동의한 것으로 봅니다.
