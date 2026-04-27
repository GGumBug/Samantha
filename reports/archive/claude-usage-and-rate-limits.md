# Claude Code: 사용량, 속도 제한 & 추가 사용량

Claude Code에서 사용량 제한이 작동하는 방식과 제한에 도달했을 때 계속 작업하는 방법.

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## 개요

구독 플랜(Pro, Max 5x, Max 20x)의 Claude Code는 롤링 창에서 리셋되는 사용량 제한이 있습니다. 세 가지 내장 슬래시 명령어가 사용량을 모니터링하고 관리하는 데 도움을 줍니다:

| 명령어 | 설명 | 사용 가능 대상 |
|--------|------|-------------|
| `/usage` | 플랜 제한 및 속도 제한 상태 확인 | Pro, Max 5x, Max 20x |
| `/extra-usage` | 제한 도달 시 종량제 초과 설정 | Pro, Max 5x, Max 20x |
| `/cost` | 현재 세션의 토큰 사용량 및 지출 표시 | API 키 사용자 |

---

## `/usage` — 제한 확인

현재 플랜의 사용량 제한 및 속도 제한 상태를 표시합니다. 제한에 도달하기 전에 얼마나 많은 용량이 남았는지 확인하는 데 유용합니다.

---

## `/extra-usage` — 제한 이후에도 계속 작업

`/extra-usage` 명령어는 플랜의 속도 제한에 도달했을 때 차단되는 대신 Claude Code가 원활하게 계속 작동하도록 **종량제 초과 청구**를 설정합니다.

### 작동 방식

1. 플랜의 속도 제한에 도달합니다 (제한은 5시간마다 리셋)
2. 추가 사용량이 활성화되어 있고 사용 가능한 자금이 있다면 Claude Code는 중단 없이 계속됩니다
3. 초과 토큰은 구독료와 별도로 **표준 API 요금**으로 청구됩니다

### 설정 방법

CLI의 `/extra-usage` 명령어가 설정을 안내합니다. claude.ai의 **설정 > 사용량**에서 웹으로도 설정할 수 있습니다:

1. 추가 사용량 활성화
2. 결제 수단 추가
3. **월별 지출 한도** 설정 (또는 무제한 선택)
4. 선택적으로 잔액이 임계값 아래로 떨어지면 자동 재충전되는 **선불 자금** 추가

### 주요 세부사항

| 세부사항 | 값 |
|---------|-----|
| 일일 상환 한도 | $2,000/일 |
| 청구 | 구독과 별도, 표준 API 요금 |
| 제한 리셋 창 | 5시간마다 |

### 알려진 문제

2026년 2월 기준으로 `/extra-usage` CLI 명령어는 [미문서화](https://github.com/anthropics/claude-code/issues/12396)이며 명확한 설정 옵션 없이 로그인 창이 열릴 수 있습니다. 지금은 **claude.ai 웹 인터페이스**를 통한 설정이 더 신뢰할 수 있는 방법입니다.

---

## `/cost` — 세션 지출 (API 사용자)

API 키로 인증하는 사용자(구독 플랜 아님)의 경우 `/cost`는 다음을 표시합니다:

- 현재 세션의 총 비용
- API 지속 시간 및 실제 소요 시간
- 토큰 사용량 분류
- 변경된 코드

이 명령어는 Pro/Max 구독 사용자에게는 해당되지 않습니다.

---

## 빠른 모드와 추가 사용량

빠른 모드(`/fast`)는 더 빠른 출력으로 Claude Opus 4.6을 사용합니다. 추가 사용량과 특별한 청구 관계가 있습니다:

- 빠른 모드 사용은 **첫 번째 토큰부터 항상 추가 사용량에 청구됩니다**
- 구독 플랜에 남은 사용량이 있더라도 적용됩니다
- 빠른 모드는 플랜의 포함된 속도 제한을 소모하지 않습니다

즉, `/fast`를 사용하려면 추가 사용량이 활성화되고 자금이 있어야 합니다.

---

## CLI 시작 플래그

사용량 예산과 관련된 두 가지 시작 플래그 (API 키 사용자 전용, 프린트 모드):

| 플래그 | 설명 |
|-------|------|
| `--max-budget-usd <AMOUNT>` | 중지하기 전 API 호출의 최대 달러 금액 |
| `--max-turns <NUMBER>` | 에이전트 턴 수 제한 |

전체 목록은 [CLI 시작 플래그 참조](claude-cli-startup-flags.md)를 참고하세요.

---

## 출처

- [유료 Claude 플랜을 위한 추가 사용량 — Claude 도움말 센터](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans)
- [Pro 또는 Max 플랜으로 Claude Code 사용 — Claude 도움말 센터](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [/extra-usage 슬래시 명령어 미문서화 — GitHub 이슈 #12396](https://github.com/anthropics/claude-code/issues/12396)
- [Claude Code CLI 참조](https://code.claude.com/docs/en/cli-reference)
