---
name: unity-ui-standards
description: Unity UI/UX 표준 참조 지식. Rachael(UI/셰이더)에 사전 로드됩니다. Canvas 설정, TextMeshPro, DOTween 애니메이션, 색상 팔레트 표준을 담고 있습니다.
user-invocable: false
---

# Unity UI/UX 표준

이 스킬은 Unity 게임 UI 개발의 표준 패턴과 설계 가이드를 정의합니다.

---

## 1. Canvas 설정 표준

### Screen Space - Overlay (기본 HUD)
```
Canvas
└── Canvas Scaler
    ├── UI Scale Mode: Scale With Screen Size
    ├── Reference Resolution: 1920 × 1080
    ├── Screen Match Mode: Match Width Or Height
    └── Match: 0.5 (너비/높이 균형)
```

### Screen Space - Camera (3D 효과 UI)
```
Canvas
└── Render Camera: Main Camera
    └── Plane Distance: 100
```

### World Space (인게임 UI — 체력바 등)
```
Canvas
└── Event Camera: Main Camera
    └── 빌보드 처리를 위해 LookAt Camera 스크립트 부착
```

---

## 2. 색상 시스템

```csharp
// UIColors.cs — 전체 UI 공통 색상 정의
public static class UIColors
{
    // 배경
    public static readonly Color BackgroundDark = new Color(0.051f, 0.051f, 0.102f, 1f);   // #0D0D1A
    public static readonly Color BackgroundMid  = new Color(0.102f, 0.102f, 0.180f, 1f);   // #1A1A2E

    // 강조
    public static readonly Color AccentPrimary  = new Color(0.914f, 0.271f, 0.376f, 1f);   // #E94560
    public static readonly Color AccentSecondary= new Color(0.059f, 0.204f, 0.376f, 1f);   // #0F3460

    // 텍스트
    public static readonly Color TextPrimary    = new Color(0.918f, 0.918f, 0.918f, 1f);   // #EAEAEA
    public static readonly Color TextSecondary  = new Color(0.533f, 0.549f, 0.655f, 1f);   // #888CA7

    // 상태
    public static readonly Color Success        = new Color(0f, 0.784f, 0.588f, 1f);        // #00C896
    public static readonly Color Warning        = new Color(1f, 0.702f, 0.278f, 1f);        // #FFB347
    public static readonly Color Danger         = new Color(1f, 0.278f, 0.341f, 1f);        // #FF4757
}
```

---

## 3. TextMeshPro 설정 표준

| 용도 | Font Size | Style | Letter Spacing | Line Spacing |
|-----|-----------|-------|---------------|-------------|
| 대형 제목 | 72 | Bold | -1 | — |
| 제목 | 48 | Bold | -1 | — |
| 부제목 | 28 | SemiBold | 0 | — |
| 본문 | 18 | Regular | 0 | 1.5 |
| 레이블 | 14 | Medium | 2 | — |
| 소형 레이블 | 12 | Regular | 1 | — |

```
권장 폰트: Noto Sans KR (한글 지원)
         또는 Inter (영어 전용)
TextMeshPro 폰트 에셋은 Assets/UI/Fonts/ 에 저장
```

---

## 4. DOTween 애니메이션 표준

### 패널 등장 애니메이션
```csharp
// 패널 페이드인 + 슬라이드업
public static Sequence ShowPanel(CanvasGroup panel, RectTransform rect)
{
    panel.alpha = 0f;
    rect.anchoredPosition = new Vector2(0, -30f);

    return DOTween.Sequence()
        .Append(panel.DOFade(1f, 0.25f).SetEase(Ease.OutQuad))
        .Join(rect.DOAnchorPosY(0f, 0.25f).SetEase(Ease.OutBack));
}

// 패널 페이드아웃
public static Sequence HidePanel(CanvasGroup panel)
{
    return DOTween.Sequence()
        .Append(panel.DOFade(0f, 0.2f).SetEase(Ease.InQuad))
        .OnComplete(() => panel.gameObject.SetActive(false));
}
```

### 버튼 탭 피드백
```csharp
public static void ButtonPunch(Transform button)
{
    button.DOPunchScale(Vector3.one * 0.15f, 0.25f, 8, 0.5f);
}
```

### 체력바 애니메이션
```csharp
// 피격 시 체력바 흔들림
public static void HealthBarShake(RectTransform bar)
{
    bar.DOShakeAnchorPos(0.3f, strength: 5f, vibrato: 10, randomness: 45f);
}

// 체력 감소 트윈
public static void AnimateHealth(Image fillImage, float targetNormalized)
{
    fillImage.DOFillAmount(targetNormalized, 0.4f).SetEase(Ease.OutCubic);
}
```

---

## 5. UI 컴포넌트 스크립트 패턴

```csharp
// 표준 UIPanel 기반 클래스
public abstract class UIPanel : MonoBehaviour
{
    [SerializeField] protected CanvasGroup _canvasGroup;
    [SerializeField] protected RectTransform _rectTransform;

    protected virtual void Awake()
    {
        _canvasGroup ??= GetComponent<CanvasGroup>();
        _rectTransform ??= GetComponent<RectTransform>();
    }

    public virtual void Show()
    {
        gameObject.SetActive(true);
        // 서브클래스에서 애니메이션 오버라이드
    }

    public virtual void Hide()
    {
        // 서브클래스에서 애니메이션 오버라이드
        gameObject.SetActive(false);
    }
}

// UIManager — 화면 전환 관리
public class UIManager : MonoBehaviour
{
    public static UIManager Instance { get; private set; }

    [Header("패널")]
    [SerializeField] private UIPanel _mainMenuPanel;
    [SerializeField] private UIPanel _pauseMenuPanel;
    [SerializeField] private UIPanel _gameOverPanel;
    [SerializeField] private HUDUI _hud;

    public void ShowScreen(UIScreen screen)
    {
        // 모든 패널 숨기고 해당 패널만 표시
        HideAll();
        GetPanel(screen)?.Show();
    }
}
```

---

## 6. 앵커(Anchor) 설정 가이드

| 위치 | Anchor Min | Anchor Max | 용도 |
|-----|-----------|-----------|-----|
| 전체 화면 | (0,0) | (1,1) | 풀스크린 패널 |
| 상단 중앙 | (0.5,1) | (0.5,1) | 상단 HUD |
| 좌측 상단 | (0,1) | (0,1) | 체력바, 스코어 |
| 우측 상단 | (1,1) | (1,1) | 미니맵, 설정 |
| 하단 중앙 | (0.5,0) | (0.5,0) | 액션바, 대화창 |
| 중앙 | (0.5,0.5) | (0.5,0.5) | 팝업, 모달 |

```
규칙: Stretch 앵커(0,0)→(1,1)는 패널에만 사용
      개별 UI 요소는 고정 앵커 포인트 사용
```

---

## 7. 파티클 & VFX 표준

```
효과 타입별 Duration 가이드:
- 히트 스파크: 0.3s, Max Particles: 10
- 폭발: 1.0s, Max Particles: 50
- 수집 아이템 반짝임: 0.5s, Max Particles: 20
- 레벨업: 2.0s, Max Particles: 100
- 발자국 먼지: 루프, Max Particles: 5

Stop Action: Destroy (풀링 미사용 시)
            Disable (풀링 사용 시)
```

---

## 8. 성능 최적화 (UI)

| 문제 | 해결책 |
|-----|--------|
| 과도한 Draw Call | Sprite Atlas 사용, 같은 Canvas에 배치 |
| 잦은 Canvas Rebuild | 움직이는 UI를 별도 Canvas로 분리 |
| Layout Group 성능 | 동적 요소에만 사용, 정적 요소는 수동 배치 |
| 텍스트 잦은 갱신 | 이벤트 기반으로 변경될 때만 갱신 |
| Overdraw | Raycast Target은 클릭 가능한 요소에만 활성화 |

---

## 9. 반응형 UI 체크리스트

```
지원 해상도:
✅ 1920×1080 (16:9, PC 기본)
✅ 2560×1440 (16:9, 고해상도)
✅ 1280×720 (16:9, 저사양)
✅ 1334×750 (16:9, 모바일 iOS)
✅ 2340×1080 (19.5:9, 노치 모바일)

Safe Area 처리:
- 노치/펀치홀 기기: SafeArea Panel로 래핑
- Screen.safeArea를 런타임에 읽어 RectTransform 조정
```
