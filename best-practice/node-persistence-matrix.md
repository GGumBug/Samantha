[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 노드 영속화 매트릭스 — Hwaseo 5-노드 저장 타이밍 계약

로그라이크 노드 세션의 **디스크 저장 타이밍**은 개별 노드 단위로 판단하지 말고 **전체 트랜잭션 계약**으로 검증해야 합니다. 2026-04-24 Treasure 노드 추가 중 "Treasure는 단순하니 즉시 커밋 OK" 판단이 **전체 계약 위반**으로 교정된 인시던트에서 도출.

## 5-노드 매트릭스

| 노드 | 진입 시 `_saveCurrentData` | `Exit*Session` 호출 | `RelicAutoSaveSuppression` |
|---|---|---|---|
| Battle | O (`MarkBattleNodeEntered`) | — (세션 개념 없음) | — |
| Encounter | O (`MarkEncounterNodeEntered`) | `EncounterManager.ExitEncounterSession` | — |
| Camp | O (`MarkCampNodeEntered`) | — (세션 개념 없음) | — |
| Shop | O (`MarkShopNodeEntered`) | `ShopManager.ExitShopSession` | O |
| Treasure | O (`MarkTreasureNodeEntered`) | `TreasureManager.ExitTreasureSession` | O |

## 계약 (Invariant)

1. **노드 내부 상태 변경은 in-memory만** — 구매/획득/선택 효과는 `_pending*` 리스트에 누적
2. **디스크 저장은 다음 노드 진입 시 `Mark*`의 `_saveCurrentData()` 에서 일괄 처리** — 지연 커밋 (Deferred Commit)
3. **세션 개념이 있는 노드(Shop/Treasure/Encounter)** 는 `Exit*Session` 에서 pending 리스트를 applied로 flush
4. **`RelicAutoSaveSuppression`** 은 RelicInventory 자동 저장이 중간 시점에 디스크를 건드리는 것을 억제 (Shop/Treasure에서 필요)

## 판단 실수 패턴

"이 노드는 단순하니 즉시 커밋해도 되지 않나?" **금지**. 개별 노드 단위 판단은 `Mark*NodeEntered` 훅이 보장하는 **원자성 계약**을 깨뜨림. 재입장·중간 종료 시나리오가 다른 노드와 섞이면 silent 재지급/누락 발생.

## 새 노드 추가 시 체크리스트

- [ ] `Mark[Node]NodeEntered` 에서 `_saveCurrentData()` 호출 포함
- [ ] 세션 개념이 있으면 `Exit[Node]Session` 메서드 제공 (pending → applied flush)
- [ ] RelicInventory를 건드리면 `RelicAutoSaveSuppression` 래핑
- [ ] 매트릭스 표에 행 추가 (위 문서 + `node-lifecycle-patterns.md` 체크리스트)
- [ ] 다른 노드 매니저의 `Exit*Session` 흐름과 동일한 계약 유지 확인

## 저장 SSOT

매트릭스의 "진입 시 `_saveCurrentData`" 열은 **저장 SSOT 규칙**의 결과다. 위반 시 매트릭스 자체가 무효화된다.

- [ ] 노드 진입 저장은 **`Mark*NodeEntered` 단일 메서드만** 호출 — `PlayerData` / `PlayerRunStateData` 직접 set 금지
- [ ] 진입 SSOT는 **(a) 좌표 정규화 (b) Phase 전이 (c) commit 트리거** 3종을 한 곳에서 처리
- [ ] 새 노드 타입은 진입 SSOT의 **Switch / Strategy 1줄 추가만** 허용 — 별도 `Mark*Entered` 메서드 신설 금지
- [ ] 위반 탐지 grep: `git grep "PlayerRunStateData\." -- '*Manager.cs' '*Service.cs'` 결과에서 `Mark*NodeEntered` 미경유 호출은 모두 위반
- [ ] 매트릭스 "타이밍" 칸을 변경할 때는 SSOT 메서드의 **분기 표 동기화 의무** — 매트릭스만 갱신하고 메서드 분기를 빠뜨리면 silent 누락

## 참고

- [node-lifecycle-patterns.md](node-lifecycle-patterns.md) — Deferred Commit State Machine 전체 구조
- [refactoring-lessons.md](refactoring-lessons.md) 섹션 17 — 3단계 리팩토링 분할 기법
