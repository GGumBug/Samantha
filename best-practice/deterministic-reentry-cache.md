[← README로 돌아가기](../README.md)

# Deterministic Reentry Cache (Idempotent Replay) Pattern

**의도된 결정론 design pattern**. cached path 가 다음 4종 우회를 **함께** 보이면 "안전 검사 누락 버그" 가 아닌 **재진입 결정론 보존 패턴** 으로 우선 판정.

## 패턴 정의

cached path 의 4종 우회 동거 시 idempotent replay 의도:

| 우회 종류 | 표면 형태 | 의도 |
|----------|----------|------|
| 1. IsEnable bypass | `enabled` 플래그 / `IsActive` 가드 미통과 | 비활성 상태에서도 cached ID 로 재구성 |
| 2. OnDataChosen no-op | 신규 추첨 시점의 hook (이벤트/RNG 갱신) 미발동 | 재진입은 추첨이 아니므로 hook 부재가 정상 |
| 3. Set... no-op | setter 미호출 (state mutation 0) | live ↔ raw 양쪽 이미 cached ID 보유, 재 set 불필요 |
| 4. ID lookup-only | `FindRuleById(cachedId)` 한 줄 lookup | 동일 ID → 동일 결과 (deterministic) |

**핵심**: 위 4종이 **함께** 나타나면 cached path 의 책임이 **"새 결정을 하지 말 것"** — 이미 결정된 ID 로 동일 결과 재구성. 시뮬레이션 / Save-Load Resume / 재접속 시 결정론 보장이 의도.

## 본 사이클 사례 — EnemySpawnManager.SelectData (2026-05-11)

`EnemySpawnManager.SelectData` 의 `existingId != -1` 분기가 4종 우회 모두 동거:

```csharp
public EnemySpawnRule SelectData(int existingId = -1)
{
    if (existingId != -1)
    {
        // 1. IsEnable bypass: enabled 체크 없음
        // 2. OnDataChosen no-op: 이벤트 발사 없음
        // 3. Set no-op: live/raw 모두 이미 existingId 보유
        // 4. ID lookup-only: FindRuleById 한 줄
        return FindRuleById(existingId);
    }
    // 신규 추첨 path (정상 흐름)
    return PickRandomRule();
}
```

**진단 과정 (commit `b085eeda`)**:
- 초기 의심: "cached path 가 안전 검사 우회 → 누락 버그?"
- 실제 의도: **재진입 시 결정론 보존** — 동일 ID 로 동일 적 spawn 보장
- 진짜 root cause: 별도 layer (live ↔ raw SoT 분기) 의 `selectedEnemySpawnDataId = -1` 박제 → cached path 미발동
- cached path 자체는 정상 — 외부에서 cached ID 가 `-1` 로 잘못 박제된 게 원인

## 적용 도메인

- **RNG / 시뮬레이션**: 같은 seed 로 같은 결과 재현 (battle replay, save-load determinism)
- **트랜잭션**: idempotent retry (network 재시도 시 중복 effect 방지)
- **Save-Load Resume**: 재접속 시 in-progress 노드/배틀의 이전 결정 복원
- **A/B 테스트**: 동일 사용자에게 동일 variant 보장

## 사고 회피 룰

**cached path 의 안전 검사 우회를 보면 의도 검증 의무**:

1. **4종 우회 동거 확인** (IsEnable bypass + side-effect 0 + Set no-op + lookup-only) — 4개 다 보이면 idempotent replay 의도 우선 판정
2. **"누락 버그" 단정 금지** — cached path 의 caller chain 추적 (어떤 시점에 호출되는가? Resume / 재접속 / 시뮬레이션?)
3. **진짜 root cause 는 다른 layer** — cached ID 가 의도된 값인지 검증 (예: `selectedEnemySpawnDataId = -1` 박제 layer 검증). 상세 [multilayer-state-sync.md](multilayer-state-sync.md) 의 2-layer 변형 (live ↔ raw)
4. **테스트 시나리오 의무**: ① 정상 추첨 ② 동일 ID 재진입 ③ Save → Load → 동일 결과 ④ 비활성 상태 cached path 호출

## 관련 문서

- [multilayer-state-sync.md](multilayer-state-sync.md) — Live ↔ Raw 2-layer SoT 분기 (cached ID 박제 layer)
- [determinism-hooks.md](determinism-hooks.md) — 결정론 RNG 훅 (라벨 기반 SSOT)
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §3 디자인 패턴 우선순위
