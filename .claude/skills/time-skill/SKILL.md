---
name: time-skill
description: 파키스탄 표준시(PKT, UTC+5)로 현재 시간을 표시합니다. 사용자가 현재 시간, 파키스탄 시간, 또는 PKT를 요청할 때 사용합니다.
user-invocable: true
---

# 시간 스킬

이 스킬은 파키스탄 표준시(PKT)의 현재 날짜와 시간을 표시합니다.

## 작업

파키스탄 표준시(UTC+5)의 현재 날짜와 시간을 표시합니다.

## 지침

1. **현재 시간 가져오기**: 다음 bash 명령어를 실행합니다:
   ```
   TZ='Asia/Karachi' date '+%Y-%m-%d %H:%M:%S %Z'
   ```

2. **결과 표시**: 다음 형식으로 시간을 표시합니다:
   ```
   Current Time in Pakistan (PKT): YYYY-MM-DD HH:MM:SS PKT
   ```

## 요구사항

- 항상 `Asia/Karachi` 타임존(UTC+5)을 사용합니다
- 24시간 형식을 사용합니다
- 시간과 함께 날짜를 포함합니다
- 출력을 간결하게 유지합니다 — 불필요한 설명은 생략합니다
