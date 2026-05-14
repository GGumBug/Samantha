[← README로 돌아가기](../README.md) | [engineering-constitution.md](../.claude/rules/engineering-constitution.md)

# UI Visibility — Two-Layer SSOT 분리 (SRP)

사전 생성(pre-instantiated) UI 패턴에서 가시성(visibility) 의 SSOT 가 **2개 layer 로 분리**됨을 인지하지 못하면 panel root SetActive 를 잘못 만지는 사고 발생. 두 layer 의 책임을 SRP 로 박제.

## 두 Layer 구조

```
┌─────────────────────────────────────────────────┐
│ Layer 1 — Panel Root GameObject                 │
│   • UIManager 인스턴스 라이프사이클 SSOT        │
│   • Awake 에서 active = true (사전 생성 시점)   │
│   • 런타임 코드는 절대 SetActive 안 건드림      │
│   • OpenUIAsync 가 GetUIAsync 로 인스턴스 가져옴│
└─────────────────────────────────────────────────┘
              │ child of
              ▼
┌─────────────────────────────────────────────────┐
│ Layer 2 — Content Child (Panel_*)               │
│   • 화면 표시 SSOT                              │
│   • UIPanelSlider / UIPanelFader 부착           │
│   • Show/HideAsync 가 SetActive + tween 제어    │
│   • prefab 에 active = false (사전 비활성)      │
└─────────────────────────────────────────────────┘
```

## 책임 매트릭스

| 책임 | Layer 1 (panel root) | Layer 2 (content child) |
|------|----------------------|--------------------------|
| 인스턴스 생성 | UIManager.Awake 사전 생성 | Layer 1 의 자식으로 prefab 에 박제 |
| SetActive 권한 | **UIManager 만** (또는 항상 true) | UIPanelTransition Show/HideAsync |
| 사용자 가시성 | 인스턴스 존재 여부 | 화면에 실제 보이는지 |
| 트랜지션 대상 | 아님 (anchor stretch 고정) | 슬라이드/페이드 anchoredPosition/alpha |
| ILocaleAware | 인스턴스 라이프타임 동안 구독 | 표시 중일 때만 갱신 |

## 안티패턴 사례

### 안티패턴 A — Panel Root SetActive 직접 토글

```csharp
// ❌ 잘못된 layer 에 SSOT 가정
public async UniTaskVoid OnTutorialStart()
{
    UITutorialGuidePanel panel = await UIManager.Instance.GetUIAsync<UITutorialGuidePanel>();
    panel.gameObject.SetActive(true);   // Layer 1 활성화 — 사전 생성된 인스턴스에 불필요
    panel.ShowStep(stepData);
}
```

**증상**: panel root 가 한 번 켜진 후 영영 SetActive(false) 안 됨 → 다른 UI 와 z-order 충돌 / 영역 차단. Hide 시 Layer 2 만 비활성화되고 Layer 1 은 active 상태 유지.

### 안티패턴 B — OpenUIAsync 우회

```csharp
// ❌ Open/Close 컨벤션 우회
panel.gameObject.SetActive(false);
panel.gameObject.SetActive(true);
panel.ShowStep(stepData);
```

UIManager 의 OpenUIAsync/CloseUIAsync 가 transition 자동 감지(UIPanelTransition / UIPanelFader 등) + Open 큐 + escape 키 처리를 통합 SSOT 로 제공. 우회 시 모든 부수효과 누락.

### 안티패턴 C — 사전 비활성 prefab 의 OnEnable 의존

```csharp
public class UITutorialGuidePanel : MonoBehaviour
{
    private void OnEnable()
    {
        _slider.ShowAsync(_cts.Token).Forget();  // Layer 2 활성화 시점에 발동
    }
}
```

prefab 에서 Panel_TutorialGuide 가 active=false 면 OnEnable 이 첫 Show 까지 호출 안 됨 — 의도일 수 있으나, panel root active 가 true 라 GetUIAsync 결과는 사전 인스턴스화된 인스턴스라는 점을 기억.

## 권장 패턴

```csharp
// ✓ UIManager 컨벤션 준수
public async UniTaskVoid OnTutorialStart()
{
    var panel = await UIManager.Instance.OpenUIAsync<UITutorialGuidePanel>();
    // OpenUIAsync 내부에서
    //   1. GetUIAsync 로 인스턴스 (Layer 1) 가져옴 (panel root active=true 유지)
    //   2. UIPanelTransition 자동 감지 → ShowAsync (Layer 2 활성화 + tween)
    //   3. Open 큐 등록 + ESC 핸들러 wire
    panel.ShowStep(stepData);
}
```

## 자동 검증 grep

```
# 사전 생성 UI 의 panel root SetActive 직접 호출 (의심)
grep -rE "panel\.gameObject\.SetActive|_panel\.gameObject\.SetActive" Assets/Scripts
```

결과 발견 시 **GetUIAsync / OpenUIAsync 컨벤션 우회 여부** 검토. 정당화 가능한 경우만 허용 (예: panel pooling 의 명시적 비활성화).

## 사용자 시니어 통찰 박제

> "UITutorialGuidePanel SetActive 직접 만질 필요 없어. panel root 는 UIManager 가 관리하는 인스턴스 SSOT, 화면 표시 SSOT 는 Panel_TutorialGuide 자식의 UIPanelSlider 한테 있어."

— 본 세션 사용자 회고, 2026-05-14. 두 layer 가 같은 GameObject 계층이라 한 layer 로 착각하는 사고가 반복됨 → SRP 로 박제.

## 본 세션 박제 근거

- `8a701f17` UITutorialGuidePanel.prefab — UIPanelSlider 부착, panel root anchor stretch, Panel_TutorialGuide 사전 비활성
- `23e0f88e` UITutorialGuidePanel — UIPanelSlider 위임 + same-side fast path
- `547738f0` TutorialUIManagerViewProvider — OpenUIAsync 컨벤션 주석 보강 (panel root 활성화 책임 분리)

## 관련 문서

- [ui-transition-prefab-convention.md](ui-transition-prefab-convention.md) — prefab=Start 컨벤션
- [multi-axis-fast-path-guard.md](multi-axis-fast-path-guard.md) — Layer 2 가시성 transition 가드
- [.claude/rules/engineering-constitution.md §1 SOLID SRP](../.claude/rules/engineering-constitution.md)
