---
name: unity-log-diagnostic
description: Codex의 픽스를 사용자 플레이 테스트로 자동 검증. Codex가 [Prefix][Layer] 형식의 진단 Debug.Log를 박은 후 사용자가 Unity Editor에서 시나리오를 재현하면, 본 스킬이 Editor.log를 읽어 픽스 성공/실패를 판정합니다 (예: /unity-log-diagnostic BattleRng).
argument-hint: <prefix>
allowed-tools: Bash, Read
---

# Unity Log Diagnostic 스킬

## 용도

**Codex 픽스 ↔ 사용자 플레이 검증 루프**의 자동 검증 단계. 사용자의 복붙 노동을 0으로 압축하고 픽스 검증 사이클을 분 단위 → 초 단위로 단축한다.

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Codex  → 코드 픽스 + 진단 Debug.Log 삽입                 │
│             ([Prefix][Layer] 컨벤션 준수)                    │
│                                                             │
│ 2. 사용자  → Unity Editor에서 시나리오 재현 (플레이 테스트)  │
│             "테스트 끝났어" 한 마디                          │
│                                                             │
│ 3. 본 스킬 → Editor.log 자동 추출/분석 → 검증 판정          │  ← 본 스킬
│                                                             │
│ 4. Codex  → ✅/❌/⚠️/🔍 판정 보고 + 다음 액션 제안          │
└─────────────────────────────────────────────────────────────┘
```

## 사전 조건 (Codex가 픽스 단계에서 충족시켜야 함)

본 스킬이 작동하려면 픽스 단계에서 다음을 박아야 한다 — 본 스킬은 이 컨벤션을 신뢰하고 동작:

- **Prefix 컨벤션**: `Debug.Log("[<도메인>][<Layer>] <상태>")` — 도메인은 픽스 범위 식별자 (예: `BattleRng`, `Save`, `NodeEntry`, `L10n`)
- **Layer 태깅**: 분기 진단을 위해 `[L1]/[L2]/[L3]` 같이 의심 가설 layer 별 분류. Layer 없으면 어느 단계가 깨졌는지 판정 불가.
- **Before/After 비교 가능**: 같은 prefix 가 픽스 전/후 동일 위치에서 찍혀야 차이가 noticeable.
- **핵심 분기마다 로그**: ENTER / EARLY-RETURN / 핵심 결정 분기 / 결과값 — 통과 경로 추적 가능해야 함.

이 컨벤션을 충족하는 진단 로그 작성은 본 스킬의 책임 밖. Codex의 픽스 단계에서 보장해야 한다.

**다중 가설 동시 진단**: 한 진단 로그 셋에 N 가설을 동시 배치하면 1회 재현으로 root cause 확정 + 나머지 배제 가능 (ROI ~80% 단축). 패턴 상세: [best-practice/multi-hypothesis-diagnostic.md](../../../best-practice/multi-hypothesis-diagnostic.md).

## 작업

`<prefix>` 인자로 받은 도메인을 기준으로 `~/Library/Logs/Unity/Editor.log` 에서 매칭 로그를 추출하고, Run 별 분리 → Layer 그룹화 → 검증 판정 표 출력.

## 지침

### 1. 입력 검증

- `<prefix>` 가 비어있으면 사용자에게 prefix 묻기 — Codex가 본 픽스에서 사용한 도메인 이름.
- prefix 는 대괄호 없이 받음 — 내부에서 `[<prefix>]` 로 grep.

### 2. 로그 추출

```bash
LOG_PATH="$HOME/Library/Logs/Unity/Editor.log"
PREFIX="<사용자 prefix>"

if [ ! -f "$LOG_PATH" ]; then
  echo "Editor.log 없음 — 경로: $LOG_PATH"
  exit 1
fi

grep -n "\[$PREFIX\]" "$LOG_PATH"
```

추출 결과 0줄이면 가능 원인 제시:
- ① prefix 오타 — Codex가 픽스에서 사용한 정확한 prefix 확인
- ② 진단 로그 코드가 아직 컴파일/실행 안 됨 — Unity Editor 컴파일 확인
- ③ Editor 재생 안 함 / 코드 경로 안 탐 — 시나리오 재현 확인
- ④ 픽스 단계에서 Prefix 누락 — Codex가 진단 로그를 안 박음

### 3. 사이클 분리 (Run-by-Run)

같은 prefix 로 여러 Play 세션이 누적된 경우 자동 분리. **Before(픽스 전 베이스라인)/After(픽스 후) 비교** 가 검증 본질.

**자동 마커 우선순위**:
1. `[<Prefix>][CYCLE]` 명시 마커 — 가장 신뢰도 높음
2. **라이프사이클 진입 로그**: `Initialize ENTER`, `Awake ENTER`, `Start ENTER`, `Bootstrap ENTER` — 새 Play 세션의 자연 경계
3. **fallback**: 라인 번호 gap 이 100 이상 벌어지면 사이클 경계로 추정

각 사이클을 `Run 1`, `Run 2`, ... 라벨링.

### 4. Layer 그룹화

각 Run 내부에서 `[L1]/[L2]/[L3]/[L4]` Layer 태그 있으면 layer 별 정렬. 동일 Layer 의 같은 메서드 호출이 여러 번이면 시간순 모두 보존.

Layer 태그 없으면 시간순 단순 출력 + 사용자에게 "다음 픽스부터 Layer 태깅 권장" 안내.

### 5. 검증 판정 + 보고

다음 형식으로 보고. **판정 한 가지로 명확히 단정** (애매 회피):

```
## <Prefix> 검증 결과

추출: <총 라인 수>줄 / Run <N>개 / 의도된 픽스: <Codex가 보고한 의도 한 줄>

### 검증 판정
✅ 픽스 성공 / ❌ 픽스 실패 / ⚠️ 부분 성공 / 🔍 판정 불가

근거: <어느 시그널이 의도대로 변경/유지됐는가>

### Run 별 핵심 시그널
| Run | Layer | 핵심 값 |
|-----|-------|---------|
| Run 1 (Before) | L2 | <값> |
| Run 2 (After)  | L2 | <값> |

### Layer-by-Layer Diff
| Layer | 의도 | Before | After | 결과 |
|-------|------|--------|-------|------|
| L1.<key> | <기대 변화> | <v1> | <v2> | ✅/❌ |

### 실패/부분/불가 시 추가 시그널
- <어느 Layer 가 여전히 깨진 패턴 — 추가 픽스 후보>
- <누락된 로그 — 코드 경로 안 탐, 재현 부족 가능>
```

판정 우선순위: ✅ > ❌ > ⚠️ > 🔍. 자기 평가 회피 — 로그 데이터로 직접 증명 가능한 것만 ✅.

### 6. 후속 액션 제안

판정에 따라 1~2개 옵션:
- **✅ 성공**: "픽스 검증 완료. 진단 로그 제거 + 커밋 진행할까요?"
- **❌ 실패**: "픽스 미해결. <대안 가설 — 본 스킬이 발견한 새 의심 layer> 으로 재시도할까요?"
- **⚠️ 부분**: "<해결된 부분> 은 OK, <남은 부분> 만 추가 픽스 필요. 어느 layer 부터?"
- **🔍 불가**: "<누락된 로그 / 다른 시나리오 재현 / Layer 추가 삽입> 중 어느 방향?"

## 사용 예시 (도메인 무관)

```
[1. Codex 픽스]
- <도메인> 의 <의심 함수> 에 [<Prefix>][L1]/[L2]/[L3] 진단 로그 삽입
- <픽스 의도> 적용

[2. 사용자]
Unity Editor 재생 → 시나리오 재현 → 정지 → "테스트 끝"

[3. 본 스킬]
사용자: /unity-log-diagnostic <Prefix>
스킬:
1. Editor.log 에서 [<Prefix>] 추출
2. 라이프사이클 ENTER 마커로 Run 분리 (Before/After)
3. L1/L2/L3 비교 표
4. 판정: ✅ <근거> 또는 ❌ <남은 깨진 layer>

[4. Codex]
판정 보고 + 다음 액션 제안
```

## 참고사항

- **macOS 만 지원** (`~/Library/Logs/Unity/Editor.log`). Windows/Linux 는 경로 다름 — 추후 `$LOG_PATH` 인자화 필요.
- 추출 로그 1000줄 초과 시 Before/After 핵심 시그널 위주 요약. 전체 dump 는 명시 요청 시.
- `[Prefix][Layer]` 컨벤션 미준수 시 본 스킬 가치 발현 안 됨 — 픽스 단계에서 Layer 태깅 필수.
- **읽기 전용**: 코드/로그 파일 수정하지 않음. 픽스/제거는 Codex의 별도 위임.
- **검증 사이클의 일부**: 본 스킬 단독 호출 < Codex의 픽스 워크플로우 통합 사용 시 가치 최대.

## 본 스킬의 비-목적 (오용 회피)

- ❌ 픽스 자체 — 픽스는 Codex가 별도 위임으로 처리
- ❌ 진단 로그 삽입 — 픽스 단계의 책임
- ❌ 일반 Unity 콘솔 에러 추적 (예: NullReferenceException 추적) — 그건 raw Editor.log 직접 읽기로 충분, prefix 컨벤션 불필요
- ✅ **닫힌 검증 루프의 3단계** — 픽스가 의도대로 작동했는지 로그로 자동 판정
