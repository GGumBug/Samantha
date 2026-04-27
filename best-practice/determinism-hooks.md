[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 결정론 보존 Hook — 시드 기반 시스템의 단일 정리

시드 기반 결정론 시스템(Hwaseo Battle/Map RNG)은 한 번 깨지면 "동일 입력에서 다른 결과"가 silent하게 누적된다. 보존 지점을 산재한 사례로 두지 말고 **불변식 + Hook 체크리스트**로 박제한다. `refactoring-lessons.md §3` (해시 결정성), `node-lifecycle-patterns.md` (재진입)와 함께 참조.

## 1. 결정론 불변식

| 지점 | 불변식 |
|---|---|
| 시드 생성 | 신규 런에서 1회만, `RunSeed != 0` 보장 |
| 시드 로드 | 디스크 → in-memory 1회, fallback `RunSeed=0`은 반드시 `Debug.LogWarning` |
| Phase 전이 | `RunNodeResumePhase`는 단조 증가, skip 금지 (예: BattleEntered → BattleRewardPending) |
| Save 시점 | `Mark*NodeEntered` 단일 진입점만, **결정론 컨텍스트 확정 후** 호출 |
| Re-entry 판정 | `IsReentrant = (Phase 일치) AND (좌표 일치) AND (snapshot 유효)` 3조건 AND |

## 2. Hook 지점 체크리스트

결정론에 영향을 주는 작업은 **Mark 이전에 박제**되어야 한다. 그래야 Mark의 `_saveCurrentData`가 post-결정론 상태를 디스크에 커밋한다.

- [ ] **저장 hook**: `Mark*NodeEntered` 호출 직전에 RNG 소비 / cooldown 감소 / spawnId 확정 등 결정론 컨텍스트 완결
- [ ] **로드 hook**: 디스크 → in-memory 복원 시 `RunSeed`, Phase, snapshot 3종을 한 번에 (부분 로드 금지)
- [ ] **Re-entry hook**: 재진입은 새 RNG 소비 0건 — 기존 snapshot 재사용만, 신규 추첨 절대 금지
- [ ] **Skip / Auto-clear hook**: 자동 패배·디버그 명령으로 노드를 건너뛸 때도 RNG 소비 패턴이 동일해야 (소비 안 하면 다음 노드 시드 어긋남)
- [ ] **신규 결정론 작업 추가**: Template Method 기반 Framework가 있으면 `EstablishDeterminismContextAsync` 같은 hook으로 박제 (사례: `NodeReentryHandlerBase.EstablishDeterminismContextAsync` — Battle만 override, 나머지는 no-op)

## 3. 재진입 가드 패턴

| Phase | IsReentrant 조건 | 동작 |
|---|---|---|
| `*Entered` (전투 중·구매 중) | 좌표 일치 + 같은 노드 진입 | snapshot 재바인딩, RNG 소비 0 |
| `*RewardPending` / `*Completed` | 좌표 일치 + snapshot 존재 | UI만 복원, 보상 재계산 금지 |
| `Idle` / 미진입 | 항상 false | 신규 진입 경로 (`InitializeNewAsync`) |

## 4. 안티패턴

- **시드 재할당**: 런 도중 `RunSeed = newValue` — 이후 모든 결정론 깨짐. 신규 시드 생성은 신규 런 시작 시 1회만
- **Phase skip**: `BattleEntered` 없이 `BattleRewardPending`으로 직행 — Re-entry 판정이 좌표 만으로 통과해 silent 보상 재계산
- **미커밋 상태 재진입**: spawn 후 `_saveCurrentData` 미호출 상태로 크래시 → 재접속 시 pre-spawn 쿨다운으로 cached rule 반환 → cooldown 영영 감소 안 됨

## 5. 새 결정론 hook 추가 체크리스트

- [ ] RNG 라벨을 **중앙 빌더**(예: `BattleRngLabels`)에 등록 — 직접 string 리터럴 금지
- [ ] 라벨이 (a) 도메인 (b) act/row (c) ordinal/turn 3 컨텍스트를 분리하는지 확인
- [ ] hook 실행 시점이 `Mark*NodeEntered`의 `_saveCurrentData` **이전**임을 명시 (Template Method 활용 권장)
- [ ] Re-entry 경로에서는 hook이 **호출되지 않도록** 가드 (재진입 = 결정론 재소비 금지)
- [ ] 종료 게이트: `grep -rn "RunRngService.Instance.ForSubsystem(\"battle\"" → 모두 빌더 경유` 0건 잔재 확인

## 참고

- [refactoring-lessons.md](refactoring-lessons.md) §3 해시 결정성 / §12.5 SSOT 단일 진입점 보존
- [node-lifecycle-patterns.md](node-lifecycle-patterns.md) §4 Deferred Commit State Machine
- [node-persistence-matrix.md](node-persistence-matrix.md) 저장 SSOT 규칙
