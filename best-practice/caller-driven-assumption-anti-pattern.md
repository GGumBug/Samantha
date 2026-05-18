[← README로 돌아가기](../README.md)

# Caller-Driven Assumption 안티패턴 (enum/시그니처/시트 컬럼 추측 금지)

코드 작성/위임 시 **enum 멤버 / 메서드 시그니처 / 시트 컬럼 키 / Manager 프로퍼티 이름** 을 grep 없이 "보통 이렇게 쓰겠지" 추측하는 패턴은 100% 컴파일 에러 또는 silent 잘못 동작으로 이어진다. 헌법 §0-1 Step 1 "변경 전 영향 분석" 의 직접 위반.

## 핵심 룰

**정확한 enum/시그니처/시트 구조는 grep 결과 인용 의무**. "보통 이렇게 쓰겠지" 추측 금지. 위임 프롬프트에도 "사용 enum 정의 파일 read + 결과 인용 후 코드 작성" 명시.

## 본 세션 사례 2건 (2026-05-11)

### 사례 A — Sonny B2 LocationType.Battle 추측 (CS0117)

**위치**: `BattleManager.cs:862` 신규 분기 작성 시 Sonny B2 가 `LocationType.Battle` 사용.

**실제**: `LocationType` enum 정의 파일 grep 시 `Battle` 멤버 없음. 정확한 멤버는 `LocationType.Monster`.

**증상**: Unity 컴파일 시 CS0117 (`'LocationType' does not contain a definition for 'Battle'`) → 사용자 컴파일 실패 알림 → Sonny 픽스 (`LocationType.Monster` + `PlayerData → CurrentData` 보정) → 컴파일 PASS.

**예방**:
```bash
# enum 사용 전 sweep
grep -nE "enum LocationType" Assets/Scripts/
# 결과 파일 read + 멤버 인용 후 코드 작성
```

### 사례 B — 메인 세션이 시트 컨벤션 추측

**위치**: `BattleKeys.cs` const 값 작성 — 메인 세션이 `battle.reward_potion.name` 을 lookup 키로 가정.

**실제**: 사용자 시트 컨벤션은 `battle.0102` 가 lookup 키 + `battle.reward_potion.name` 은 alias 컬럼 (의미 주석용).

**증상**: const 변경 (`battle.0102` → `battle.reward_potion.name`) → 사용자 정정 ("그건 alias 야") → 다시 `battle.0102` 원복.

**예방**:
- 시트 컬럼 / 키 추측 전 시트 export TSV grep 또는 사용자 1 질문 ("lookup 키와 alias 컬럼 구분 법?")
- "보통 의미 있는 이름이 키" 라는 컨벤션 추측 금지 — 프로젝트마다 다름

## 검증 grep 패턴

위임 시작 전 의무:

```bash
# 1. enum 멤버 정확성
grep -nE "enum {대상Enum}" Assets/Scripts/  # 정의 파일 식별
# 식별 파일 read + 멤버 목록 인용 후 코드 작성

# 2. 메서드 시그니처 정확성
grep -nE "public .* {대상메서드}\(" Assets/Scripts/  # 시그니처 식별
# 정확한 파라미터 타입/순서 인용 후 호출 코드 작성

# 3. 시트 컬럼 / 키 컨벤션
grep -nE "{lookup 키 후보}" Assets/Resources/  # TSV 또는 시트 export 파일
# lookup 키 vs alias 컬럼 구분 사용자 1 질문
```

## 헌법 §0-1 Step 1 cross-link

본 안티패턴은 헌법 [engineering-constitution.md §0-1 Step 1](../.claude/rules/engineering-constitution.md) "변경 전 영향 분석" 의 "코드 형태 grep + 결과 표 작성 의무" 직접 위반. 추가로 §0 메타 원칙 ("패턴 미러링 보고 시 코드 형태 grep 비교 + 인용 의무") 도 위반.

## 위임 프롬프트 박제 문구

리팩토링/신규 분기 작성 위임 시 프롬프트에 다음 1줄 의무:

> "사용 enum / 메서드 시그니처 / 시트 컬럼 키는 grep 결과 인용 후 코드 작성. '보통 이렇게 쓰겠지' 추측 시 100% 컴파일 에러 또는 silent 잘못 동작 — 사례 2건 ([caller-driven-assumption-anti-pattern.md](../../best-practice/caller-driven-assumption-anti-pattern.md))"

## 시니어 회고

- 추측 비용 0 직관은 함정 — 컴파일 에러는 사용자 통보 + 재위임 cycle 발생, silent 잘못 동작은 진단 cost 폭증
- enum / 시그니처 / 시트 컬럼은 **15초 grep** 으로 확실 — "이 정도는 알겠지" 자기 정당화 회피
- 헌법 §0 메타 원칙: "패턴을 따랐다 / 보통 이렇다" 자체 정당화 금지 — grep 결과 인용 의무

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §0-1 Step 1 + §0 메타 원칙
- [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) — 리팩토링 위임 체크리스트
- [external-critique-simulation.md](external-critique-simulation.md) — 외부 비판자 6 질문 시뮬레이션
