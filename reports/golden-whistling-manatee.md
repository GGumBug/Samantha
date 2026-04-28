# Localization 시스템 신규 구축 계획

## Context

Hwaseo 프로젝트는 BGDatabase를 단일 데이터 SSOT로 사용합니다. 기존 Localization 인프라(레거시 `TextDatabase` Addressables + Unity Localization Package `LocalizationSettings`/`LocalizedString`)는 다음 이유로 **전면 제거 후 신규 구축**합니다:

1. **이중 저장소 SSOT 위반** — BGDatabase 신규 시트와 정수 코드 테이블 공존, 키-코드 대응이 코드에 하드코딩.
2. **즉시 반영 부재** — `LocalizedString.GetLocalizedString()`은 비동기 로드 가정, "Settings 변경 즉시 모든 텍스트 갱신" 요구사항과 충돌.
3. **에디터 워크플로 단절** — `TextDatabase` ScriptableObject는 정수 code 수동 부여, 기획자/번역가가 BGDatabase 시트를 직접 편집하는 워크플로와 분리됨.
4. **ScriptableObject 직렬화 의존** — `IdentifiedObject.LocalizedData` 필드가 모든 자식 에셋에 박혀 있어 BGDatabase 키로 마이그레이션 시 데이터 정리 필요.

**대체 시스템 핵심 원칙**:
- BGDatabase가 **유일한 데이터 SSOT** — 시스템별 시트 분리(`LocalizedText_System`, 향후 `LocalizedText_Battle`/`LocalizedText_Card` 등).
- 4개 언어 지원 — `ko`, `en`, `ja`, `zh_Hans`.
- 언어 변경 즉시 반영 — `Settings.LocaleChanged` → `L10n.LocaleApplied` → 모든 `LocalizedTextBinder` 동기 갱신.
- DIP boundary 1곳에 BGDatabase 의존 격리, OCP로 시트 추가 = 등록 1줄.

## Architecture

```
                    Settings.cs (hub)
                  Locale / LocaleChanged
                          │
                          ▼
   ┌────────────────────────────────────────────────────────┐
   │                L10n  (static facade — SSOT)            │
   │   T(key) / Format(key, args) / HasKey(key)             │
   │   LocaleApplied event  /  Initialize(repo)             │
   └────────────────────────┬───────────────────────────────┘
                            │
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │         ILocalizedTextRepository (interface)           │
   │   bool TryGet(string key, LocaleType, out string)      │
   └────────────────────────┬───────────────────────────────┘
                            │
                            ▼
   ┌────────────────────────────────────────────────────────┐
   │       CompositeLocalizedTextRepository                 │
   │   - 시스템별 시트 source 등록 (OCP)                    │
   │   - Resolution: 등록 순서대로 첫 매치                  │
   └────────────────────────┬───────────────────────────────┘
                            │ registers
            ┌───────────────┴────────────────┬───────────────┐
            ▼                                ▼               ▼
   BGSheetTextSource             BGSheetTextSource     BGSheetTextSource
   <DB_LocalizedText_System>     <DB_LocalizedText_    <DB_LocalizedText_
                                  Battle (future)>      Card (future)>

   UI 즉시 반영:
   ┌────────────────────────────────────────────────────────┐
   │   LocalizedTextBinder : MonoBehaviour                  │
   │   [SerializeField] string _key                         │
   │   [SerializeField] TMP_Text _target                    │
   │   OnEnable: subscribe LocaleApplied + Apply()          │
   │   OnDisable: unsubscribe                               │
   └────────────────────────────────────────────────────────┘
```

**SOLID 매핑**:

| 원칙 | 적용 |
|------|------|
| §1 SRP | 각 클래스 단일 책임 (Source=시트 1개 캐싱, Repository=조합, L10n=조회 facade, Binder=UI 갱신) |
| §1 OCP | 새 시트 추가 = `repo.Register(new BGSheetTextSource<DB_X>(...))` 1줄 |
| §1 LSP | 모든 Source는 `TryGet` 동일 계약 |
| §1 ISP | `ILocalizedTextRepository` (조회) vs `ILocalizedTextSource` (시트 단위) 분리 |
| §1 DIP | `L10n`은 인터페이스에 의존, BGDatabase 구체 의존은 `BGSheetTextSource`에만 |
| §2 SSOT | Locale → `Settings.Locale`, 텍스트 → BGDatabase, 조회 진입점 → `L10n` |
| §2-1 양방향 검증 | `Settings.Locale` setter → 항상 `LocaleChanged` 발행 → `L10n.LocaleApplied`. 양 방향 참 (private `_locale` 직접 변경 경로 없음) |
| §3 패턴 정당화 | Observer (LocaleApplied) — 사용처 ≥ 수십 UI / Strategy (Source switch) — 사용처 ≥ 3 시트 예정 |

## Critical Files

| # | 파일 | 종류 | 위임 |
|---|------|------|------|
| 1 | [Assets/Scripts/Localization/LocaleType.cs](../../Assets/Scripts/Localization/LocaleType.cs) | 수정 — `CHINESE_SIMPLIFIED` 추가 | 직접 |
| 2 | [Assets/Scripts/Localization/L10n/ILocalizedTextRepository.cs](../../Assets/Scripts/Localization/L10n/ILocalizedTextRepository.cs) | 신규 | 직접 |
| 3 | [Assets/Scripts/Localization/L10n/ILocalizedTextSource.cs](../../Assets/Scripts/Localization/L10n/ILocalizedTextSource.cs) | 신규 | 직접 |
| 4 | [Assets/Scripts/Localization/L10n/CompositeLocalizedTextRepository.cs](../../Assets/Scripts/Localization/L10n/CompositeLocalizedTextRepository.cs) | 신규 | **Jarvis** |
| 5 | [Assets/Scripts/Localization/L10n/BGSheetTextSource.cs](../../Assets/Scripts/Localization/L10n/BGSheetTextSource.cs) | 신규 — 제네릭 | **Jarvis** |
| 6 | [Assets/Scripts/Localization/L10n/L10n.cs](../../Assets/Scripts/Localization/L10n/L10n.cs) | 신규 — facade | **Jarvis** |
| 7 | [Assets/Scripts/Localization/L10n/LocalizedTextBinder.cs](../../Assets/Scripts/Localization/L10n/LocalizedTextBinder.cs) | 신규 — MonoBehaviour | **Ava** |
| 8 | [Assets/Scripts/GameSettings/Settings.cs](../../Assets/Scripts/GameSettings/Settings.cs) | 수정 — Chinese 매핑 + `ChangeLocale` stub 제거 | 직접 |
| 9 | 부트스트랩 진입점 (Jarvis 식별) | 수정 — 시트 등록 + `L10n.Initialize` | **Jarvis** |
| 10 | [Assets/Scripts/DGCore/IdentifiedObject.cs](../../Assets/Scripts/DGCore/IdentifiedObject.cs) | 수정 — `LocalizedData` → `string nameKey/descKey` | **Sonny** |
| 11 | Editor migration script | 신규 (1회성, 작업 후 삭제) | **Jarvis** |
| 12 | [Assets/Scripts/Localization/TextDB/](../../Assets/Scripts/Localization/TextDB/) | **삭제** + Editor + .asset | **Jarvis** |
| 13 | [Assets/Localization/](../../Assets/Localization/) + `Packages/manifest.json` | **삭제** + Package 의존 정리 | **Jarvis** |
| 14 | `BattleManager`, `IntroSubtitleController` 등 호출처 | 수정 — `L10n.T(key)` 치환 | **Sonny** |
| 15 | UI 검증 표면 — UIPause, UIPreference | `LocalizedTextBinder` 부착 | **Ava** |

## Key Implementations (시그니처만)

### `BGSheetTextSource<TEntity>` (Jarvis)
```csharp
public sealed class BGSheetTextSource<TEntity> : ILocalizedTextSource where TEntity : BGEntity
{
    public BGSheetTextSource(
        Action<Action<TEntity>> forEach,                  // DB_X.ForEachEntity
        Func<TEntity, string> keyOf,                      // e => e.f_Key
        Func<TEntity, LocaleType, string> textOf);        // (e, l) => locale switch

    public bool TryGet(string key, LocaleType locale, out string value);
}
```

### `L10n` (Jarvis) — 즉시 반영 핵심
```csharp
public static class L10n
{
    public static event Action LocaleApplied;
    public static LocaleType CurrentLocale => Settings.Locale;

    public static void Initialize(ILocalizedTextRepository repo)
    {
        if (_initialized) return;                          // idempotent
        _repo = repo;
        Settings.LocaleChanged += _ => LocaleApplied?.Invoke();  // 동기 체인
        _initialized = true;
    }

    public static string T(string key) =>
        _repo != null && _repo.TryGet(key, Settings.Locale, out var v)
            ? v : LogMissingAndReturnPlaceholder(key);
    public static string Format(string key, params object[] args) => string.Format(T(key), args);
    public static bool HasKey(string key);
}
```

### `LocalizedTextBinder` (Ava)
```csharp
public sealed class LocalizedTextBinder : MonoBehaviour
{
    [SerializeField] private string _key;
    [SerializeField] private TMP_Text _target;
    [SerializeField] private string[] _staticArgs;

    public void SetKey(string key);
    public void SetArgs(params object[] args);

    private void OnEnable() { L10n.LocaleApplied += Apply; Apply(); }
    private void OnDisable() => L10n.LocaleApplied -= Apply;
    private void Apply();
}
```

### 부트스트랩 (Jarvis)
```csharp
var repo = new CompositeLocalizedTextRepository();
repo.Register(new BGSheetTextSource<DB.DB_LocalizedText_System>(
    DB.DB_LocalizedText_System.ForEachEntity,
    e => e.f_Key,
    (e, l) => l switch
    {
        LocaleType.KOREAN              => e.f_ko,
        LocaleType.ENGLISH             => e.f_en,
        LocaleType.JAPANESE            => e.f_ja,
        LocaleType.CHINESE_SIMPLIFIED  => e.f_zh_Hans,
        _ => e.f_en
    }));
L10n.Initialize(repo);
// 미래 시트: repo.Register(new BGSheetTextSource<DB.DB_LocalizedText_Battle>(...));
```

## Implementation Order (Wave-based)

### Wave 0 — 사전 정리 + 사용자 보고
- 워킹트리 Spine 잔존 변경 처리 옵션(A 제외 / B 되돌리기 / C 별도 커밋) 사용자에게 보고 후 결정 받기.
- `BattleManager.GetString(10001)` 등 정수 code 호출처 인벤토리 작성 → 신규 시트 추가가 필요한 키 목록을 사용자에게 보고. 사용자가 시트에 키 추가 후 Wave 7 진행 (보수적 기본값).

### Wave 1 — 기반 (직렬 → 병렬)
1. `LocaleType.cs` enum 확장 (직접, +1줄)
2. `ILocalizedTextRepository.cs`, `ILocalizedTextSource.cs` (직접, 병렬, 신규)

### Wave 2 — 코어 구현 (Jarvis 단일)
3. `BGSheetTextSource.cs` + `CompositeLocalizedTextRepository.cs` + `L10n.cs` 일괄 (신규 파일 묶음, 단일 위임이 효율적)

### Wave 3 — UI 컴포넌트 (Ava)
4. `LocalizedTextBinder.cs` 신규

### Wave 4 — Settings + 부트스트랩 (직렬 hub)
5. `Settings.cs` Chinese 매핑 + `ChangeLocale` stub 제거 (직접, +2줄/-5줄)
6. 부트스트랩 진입점 식별 + 시트 등록 + `L10n.Initialize` 호출 (Jarvis)

### Wave 5 — IdentifiedObject 데이터 마이그레이션 (Sonny + Jarvis 직렬)
7. **Sonny**: `IdentifiedObject.cs` 필드 교체 (`LocalizedData` → `string nameKey/descKey`)
8. **Jarvis**: 1회성 Editor migration script 작성 — 기존 `LocalizedString.tableEntryReference` → `nameKey` 자동 추출. 실행 후 script 삭제.

### Wave 6 — 레거시 전면 제거 (Jarvis 단일)
9. `Assets/Scripts/Localization/TextDB/` 디렉토리 삭제
10. `Assets/Database/TextDatabase.asset` + Addressables 그룹 정리
11. `Assets/Localization/Localization Settings.asset` + 관련 .asset 삭제
12. `Packages/manifest.json`에서 `com.unity.localization` 제거
13. `IntroSubtitleController.cs:29` `GetLocalizedString()` → `L10n.T` 치환

### Wave 7 — 호출처 치환 (Sonny + Ava 병렬)
14. **Sonny**: `BattleManager` 등 정수 code 호출처 → `L10n.T(key)` 치환 (Wave 0에서 사용자 시트 추가 완료된 키 한정)
15. **Ava**: UIPause + UIPreference에 `LocalizedTextBinder` 부착 + 키 SerializeField 할당 (검증용 2개 표면)

### Wave 8 — 검증
16. 4개 언어 즉시 반영 시나리오 실행 (아래 Verification)
17. 사용자에게 게임 전체 UI 확장 진행 여부 결정 받기 (검증 통과 후)
18. `git status --short` 워킹트리 최종 정리

## Verification

### 즉시 반영 시나리오 (필수)
1. Play 모드 → ESC → UIPause 표시
2. UIPause 위에 UIPreference 오픈 → Language → English 선택
3. **UIPause + UIPreference 양쪽 텍스트가 같은 프레임에** 영어로 변경 확인
4. 한국어 → 일본어 → 중국어 간체 순회 검증
5. Console `[L10n:` warning 0건

### 단위 테스트 (POCO 가능)
- `L10n.T_returns_value_for_known_key`
- `L10n.T_returns_placeholder_for_missing_key`
- `L10n.Format_applies_string_Format`
- `Composite_first_source_wins`
- `BGSheetTextSource_locale_field_selection_correct`
- `LocaleChanged_triggers_LocaleApplied_synchronously`
- `Initialize_is_idempotent`

### `git diff --stat` 기대치 (대략)
```
Wave 1~4: +250 lines / 8 files
Wave 5  : ±50 lines / 1 file + N개 .asset 갱신
Wave 6  : -200 lines / 5 files 삭제 + Package manifest 1
Wave 7  : ±100 lines / N files (호출처 수에 비례)
─────────────────────────────────────────────────────
Total   : 12~20 files, ScriptableObject .asset 갱신 별도
```

### 워킹트리 정리 의무
현재 Spine `.asset`/`.mat` 잔존 (Character_01~03, Monster_101~107) — 본 작업 무관. Wave 0에서 사용자 처리 옵션 결정.

## Trade-offs (헌법 §7)

| 결정 | 양보 | 사유 |
|------|------|------|
| `LocalizedTextBinder` MonoBehaviour 도입 | §0 추상화 비용 | 즉시 반영 + 사용처 ≥ 수십 → §3 정당화. 미도입 시 모든 UI 수동 구독 보일러플레이트 → DRY 위반이 더 큼 |
| `BGSheetTextSource<T>` 제네릭 + delegate | §0 진입 장벽 | 시트 ≥ 3 예상 → 등록 1줄 vs 클래스 복사. OCP 정당화 |
| Editor migration script 1회성 | §0 자동화 비용 | ScriptableObject `.asset` 다수 (수십~수백) → 수동 입력 비현실적. script는 작업 후 삭제 — 영구 비용 0 |
| `string` 키 (enum 아님) | 컴파일 안전성 | BGDatabase `f_Key`가 SSOT. enum 자동 생성은 Phase 후속 (사용처 늘면 도입) |
| 레거시 전면 제거 (gradual deprecate 아님) | §5 호환성 hack 회피 | 사용자 명시적 승인. 두 시스템 공존 유지가 §2 SSOT 더 크게 위반 |

## 기본 결정 (Open Questions 응답 반영)

사용자 승인을 받았으나 4개 Open Question에 별도 답변 없으므로 **합리적 기본값**을 적용하되, **Wave 0에서 재확인 보고** 의무를 가집니다:

| Q | 기본값 |
|---|------|
| 레거시 전면 제거 OK? | **Yes** (사용자 의도 명시 — Wave 6 진행) |
| 정수 code 호출처 시트 추가 시점 | **Wave 0에서 키 인벤토리를 사용자에게 보고 → 사용자가 시트 추가 후 Wave 7 진행** |
| `LocalizedTextBinder` 적용 범위 | **Wave 7에서 검증용 2개 표면 (UIPause + UIPreference) 우선, 검증 통과 시 게임 전체 확장 사용자 결정** |
| Editor migration script | **Jarvis가 자동 작성 + 실행 + 삭제** (Wave 5) |

## Critical Path 의존 순서

```
Wave 0 (사용자 보고) → 1 → 2 → 3, 4 (병렬) → 5 → 6 → 7 (Sonny + Ava 병렬) → 8 (검증) → 9 (확장 결정)
```

각 Wave 종료 시 `git status --short` + `git diff --stat` 보고로 작업 범위 외 변경 추적 (헌법 위임 종료 의무).
