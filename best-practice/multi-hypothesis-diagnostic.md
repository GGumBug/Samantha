[← README로 돌아가기](../README.md)

# 다중 가설 동시 진단 패턴 (N 가설 1 회 재현)

간헐 결정론 사고 / race / 환경 의존 버그 진단 시, **한 진단 로그 셋에 N 가설을 동시 검증** 하면 **한 회 재현으로 root cause 확정 + 나머지 배제**가 가능. 직렬 검증(가설별 1 사이클씩) 대비 ROI ~80% 단축.

## 핵심 원칙

```
[직렬 검증]                          [동시 검증]
가설 1 → 진단 → 재현 → 판정          가설 1-5 → 진단 셋 → 재현 1회 → 판정
가설 2 → 진단 → 재현 → 판정          (root cause 확정 + 나머지 배제)
가설 3 → 진단 → 재현 → 판정
가설 4 → 진단 → 재현 → 판정          시간 ROI: 5 사이클 → 1 사이클
가설 5 → 진단 → 재현 → 판정          (사용자 재현 노동 80% 압축)
```

## 적용 조건

- **사용자 재현 비용이 비대칭** — 사용자가 재현 1회 = 분 단위, Claude 진단 로그 추가 = 초 단위. 진단 로그를 **최대한 박고** 1회 재현으로 최대 정보 회수가 ROI 최적
- **가설 간 진단 위치 충돌 없음** — 같은 메서드 / 같은 layer 에 여러 가설 진단 로그 공존 가능
- **`[Prefix][Layer]` 컨벤션 준수** — `unity-log-diagnostic` 스킬이 layer 별 자동 grep / 분리 / 판정 가능 ([SKILL.md](../.claude/skills/unity-log-diagnostic/SKILL.md))

## 본 사이클 사례 (2026-05-08 BattleRng 결정론 인시던트)

**증상**: 동일 시드 5-10회 재현 시 1회 RNG 결정론 깨짐 — Run C → Run D 변환 시점 한정.

**5 가설 동시 진단**:

| Layer | 가설 | 진단 로그 위치 |
|-------|------|---------------|
| L1 | ID=0 sentinel 변환이 정상 자산을 미설정으로 오해석 | `MapDataMapper.RoundtripExisting()` ENTER + 변환 결과 |
| L2 | RunSeed round-trip 깨짐 (저장/복원 시 시드 변환) | `RunSeedManager.Save/Load` ENTER + 시드 값 |
| L3 | RNG 라벨 충돌 (다른 subsystem 이 같은 라벨 소비) | `RunRngService.ForSubsystem()` 라벨 + counter |
| L4 | Cooldown round-trip 깨짐 (저장/복원 시 cooldown 손실) | `CooldownManager.Save/Load` cooldown map |
| L5 | `_rules` 순서 불안정 (List ordering 비결정적) | `RuleEngine.Initialize()` `_rules` 순서 dump |

**한 회 재현 (시나리오 A 5-10회) → /unity-log-diagnostic BattleRng 분석**:
- Run C/D 사고 케이스 잡힘
- L1 진단 로그가 `existingId=0 → -1 변환` 시그널 노출 → **가설 1 확정**
- L2 시드 round-trip OK / L3 라벨 안정 / L4 cooldown 보존 / L5 `_rules` 순서 stable → **가설 2-5 배제**

**ROI**: 5 가설 직렬 검증 시 사용자 재현 5회 (각 시나리오 A 5-10회 plays) → **1회 재현 으로 압축**.

## 본 사이클 사례 (2026-05-11 PotionDropChance preserve block 누락)

**증상**: 보스층 클리어 후 다음 act 진입 시 포션 드롭 확률이 항상 default (40) 으로 silent 리셋. POCO clamp / Save / Load / Reset 모두 정상 → 가시 증상 1개 vs root cause 후보 5 layer.

**5 layer 동시 진단**:

| Layer | 가설 | 진단 로그 위치 |
|-------|------|---------------|
| L1 | Reset 호출이 보스층 클리어 시 실수로 트리거 | `PlayerData.ResetPotionDropChance()` ENTER + caller stack |
| L2a | SkipBoss 분기가 chance 를 직접 덮어씀 | `BattleManager.SkipBoss()` ENTER + chance 변경 |
| L2b | Roll 직후 chance 변경이 누락 | `PotionDropChanceCalculator.Roll()` prev / next |
| L3 | POCO clamp 가 max 초과 시 default 로 reset | `PlayerData.AddPotionDropChance()` prev / delta / next |
| L4 | Save / Load 직렬화 mismatch (ES3 mismatch) | `PlayerDataManager.Save/Load` saving / loaded chance |

**한 회 재현 (시나리오 보스층 클리어 1회) → /unity-log-diagnostic 분석**:

| Layer | 결과 | 판정 |
|-------|------|------|
| L1 [Reset] | 0건 → reset 호출 안 됨 | 가설 1 배제 (정상) |
| L2a [SkipBoss] | 분기 진입 안 됨 | 가설 2a 배제 |
| L2b [Roll] | prev=40 → next=±10 정상 | 가설 2b 배제 (Roll 정상 동작) |
| L3 [Update] | clamp 정상 (40 → 50 → 60 ...) | 가설 3 배제 |
| L4 [Save] | **saving chance=50 직후 saving chance=40 (덮어쓰기 패턴)** | **root cause 후보 확정** |
| L4 [Load] | disk-loaded chance=40 (덮어쓴 값 그대로) | ES3 직렬화 정상 — 덮어쓰기가 진짜 root |

**root cause 확정**: `RunLifecycleService.CaptureRunStateFromPlayerManagerInternal` 의 preserve block 에 `PotionDropChancePercent` 누락 → `new PlayerRunStateData()` 후 일부 필드만 복원 → 신규 필드는 default 로 휘발 → "Save 직후 Save (덮어쓰기)" 시그널로 노출.

**픽스**: preserve block 에 한 줄 추가 (Stage 4 commit `274a8976`). 상세 [runstate-preserve-block-grep.md](runstate-preserve-block-grep.md).

**ROI**: 5 가설 직렬 검증 시 사용자 재현 5회 → **1회 재현으로 압축**. L4 만 진단했으면 SSOT 단일 진입점이 어디서 덮어쓰는지 추가 cycle 필요 — L1-L4 동시 박제로 "모든 다른 layer 정상" 즉시 확정 → root cause 위치 좁힘.

## 진단 로그 컨벤션 (사전 조건)

`[Prefix][Layer]` 형식 의무 — `unity-log-diagnostic` 스킬이 자동 grep + run 분리 + layer-by-layer diff 판정 가능:

```csharp
// 핵심 분기마다 ENTER + 결과값
Debug.Log($"[BattleRng][L1] RoundtripExisting ENTER existingId={existingId}");
Debug.Log($"[BattleRng][L1] RoundtripExisting result={result}");
Debug.Log($"[BattleRng][L2] RunSeed Save seed={seed}");
Debug.Log($"[BattleRng][L3] ForSubsystem label={label} counter={counter}");
```

상세 컨벤션: [unity-log-diagnostic SKILL.md](../.claude/skills/unity-log-diagnostic/SKILL.md) §사전 조건.

## 가설 설계 체크리스트 (헌법 §0-1 Step 1 영향 분석 연계)

진단 로그 박기 전:
- [ ] 가설 셋이 **MECE** (Mutually Exclusive, Collectively Exhaustive) — 한 root cause 확정 시 나머지 자동 배제 가능?
- [ ] 각 가설이 **독립 layer** 에 매핑 (L1, L2, L3, ...) — 시그널 충돌 없음
- [ ] 진단 로그가 **재현 비용 안 늘림** — 같은 시나리오 1회 재현으로 모든 가설 시그널 회수 가능
- [ ] **layer-by-layer diff** 가 가설 판정에 충분 — Before/After 비교가 가설 확정/배제 가능
- [ ] `[Prefix]` 일관 (도메인별 단일 prefix) — 스킬 grep 단일 사이클로 추출

## 시니어 회고

- **사용자 재현 비용 비대칭** 인지 의무 — Claude 가 진단 로그 박는 비용 << 사용자가 재현 1회 비용. 직렬 검증은 사용자 노동 5배 낭비
- "가설 1만 확신" 시 함정: 사용자가 5-10회 재현 후 root cause 가 가설 3 였다면 5 사이클 손해. **확신 강도 무관 N 가설 동시 박제** 가 ROI 우수
- 가설 셋 MECE 설계가 핵심 — 가설 1, 2 가 같은 layer 진단 로그 위치를 다투면 시그널 혼란

## 관련 문서

- [.claude/rules/evaluation.md](../.claude/rules/evaluation.md) — 평가 주도 검증 (실행 결과로 증명)
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §0-1 Step 1 변경 전 영향 분석
- [.claude/skills/unity-log-diagnostic/SKILL.md](../.claude/skills/unity-log-diagnostic/SKILL.md) — Editor.log 자동 추출 + layer 분리 + run 별 판정 스킬
- [evidence-based-debugging.md](evidence-based-debugging.md) — 4단계 증거 기반 디버깅 프로토콜
