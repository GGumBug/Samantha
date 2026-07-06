[← README로 돌아가기](../README.md) | [engineering-constitution.md](../.claude/rules/engineering-constitution.md)

# UI Transition Prefab Convention — Prefab은 Start 위치 (SSOT)

UI 슬라이드/페이드/스케일 트랜지션 컴포넌트의 prefab Inspector 위치를 **End(목표)가 아닌 Start(시작) 상태**로 박제하는 컨벤션. 디자이너 직관과 CSS `slide-from-*` 의미론에 정합.

## 두 컨벤션 비교

| 항목 | prefab=End (예전) | prefab=Start (권장) |
|------|-------------------|---------------------|
| Inspector 시각 | 화면 안 (보여질 위치) | 화면 밖 (숨겨진 위치) |
| Show 흐름 | Off-screen 으로 강제 이동 → 다시 onscreen 으로 tween | 그대로 onscreen 으로 tween (1단계) |
| Hide 흐름 | Onscreen → off-screen tween | Onscreen → 원래 prefab 위치 tween |
| `_targetAnchoredPos` 캐시 | End 위치 = prefab 위치 (혼동) | End 위치 = `Vector2.zero` (명시) |
| `slide-from-left` 의미 | "왼쪽 으로부터 들어오기" | "왼쪽 에서 시작" (CSS 일치) |
| 디자이너 직관 | "Inspector 에 보이는 위치 = 보여질 위치" | "Inspector 에 보이는 위치 = 숨겨진 시작 위치" |

## 권장 컨벤션 — Prefab = Start

```csharp
// UIPanelSlider 슈도
[SerializeField] private SlideDirection _slideFrom = SlideDirection.Bottom;
[SerializeField] private float _slideDistance = 1080f;

private Vector2 _targetAnchoredPos = Vector2.zero;  // End = 원점
private Vector2 _startAnchoredPos;                  // Awake 에서 prefab 위치 캐시

private void Awake()
{
    _startAnchoredPos = _rectTransform.anchoredPosition;  // prefab 위치 = Start
}

public async UniTask ShowAsync(CancellationToken token)
{
    _rectTransform.anchoredPosition = _startAnchoredPos;
    await _rectTransform.DOAnchorPos(_targetAnchoredPos, _duration).ToUniTask(cancellationToken: token);
}

public async UniTask HideAsync(CancellationToken token)
{
    await _rectTransform.DOAnchorPos(_startAnchoredPos, _duration).ToUniTask(cancellationToken: token);
}
```

## 런타임 SetSlideFrom 변경 시 캐시 동작

```csharp
public void SetSlideFrom(SlideDirection from, float distance)
{
    _slideFrom = from;
    _slideDistance = distance;
    _startAnchoredPos = ComputeStartPos(from, distance);  // 재계산
    // _targetAnchoredPos 는 항상 Vector2.zero — 변경 불필요
}
```

핵심: **End 가 항상 0** 이라 `SetSlideFrom` 호출 시 Start 만 재계산. End=prefab 컨벤션이면 Inspector 위치를 별도로 잡아둬야 하고, 동적 방향 변경 시 prefab 위치 vs 동적 위치 충돌 발생.

## CSS slide-from-* 컨벤션과의 정합

```css
.slide-from-left { transform: translateX(-100%); }  /* 시작 위치 */
.slide-from-left.active { transform: translateX(0); }  /* 끝 위치 = 원점 */
```

웹 프론트 디자이너는 `slide-from-left` = "왼쪽 에서 시작" 으로 학습됨. Unity prefab 도 같은 멘탈 모델로 정렬하면 Inspector 만 봐도 어디서 들어오는지 즉시 파악.

## 일반화 — Fade / Scale 트랜지션

| 컴포넌트 | prefab=Start 의미 |
|----------|-------------------|
| UIPanelFader | `CanvasGroup.alpha = 0` (invisible) → Show 시 1 |
| UIPanelScaler | `localScale = Vector3.zero` → Show 시 one |
| UIPanelSlider | off-screen 위치 → Show 시 원점 |
| UIPanelTransition (composite) | 모든 sub-transition Start 상태 |

**공통 룰**: prefab Inspector 시각 = 트랜지션 진입 전 상태. Show 호출 시 한 방향으로 tween, Hide 는 역방향.

## 안티패턴 — prefab=End 의 함정

- **사전 비활성 시점 깜빡임**: Show 직전 off-screen 으로 강제 이동 후 다시 onscreen tween → 1프레임 깜빡임 가능
- **에디터 시각 검증 불가**: Inspector 에서 "잘 보임" 으로 통과해도 실제 진입 애니메이션이 다른 방향에서 시작
- **동적 SetSlideFrom 충돌**: prefab 위치가 End 인데 런타임에 다른 방향 요청 시 prefab 위치를 무시해야 함 → Inspector 가 SSOT 가 아님

## 본 세션 박제 근거

- `4289695a` UIPanelSlider — SSOT 컨벤션 뒤집기 (prefab=Start), SetSlideFrom/SlideDistance API 추가
- `4991a5a9` UIMapView.prefab — Panel_Legend anchoredPosition (0,13)→(840,13), UIPanelSlider 새 컨벤션 정합
- `8a701f17` UITutorialGuidePanel.prefab — UIPanelSlider 부착, Panel_TutorialGuide 사전 비활성

## 관련 문서

- [ui-visibility-two-layer-srp.md](ui-visibility-two-layer-srp.md) — UI 가시성 SSOT 2-layer 분리
- [multi-axis-fast-path-guard.md](multi-axis-fast-path-guard.md) — same-side fast path 가드
- [.claude/rules/engineering-constitution.md §2 SSOT](../.claude/rules/engineering-constitution.md)
