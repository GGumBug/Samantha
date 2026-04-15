# Camp 휴식 후보 미표시 버그 수정 계획

## Context (왜 이 변경이 필요한가)

### 배경
직전 세션에서 Camp 시스템 전체 리팩토링(7개 항목) 중 **UICampRoom 휴식 버튼 정리** 작업이 포함되어 있었습니다. 기존에는 `_actionButtonOriginal`(UICampActionButton) 하나로 모든 휴식 후보를 `AddStaticButton`으로 생성했지만, 전용 컴포넌트인 `UICampPartyMemberButton`이 이미 존재하므로 이를 활용하도록 구조를 변경했습니다.

이 과정에서 `UICampRoom`에 다음 두 SerializeField가 신규 추가되었습니다:
- `[SerializeField] private RectTransform _restMemberButtonParent;`
- `[SerializeField] private UICampPartyMemberButton _restMemberButtonOriginal;`

### 문제
Unity Editor에서 이 두 신규 필드에 프리팹/오브젝트를 할당하지 않은 상태에서, `RebuildRestSelectionButtons` 메서드가 `_restMemberButtonOriginal == null`이면 멤버 버튼 생성 루프를 건너뛰어 **회복 후보가 하나도 표시되지 않는 회귀 버그**가 발생했습니다.

### 중간 시도와 사용자 방향성
직전 턴에 Ava가 **코드 폴백 경로**를 추가하여(UICampRoom.cs 195-219줄) `_restMemberButtonOriginal`이 null이면 기존 `_actionButtonOriginal`로 버튼을 생성하도록 수정했습니다. 그러나 사용자는 **근본 원인이 Inspector 미할당**임을 확인했으며, 코드 폴백은 과잉 방어(over-engineering)라고 판단하여 다음 방향을 선택했습니다:

> **"폴백 제거 + Inspector 할당"** — 코드는 단순하게 유지하고, Unity Editor에서 SerializeField에 직접 프리팹을 할당하여 해결한다.

이는 CLAUDE.md의 원칙("speculative abstractions 금지", "가상 시나리오 방어 코드 금지")과 Unity 생태계의 관례에 부합합니다.

### 의도한 결과
- `RebuildRestSelectionButtons`는 단일 경로(`UICampPartyMemberButton` 기반)만 유지
- Unity Editor에서 Inspector에 필드를 할당하여 실제 런타임 동작 복원
- 코드 중복과 "두 개의 UI 구성 방식 공존" 상태 해소

## 수정 대상

### 파일 1 — 코드 (폴백 제거)
[d:\Unity_Projects\Hwaseo\Assets\Scripts\Camp\UICampRoom.cs](../../Assets/Scripts/Camp/UICampRoom.cs) — `RebuildRestSelectionButtons` 메서드

**제거할 블록** (현재 195-219줄):
```csharp
else if (_actionButtonOriginal != null)
{
    Transform actionParent = _actionButtonParent != null
        ? _actionButtonParent
        : _actionButtonOriginal.transform.parent;

    for (int i = 0; i < candidates.Count; i++)
    {
        CampRestCandidateData candidate = candidates[i];
        if (candidate == null)
        {
            continue;
        }

        string title = candidate.GetDisplayName();
        string description = string.Format(
            "HP {0}/{1}  회복 {2}",
            candidate.CurrentHp,
            candidate.MaxHp,
            candidate.HealAmount);

        CampRestCandidateData captured = candidate;
        AddStaticButton(actionParent, title, description, true, () => OnRestCandidateClicked(captured));
    }
}
```

**제거 후 구조**: `if (_restMemberButtonOriginal != null)` 블록만 남고, 이후 "뒤로" 버튼 생성 블록(`if (_actionButtonOriginal != null)`)이 이어집니다. `_restMemberButtonOriginal`이 null이면 멤버 버튼은 생성되지 않습니다(Inspector 할당을 강제하는 방식).

### 파일 2 — Unity Editor 작업 (사용자가 수동으로)
UICampRoom이 부착된 프리팹/씬 오브젝트 Inspector에서:
- `Rest Member Button Parent` ← 멤버 버튼이 배치될 컨테이너(RectTransform) 할당
- `Rest Member Button Original` ← `UICampPartyMemberButton` 원본 오브젝트(비활성 상태) 할당

## 재사용되는 기존 함수/유틸리티

- [UICampPartyMemberButton.Setup(CampRestCandidateData, Action<CampRestCandidateData>)](../../Assets/Scripts/Camp/UICampPartyMemberButton.cs#L27): 멤버 이름·HP·회복량 표시 내장
- [CampRestCandidateData.GetDisplayName()](../../Assets/Scripts/Camp/Core/CampRestCandidateData.cs#L14): 표시 이름 획득
- [UICampRoom.ClearRestMemberButtons](../../Assets/Scripts/Camp/UICampRoom.cs#L284): 기존 생명주기 관리 유지
- [UICampRoom.BuildNavigationTargets](../../Assets/Scripts/Camp/UICampRoom.cs#L305): `_restMemberButtons` 순회 경로 유지

## 실행 단계

1. **코드 수정** (Ava에게 재위임): `UICampRoom.cs` 195-219줄의 `else if` 블록 제거
2. **Unity Editor 작업** (사용자): UICampRoom 프리팹 Inspector에서 두 SerializeField 할당
3. **플레이 테스트** (사용자): 캠프 진입 → 휴식 → 회복 후보 버튼 표시 확인

## 검증 방법 (End-to-End)

### 시나리오 A — Inspector 할당 후 정상 경로
1. Unity Editor에서 `_restMemberButtonOriginal`과 `_restMemberButtonParent`를 할당한 프리팹으로 실행
2. 게임 진입 → 캠프 노드 → "휴식" 버튼 클릭
3. **기대**: `UICampPartyMemberButton` 프리팹으로 회복 가능한 파티 멤버 수만큼 버튼이 표시
4. 각 버튼 클릭 시 `OnRestCandidateClicked`가 올바른 `CampRestCandidateData`로 호출
5. 휴식 적용 → HP 회복 → 메인 페이지로 복귀 확인

### 시나리오 B — 생명주기 검증
- 휴식 화면 ↔ 메인 화면 전환 시 `ClearRestMemberButtons`로 이전 버튼 파괴 확인
- 캠프 UI 종료 시(`OnClosed`) 메모리 누수 없는지 Profiler로 확인
- 컨트롤러 네비게이션: 키보드/게임패드로 멤버 버튼들 사이 이동 + "뒤로" 버튼까지 포커스 가능한지 확인

### 시나리오 C — 네거티브 테스트 (Inspector 미할당 시)
- 만약 어떤 프리팹에서 `_restMemberButtonOriginal`이 여전히 null이면 **멤버 버튼이 표시되지 않음**(폴백 제거됨). 이는 의도된 동작이며, 디자이너가 Console에서 원인을 빠르게 파악할 수 있도록 추후 `Debug.LogError`를 추가할지는 별도 논의.

### 회귀 테스트 체크리스트
- [ ] Inspector 할당 후 회복 후보가 정상 표시됨
- [ ] 각 버튼 클릭 시 올바른 후보가 선택됨
- [ ] "뒤로" 버튼이 정상 표시됨
- [ ] 네비게이션에서 멤버 버튼 + "뒤로" 버튼 모두 포커스 가능
- [ ] 화면 전환 시 버튼 중복 생성/잔존 없음
- [ ] 코드 195-219줄의 `else if` 블록이 완전히 제거되었는지 확인
