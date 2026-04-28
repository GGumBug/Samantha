[← README로 돌아가기](../README.md)

# Deferred Commit Pattern — Backup → Mutate → Commit/Rollback

사용자가 다단계로 값을 조정하는 동안 **메모리에 즉시 반영**하되, **디스크 저장(Commit)은 명시적 확정 시점에만** 수행하는 패턴. 취소 시 OnEnable 시점 백업으로 메모리 복원.

UIPreference Apply/Cancel 흐름과 PlayerDataManager의 pending 시스템(`MarkBattleRewardPending` 류)이 같은 구조를 공유한다.

## 의도 (Why)

설정 화면·보상 선택 UI 같이 "사용자가 값을 자유롭게 만지며 미리보기를 확인 → 마지막에 적용 또는 취소"가 자연스러운 UX에서:

- **즉시 disk write**는 취소 불가 + I/O 비용 + 부분 적용 시 일관성 깨짐
- **순수 메모리 + 적용 시 일괄 commit**도 미리보기 불가능 (Slider 조작 → 화면 밝기 즉시 반응 없음)

→ "메모리는 즉시 mutate, disk는 deferred commit, 취소 시 메모리 rollback" 분리.

## 3단계 상태 머신

```
[OnEnable]
    │
    ▼
  Backup ──── 현재 메모리 값을 _initialX 필드에 스냅샷
    │
    ▼
  Mutate ──── 사용자 입력 → 메모리 즉시 변경 (이벤트 발행 → 미리보기)
    │
    ├─── [Apply] ──→ Commit (Disk Save) ──→ 메모리 유지
    │
    └─── [Cancel] ──→ Rollback (메모리 = _initial) ──→ 이벤트 재발행
                                                     (UI 재동기화)
```

**핵심 불변식**:
- Backup은 OnEnable 시점에서 단 1회. 메서드 중간에 Backup 갱신 금지 (rollback 기준점 유실)
- Rollback은 setter를 다시 호출 — 이벤트 재발행으로 Dispatcher/구독자가 자동 동기화. 직접 필드 대입 금지

## 사례 1 — UIPreference Apply/Cancel

`Assets/Scripts/UI/Preference/UIPreference.cs:53-59` Backup 필드 선언:

```csharp
// OnEnable 시점의 현재값 backup — Cancel 시 복원, Apply 시 disk commit.
// PlayerDataManager 패턴 답습 — 메모리/디스크 분리, 명시적 commit.
private float       _initialBrightness;
private float       _initialMasterVolume;
private float       _initialBgmVolume;
private float       _initialSfxVolume;
private LocaleType  _initialLocale;
```

`Assets/Scripts/UI/Preference/UIPreference.cs:124-142` OnEnable의 Backup:

```csharp
private void OnEnable()
{
    Time.timeScale = 0f;

    // Backup — Cancel 시 복원 기준점. Apply 미클릭 시 메모리 변경 무시.
    _initialBrightness   = Settings.Brightness;
    _initialMasterVolume = Settings.MasterVolume;
    _initialBgmVolume    = Settings.BgmVolume;
    _initialSfxVolume    = Settings.SfxVolume;
    _initialLocale       = Settings.Locale;
    ...
}
```

`Assets/Scripts/UI/Preference/UIPreference.cs:91-109` Commit/Rollback 분기:

```csharp
private void Close(bool save)
{
    if (save)
    {
        Settings.Save();   // Disk commit
    }
    else
    {
        // Rollback — setter 호출로 이벤트 재발행 → Dispatcher 자동 갱신
        Settings.Brightness   = _initialBrightness;
        Settings.MasterVolume = _initialMasterVolume;
        Settings.BgmVolume    = _initialBgmVolume;
        Settings.SfxVolume    = _initialSfxVolume;
        Settings.Locale       = _initialLocale;
    }
    CloseUI();
}
```

## 적용 기준 (When)

다음 두 조건을 모두 충족하면 강력한 후보:

1. **사용자 변경 자유도가 높음** — 값을 여러 번 조정·실험할 수 있어야 함 (Slider, Dropdown, 복수 선택)
2. **취소 가능성 보장 필요** — "되돌리기" UX가 자연스러움 (설정창, 보상 선택, 캐릭터 빌드 화면)

부분 충족 시:
- 변경이 즉시 비가역(예: 골드 소비)이면 **Claimed vs Applied 분리**(node-lifecycle-patterns.md 참조)가 더 적합
- 미리보기가 불필요하면 **Form 패턴**(임시 buffer → 적용 시 일괄 commit)으로 충분

## 안티패턴

### 1. Setter에서 즉시 disk write

```csharp
// 안티패턴
public float Brightness
{
    get => _brightness;
    set { _brightness = value; SaveToDisk(); }   // 슬라이더 1프레임당 disk I/O
}
```

→ Slider 드래그 한 번에 수십 회 disk write 발생, 취소 불가.

### 2. Rollback 시 직접 필드 대입

```csharp
// 안티패턴
private void Cancel()
{
    Settings._brightness = _initialBrightness;   // 이벤트 미발행 → UI/Dispatcher 동기화 깨짐
}
```

→ UI는 백업값을 표시하지만 다른 구독자(예: 카메라 후처리)는 사용자 변경값 유지.

### 3. Backup 중복 갱신

```csharp
// 안티패턴
private void OnSomeIntermediateAction()
{
    _initialBrightness = Settings.Brightness;   // OnEnable이 아닌 곳에서 백업 갱신 → rollback 기준 유실
}
```

→ Cancel을 눌러도 OnEnable 시점이 아닌 마지막 갱신 값으로 복원되어 의도와 어긋남.

### 4. Apply가 메모리 mutate를 함

Apply는 **이미 메모리에 반영된 값을 disk에 commit하는 행위만** 수행. mutation은 사용자 입력 시점에 이미 끝나 있어야 함.

## 체크리스트

- [ ] Backup은 OnEnable 또는 진입점 1회만 수행하는가?
- [ ] Rollback은 setter/이벤트를 통해 처리되는가? (직접 필드 대입 금지)
- [ ] Commit(Apply)은 mutation 없이 disk write만 수행하는가?
- [ ] 같은 진입점 재오픈 시(예: 설정창 닫고 다시 열기) Backup이 새로 갱신되는가?
- [ ] Cancel 후 외부 시스템(Dispatcher, 카메라, BGM)이 자동 재동기화되는가?

## 관련 문서

- [node-lifecycle-patterns.md](node-lifecycle-patterns.md) — Claimed vs Applied 분리 (비가역 변경용)
- [refactoring-lessons.md](refactoring-lessons.md) — 메서드 분할 / SSOT 단일 진입점
- [solid-unity-principles.md](solid-unity-principles.md) — SRP·OCP 카탈로그
