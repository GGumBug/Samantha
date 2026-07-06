[← README로 돌아가기](../README.md)

# ILocaleAware Subclass Extension 패턴 (LSP 정합)

`ILocaleAware` 구현체를 subclass가 상속해 **추가 갱신 책임**을 더해야 할 때, 부모의 `OnLocaleApplied` 를 **virtual** 로 선언하고 자식이 `override` + `base.OnLocaleApplied()` 호출하는 것이 LSP 정합 유일 경로.

헌법 §2-0-2 (View-Level ILocaleAware 강제) 의 "Manager/Static-Event 우회 금지" 룰을 subclass 컨텍스트에서도 보존하기 위한 보강 패턴.

## 필수 패턴

```csharp
// 부모 — OnLocaleApplied를 virtual로
public class SkillViewUI : MonoBehaviour, ILocaleAware
{
    [SerializeField] private TextMeshProUGUI _txtName;
    [SerializeField] private TextMeshProUGUI _txtDesc;
    private string _nameKey;
    private string _descKey;

    private void OnEnable()  => LocalizationDispatcher.Instance?.RegisterView(this);
    private void OnDisable() => LocalizationDispatcher.Instance?.UnregisterView(this);

    public virtual void OnLocaleApplied() => ApplySkillLabels();

    protected void ApplySkillLabels()
    {
        if (!string.IsNullOrEmpty(_nameKey)) _txtName.text = L10n.T(_nameKey);
        if (!string.IsNullOrEmpty(_descKey)) _txtDesc.text = L10n.T(_descKey);
    }
}

// 자식 — base.OnLocaleApplied() 호출 + 추가 책임
public class CardView : SkillViewUI
{
    [SerializeField] private TextMeshProUGUI _txtOwnerName;
    private string _ownerNameKey;

    public override void OnLocaleApplied()
    {
        base.OnLocaleApplied();          // 부모 책임 보존 (skill name/desc 갱신)
        ApplyOwnerNameTag();             // 자식 추가 책임 (owner nameTag)
    }

    private void ApplyOwnerNameTag()
    {
        if (!string.IsNullOrEmpty(_ownerNameKey))
            _txtOwnerName.text = L10n.T(_ownerNameKey);
    }
}
```

## 안티패턴

### 부모 OnLocaleApplied를 non-virtual로 두고 자식이 manager-level 우회

```csharp
// ❌ 부모 변경 회피하고 자식이 manager 구독
public class CardView : SkillViewUI
{
    private void OnEnable()
    {
        LocalizationDispatcher.LocaleApplied += OnOwnerNameLocale;  // §2-0-2 위반
    }
    private void OnOwnerNameLocale() { /* owner 갱신 */ }
}
```

위반 사항:
- **§2-0-2 직접 위반**: ILocaleAware 외부에서 static event 직접 구독
- **DRY 위반**: 부모는 view-level / 자식은 manager-level → 1개 예외 흐름
- **OCP 역행**: 새 자식마다 manager 구독 추가, 가드 코드 분기

### 부모 메서드 시그니처 그대로 두고 자식이 새 public 메서드 추가

```csharp
// ❌ OnLocaleApplied 미override + 별도 RefreshOwner public 호출 강제
public class CardView : SkillViewUI
{
    public void RefreshOwner() { /* ... */ }   // caller가 OnLocaleApplied + RefreshOwner 둘 다 호출해야
}
```

위반 사항: caller가 자식 타입에 따라 추가 호출이 필요 → LSP 위반 (자식이 부모 계약을 깸).

## 위임 시작 시 grep 검증

ILocaleAware 구현체 subclass 작업 위임 시 프롬프트에 다음 grep을 명시:

```bash
# Pattern A — virtual 누락된 OnLocaleApplied (subclass 확장 차단됨)
grep -rE "public void OnLocaleApplied\(\)" Assets/Scripts | grep -v virtual | grep -v override

# Pattern B — subclass에서 manager-level static event 우회 (§2-0-2 위반)
grep -rE "LocalizationDispatcher\.LocaleApplied\s*\+=" Assets/Scripts
```

Pattern A 발견 + 자식 클래스가 추가 갱신 책임 필요 → 부모 메서드를 virtual로 변경.
Pattern B 발견 → §2-0-2 직접 위반, view-level override로 unification.

## 시니어 회고

(2026-04-30 CardView nameTag 확장 사례) 처음 SkillViewUI.OnLocaleApplied가 non-virtual이라 CardView가 override 불가 → virtual로 변경 + base 호출 + ownerName 추가 갱신 패턴으로 unification. Manager-level 우회 안티패턴을 사전 회피.

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §2-0-2 View-Level ILocaleAware 강제
- [multilayer-locale-snapshot.md](multilayer-locale-snapshot.md) — 다중 layer L10n 일관성
