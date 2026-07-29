# Glob: **/*.cs

## L10n String Snapshot SSOT 헌법 (§2-0 시리즈 — [engineering-constitution.md](engineering-constitution.md) §2 SSOT에서 분리)

> 헌법 200줄 정책 준수를 위해 분리된 파일. 외부 문서의 "헌법 §2-0-1/§2-0-2" 인용은 본 파일의 동일 섹션 번호를 가리킨다. 적용 강제력은 헌법 본문과 동일 (Glob 자동 주입).

### 2-0. Caller-Driven UI String Snapshot 안티패턴 (자동 식별 의무)

UI가 caller로부터 string 결과를 받아 표시하는 패턴(`SetMessage(text)`, `Setup(title)`, `txt.text = caller가 전달한 결과`)은 **string snapshot이 SoT처럼 동작** → 시트 SSOT 위반.

증상: UI 활성 중 언어 변경 시 자동 갱신 안 됨. 다른 UI는 갱신되는데 caller-driven UI만 한국어/일본어/영어 혼재.

자동 의심 트리거:
- caller가 `L10n.T(...)` / `L10n.Format(...)` 결과를 UI에 전달
- UI 컴포넌트가 `LocalizationDispatcher.LocaleApplied` 미구독
- 옛 string 시그니처 (`Setup(string title)`)

해결 — **키 보존 + Observer 패턴**:
- UI에 `_titleKey, _titleArgs` 멤버 보존
- `OnEnable/OnDisable`에서 `LocalizationDispatcher.LocaleApplied` 구독
- 시그니처 `(string titleKey, params object[] titleArgs)` 변경
- caller는 키만 전달

(2026-04-29 RewardButton string snapshot 사고: UIRewards 활성 중 언어 토글 시 reward 버튼 텍스트만 옛 언어 잔존)

**금기 합리화** (헌법 §5 위반):
- ❌ "popup transient라 영향 작음" — 라이프사이클 추측으로 SSOT 위반 보존 금지
- ❌ "caller가 항상 직접 호출하니 dead path"
- ❌ "Quick fix" — 사용자 명시 승인 + 후속 task 등록 의무

#### 2-0-1. 데이터 흐름 String Snapshot 절대 금지 (Layer-by-Layer 안티패턴 박멸)

L10n 마이그레이션이 부분적으로 끝나 같은 안티패턴이 다른 layer 에서 재발하는 사고를 막기 위한 박제 룰.

**구조적 원인**: 데이터 흐름의 각 layer 마다 snapshot 이 생긴다.
```
BGDB Sheet → Domain.NameKey (key) → *VisualData.DisplayName (STRING ← snapshot 1)
           → UI.Setup (txtName.text = string ← snapshot 2)
           → UI._tooltipTitle (string ← snapshot 3)
```
한 layer 만 fix 하면 다음 layer 의 snapshot 이 안티패턴을 보존. 모든 layer 일괄 수정 의무.

**룰**:
1. **데이터 클래스 (`*VisualData`/`*ViewData`/`*RowData`/`*Model`/`*Snapshot`) 는 사용자 노출 텍스트를 string 으로 보유 금지**. **키만** 보유 (`NameKey`, `DescriptionKey`, `TitleKey` 등).
2. **`L10n.T()` / `L10n.Format()` 호출은 표시 직전 UI 컴포넌트 내부에서만** (presentation boundary). Factory/Resolver/Repository/ViewModel 에서 호출 후 string 필드에 박으면 안티패턴.
3. **사용자 노출 텍스트를 표시하는 모든 UI 컴포넌트는 `ILocaleAware` 구현 의무** + 키 보존 멤버 + `LocalizationDispatcher.LocaleApplied` 구독 + LocaleApplied 시 표시 재계산. tooltip / popup / 동적 라벨 모두 포함.

**자동 검증 grep 패턴 (위임 시작 + 종료 시 의무)**:

```
# Pattern A — 데이터 클래스에 string 텍스트 필드
grep -rE "class.*(VisualData|ViewData|RowData|Model|Snapshot).*\{" -A 30 | grep -E "public (readonly )?string (Name|Description|Title|Label|DisplayName|DisplayDescription)"

# Pattern B — L10n.T 결과를 변수/필드에 박는 즉시 평가
grep -rE "(name|desc|description|title|label)\s*=\s*L10n\.(T|Format)\("
```

**둘 다 0건 아니면 안티패턴 잔재** — 추가 sweep 필수. **Pattern B 발견 시 view 가 직접 박제하는지 caller chain 추적 의무** — grep 결과 자동 위반 판정 금지, 사용 흐름 검증 (PlayerId/unitId 기반 lazy re-resolve 사용 시 정합).

(2026-04-29 Shop 유물 표시 재발 사고: Relic 마이그레이션 1차에서 `RelicDefinition.NameTextKr` 제거했지만 `ShopSlotVisualData.DisplayName` 와 `UIShopSlot._tooltipTitle` 가 여전히 string snapshot → 상점 슬롯 + 툴팁이 활성 중 언어 토글 미반영. 사용자 시니어 검토자 역할로 layer 누락 패턴 박제 요청)

**4-Layer 데이터 흐름 일관성** (Tooltip + {value} placeholder 등 다중 layer 파이프라인): [best-practice/multilayer-locale-snapshot.md](../../best-practice/multilayer-locale-snapshot.md) — 키 보존 + 표시 직전 lazy resolve.

#### 2-0-2. View-Level ILocaleAware 강제 — Manager/Static-Event 우회 금지

L10n 갱신 콜백을 **도메인 manager 가 static event 로 우회 구독** 하고 view 는 ILocaleAware 미구현하는 패턴 금지. 헌법 §2-0-1 의 "사용자 노출 UI 컴포넌트는 ILocaleAware 의무" 룰을 직접 위반.

**금지 패턴**:
```csharp
// ❌ Manager-level 우회 (Encounter 사고 사례)
public class XManager : Singleton<XManager>
{
    protected override void Init()
    {
        LocalizationDispatcher.LocaleApplied += OnLocaleApplied;  // static event 우회
    }
    private void OnLocaleApplied() { _xView.Render(...); }
}
public class UIXView : MonoBehaviour { /* ILocaleAware 미구현 */ }
```

**필수 패턴** (UIRelicReward / UICampActionButton / UIShopSlot 미러링):
```csharp
// ✓ View-level ILocaleAware
public class UIXView : MonoBehaviour, ILocaleAware
{
    private void OnEnable()  { LocalizationDispatcher.Instance?.RegisterView(this); }
    private void OnDisable() { LocalizationDispatcher.Instance?.UnregisterView(this); }
    public void OnLocaleApplied()
    {
        // 옵션 A: view 자체에 키 보존 + 직접 갱신
        // 옵션 B: 도메인 manager.RefreshLocale() 호출 (ViewModel 재생성 위임)
    }
}
```

**왜 manager-level 우회가 금지인가**:
- **DRY 위반**: 5개 UI 중 4개 view-level / 1개 manager-level → 새 합류자가 1개 예외 흐름 추적해야 함
- **진단 비용 폭발**: manager 가 view 의 활성/inactive/BindView 상태 모두 가드 필요 → race condition 의심 + 다층 진단 로그 필수
- **OCP 위반**: 새 UI 추가 시마다 manager 구독 + 가드 추가 → 확장에 닫혀있음. view-level 은 OnEnable 만 작성.
- **§2-0-1 명시적 우회**: 룰이 "UI 컴포넌트는 ILocaleAware 의무" 명시인데 manager 가 대신 함 = 룰 회피

**자동 검증 grep**:
```
grep -rE "LocalizationDispatcher\.LocaleApplied\s*\+=" Assets/Scripts
```
**결과는 0건이어야 함** — ILocaleAware 인터페이스 외부에서 static event 직접 구독 = 우회 패턴.

(2026-04-29 Encounter L10n 사고: Sonny 가 manager-level subscription 채택 → UIEncounterPanelView 가 ILocaleAware 미구현 → 사용자가 "이 구조가 말이 돼?" 메타 비판. 3차례 진단 로그 추가 후에야 view-level 패턴으로 unification. 헌법 §0 메타 원칙 직접 위반 — Sonny 가 검증된 패턴 무시 + 추측 기반 패턴 도입)

**Subclass 확장 시**: 부모 `OnLocaleApplied` 를 `virtual` + 자식 `override` + `base` 호출. 상세는 [best-practice/locale-aware-subclass-extension.md](../../best-practice/locale-aware-subclass-extension.md).

## 관련 문서

- [engineering-constitution.md](engineering-constitution.md) — §2 SSOT 본문 (본 파일의 모체)
- [best-practice/multilayer-locale-snapshot.md](../../best-practice/multilayer-locale-snapshot.md) — 4-Layer 파이프라인 상세
- [best-practice/locale-aware-subclass-extension.md](../../best-practice/locale-aware-subclass-extension.md) — Subclass 확장 패턴
