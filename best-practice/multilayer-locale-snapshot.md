[← README로 돌아가기](../README.md)

# 다중 Layer Caller-Driven Snapshot 박멸 패턴

L10n 마이그레이션 시 **데이터 흐름의 각 layer 마다 string snapshot 안티패턴**(헌법 §2-0-1)이 잠복할 수 있다. 한 layer만 fix하면 다음 layer의 snapshot이 안티패턴을 보존하므로, 4-layer 파이프라인 전체에 키+lazy resolve 패턴을 일관 적용해야 한다.

## 데이터 흐름 4-Layer 책임 분리

```
[Layer 1 SoT]            [Layer 2 Carrier]         [Layer 3 Resolver]        [Layer 4 View]
SkillViewUI              TooltipsTarget            UITooltipList             TooltipView
키 + spec + caster   →   키 + spec + caster    →   키 + value (eval)    →   키 + value 보존
                                                                              + ApplyLabels(매번)
                                                                              + LocaleApplied 구독
```

**원칙**: 각 layer는 **자기 책임만** 보유. 표시 직전 (Layer 4) **lazy resolve** (`L10n.T(key)` + `Replace("{value}", value.ToString())`).

## Layer별 책임 매트릭스

| Layer | 보유 데이터 | 금지 |
|-------|-----------|------|
| 1 SoT | string key + numeric spec + caster ref | `L10n.T()` 결과 string 박제 |
| 2 Carrier | key + spec + caster (전파만) | spec 즉시 evaluate 후 string화 |
| 3 Resolver | key + value (현재 caster 기반 evaluate) | L10n.T() 호출 (아직) |
| 4 View | key + value 보존 + ApplyLabels (`OnLocaleApplied` 구독) | 한 번 set 후 재계산 안 함 |

## {value} placeholder 안전 치환 패턴

numeric value를 시트 텍스트 (`"{value} damage"`) 에 치환할 때, **value는 numeric 보존 + L10n.T 후 Replace** 패턴이 언어 토글 안전:

```csharp
// View Layer (TooltipView 등)
private string _bodyKey;
private float _value;

public void Bind(string key, float value)
{
    _bodyKey = key;
    _value = value;
    ApplyLabels();
}

public void OnLocaleApplied() => ApplyLabels();   // 활성 중 언어 토글 자동 갱신

private void ApplyLabels()
{
    if (string.IsNullOrEmpty(_bodyKey)) return;
    var template = L10n.T(_bodyKey);                              // 매번 lazy resolve
    _bodyText.text = template.Replace("{value}", _value.ToString("0.##"));
}
```

**금기**:

```csharp
// ❌ Layer 2/3에서 즉시 string화
_bodyText.text = L10n.T(key).Replace("{value}", value.ToString());   // OnLocaleApplied 시 갱신 불가
```

## Layer 일관성 강제 — 위임 시작 + 종료 grep

위임 작업 시작 시점과 종료 시점에 다음 grep으로 **모든 layer가 키 보존 패턴**을 따르는지 확인:

```bash
# Pattern A — 데이터 클래스에 string 텍스트 필드 (헌법 §2-0-1 Pattern A)
grep -rE "class.*(VisualData|ViewData|RowData|Model|Snapshot|TooltipsTarget).*\{" -A 30 \
  | grep -E "public (readonly )?string (Name|Description|Title|Label|DisplayName|Body)"

# Pattern B — L10n.T 결과를 view-internal 변수에 박는 즉시 평가
grep -rE "(name|desc|description|title|label|body)\s*=\s*L10n\.(T|Format)\("

# Pattern C — view에 ILocaleAware 누락 (사용자 노출 텍스트 갱신 view)
grep -L "ILocaleAware" Assets/Scripts/UI/Tooltip/*.cs   # 0건이어야 함
```

**한 layer라도 위반 발견 시** layer 일관성 깨짐 — 전 layer sweep 의무.

## 사고 사례 — Hwaseo Effect Tooltip {value} (2026-04-30)

**증상**: 카드 effect tooltip이 `{value}` placeholder를 1회만 evaluate하고 활성 중 언어 토글 시 잔재.

**해결**:
- `SkillViewUI` (Layer 1): SoT 키 + spec + caster ref 보존
- `TooltipsTarget` (Layer 2): specs + caster를 carrier로 전파만
- `UITooltipList` (Layer 3): `currentAP + caster.GetCalculatedValue()`로 numeric value 평가
- `TooltipView` (Layer 4): 키 + value 보존, `OnLocaleApplied` → `ApplyLabels()` 매번 L10n.T + Replace

5 파일 변경(SkillViewUI / TooltipsTarget / UITooltipList / TooltipView / SkillViewUI 호출처) 모두 키+spec+caster 보존 layer 일관성 유지 → 활성 중 EN↔KO 토글 시 자동 재계산.

## 시니어 회고

L10n 마이그레이션은 **단일 파일 수정**이 아니라 **데이터 흐름 횡단 일관성 작업**. 한 layer fix 후 "끝났다" 판정 금지 — 다음 layer로 흐른 snapshot이 잔재할 수 있다. 위임 시작 시 4-layer 매트릭스를 사전 정의하고 종료 시 grep 검증.

(2026-04-29 Shop 유물 + 2026-04-30 Effect tooltip 누적 사례 — 본 패턴이 박제되지 않으면 새 도메인 마이그레이션마다 같은 사고 재발)

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §2-0-1 데이터 흐름 String Snapshot 절대 금지, §2-0-2 View-Level ILocaleAware 강제
- [evidence-based-debugging.md](evidence-based-debugging.md) — 데이터 layer 격리 진단
