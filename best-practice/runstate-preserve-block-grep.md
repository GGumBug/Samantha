[← README로 돌아가기](../README.md)

# RunState Capture/Restore Preserve Block 누락 박멸

`PlayerRunStateData` 처럼 **Capture (snapshot 직전 새 인스턴스 생성) → Preserve block 으로 일부 필드만 명시 복원** 하는 데이터 클래스에 신규 non-transient 필드 추가 시, preserve block 한 줄 누락하면 **capture 한 번 돌 때마다 해당 필드가 silent 하게 default 값으로 리셋** 된다. 컴파일 에러 없음 + 즉시 가시 증상 없음 → 다중 가설 진단 + 5 layer 박제 후에야 root cause 확정 가능.

## 본 사이클 사례 (2026-05-11 PotionDropChancePercent)

**증상**: 보스층 클리어 후 다음 act 진입 시 포션 드롭 확률이 **항상 default (40)** 으로 silent 리셋. POCO clamp / Save / Load / Reset 모두 정상 동작 → 가시 증상은 한 가지 ("값이 안 늘어남") 인데 root cause 후보가 5 layer.

**root cause**: `RunLifecycleService.CaptureRunStateFromPlayerManagerInternal` 의 preserve block 에 `PotionDropChancePercent` 한 줄 추가 누락. capture 시점마다 `new PlayerRunStateData()` → preserve block 으로 일부 필드만 복원 → `PotionDropChancePercent` 는 default (40) 로 휘발.

**수정 1줄**:
```csharp
private void CaptureRunStateFromPlayerManagerInternal(...)
{
    var snapshot = new PlayerRunStateData();
    // Preserve non-transient fields (이 블록에 신규 필드 1줄 추가 의무)
    snapshot.RunSeed = current.RunSeed;
    snapshot.CurrentAct = current.CurrentAct;
    // ...
    snapshot.PotionDropChancePercent = current.PotionDropChancePercent;  // ← 누락분
}
```

Stage 4 commit `274a8976` — 1줄 수정으로 7건 진단 로그 + 2회 재현 후 root cause 해결.

## 룰 (Capture/Restore 패턴 데이터 클래스 신규 필드 추가 시)

### 1. 사전 grep 의무

신규 필드 추가 PR 시작 전:

```bash
grep -n "Preserve non-transient" Assets/Scripts/
grep -nE "new PlayerRunStateData\(\)" Assets/Scripts/
```

Preserve block 위치 모두 식별 → 신규 필드 한 줄 추가 누락 0건 보장.

### 2. 코드 주석 자체가 정답 박제

Preserve block 위에 다음 주석 의무 (Future-proofing):

```csharp
// ⚠ PlayerRunStateData에 새 non-transient 필드 추가 시 이 블록에 한 줄 추가 필수.
// 누락하면 capture 한 번 돌 때마다 해당 필드가 silent 하게 리셋된다.
```

### 3. 종료 게이트 grep

작업 완료 직전 검증:

```bash
# 신규 필드명이 Capture preserve block 에 등장하는지 확인
grep -n "PotionDropChancePercent" Assets/Scripts/Managers/Lifecycle/RunLifecycleService.cs
```

0건이면 누락 — 즉시 추가.

## 일반화 — Capture/Restore 패턴 식별

다음 패턴이면 본 룰 적용:
- `new T()` 로 snapshot 인스턴스 생성 후 일부 필드만 명시 복원하는 메서드
- 메서드명에 `Capture` / `Snapshot` / `Take*State` 포함
- `PlayerRunStateData` 외에도 `BattleSnapshot` / `EncounterSnapshot` / `MapSnapshotState` 등 동일 위험

## 헌법 §0-1 Step 1 cross-link

본 룰은 헌법 [engineering-constitution.md §0-1 Step 1](../.claude/rules/engineering-constitution.md) "변경 전 영향 분석" 의 데이터 클래스 신규 필드 추가 sub-case. grep 결과 표 작성 의무 + 모든 Capture/Restore 진입점 식별 후 코드 작성.

## 시니어 회고

- "필드 한 줄 추가" = 영향 0 직관은 함정 — Capture/Restore 패턴이면 영향 1 (preserve block)
- 컴파일 에러 안 남 + 가시 증상 일관성 (항상 default) → 진단 매트릭스 5 layer 필요 → 1 줄 누락 비용이 진단 7건 cost 증폭
- 코드 주석 박제 = 다음 합류자 학습 비용 0 + 자동 sweep 가능

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §0-1 Step 1 변경 전 영향 분석
- [multi-hypothesis-diagnostic.md](multi-hypothesis-diagnostic.md) — N 가설 동시 진단 (본 사례 5 layer 박제로 1회 재현 root cause 확정)
- [multilayer-state-sync.md](multilayer-state-sync.md) — SSOT 단일 진입점 우회 금지
