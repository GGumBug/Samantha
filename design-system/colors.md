[← DESIGN.md로 돌아가기](DESIGN.md)

# Colors — 색상 토큰

## Brand & Accent

라벤더 블루는 **희소 자원**입니다. 브랜드 마크·1차 CTA·포커스 링·링크 강조 외에 사용 금지.

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{colors.primary}` | `#5e6ad2` | 라벤더 블루 — 1차 CTA, 브랜드 마크, 링크 강조 |
| `{colors.primary-hover}` | `#828fff` | 라벤더 호버 — primary CTA hover 상태 |
| `{colors.primary-focus}` | `#5e69d1` | 포커스 링 틴트 — 인풋·버튼 포커스 |
| `{colors.brand-secure}` | `#7a7fad` | "Linear Security" 류 보조 라벤더-그레이 |

## Surface — 4단계 ladder

다크 캔버스 위 4단계 surface로 위계 표현. **그림자 사용 금지**, 항상 surface 단계 + hairline border.

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{colors.canvas}` | `#010102` | 페이지 기본 배경 — 거의 순수 검정 + 미세한 푸른 틴트 |
| `{colors.surface-1}` | charcoal-1 | 캔버스 위 1단 — 기본 카드, 제품 스크린샷 패널 |
| `{colors.surface-2}` | charcoal-2 | 캔버스 위 2단 — 추천 가격 카드, 호버된 카드 |
| `{colors.surface-3}` | charcoal-3 | 캔버스 위 3단 — 서브 내비, 드롭다운 |
| `{colors.surface-4}` | charcoal-4 | 캔버스 위 4단 — 최상단 lift, bg-level-3 |
| `{colors.hairline}` | `#23252a` | 1px 테두리 (카드, 디바이더) |
| `{colors.hairline-strong}` | strong | 강한 1px 테두리 — 인풋 포커스 링 |
| `{colors.hairline-tertiary}` | tertiary | 중첩 surface 테두리 |

## Inverse Surface (역방향)

소수 섹션 오프너에서 흰색 inverse pill CTA를 사용할 때만.

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{colors.inverse-canvas}` | `#ffffff` | inverse pill CTA 표면 |
| `{colors.inverse-surface-1}` | off-white | inverse 위 1단 |
| `{colors.inverse-surface-2}` | off-white-2 | inverse 위 2단 |
| `{colors.inverse-ink}` | dark | inverse 위 텍스트 |

## Text — Ink ladder

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{colors.ink}` | `#f7f8f8` | 모든 헤드라인·강조 본문 — 라이트 그레이 |
| `{colors.ink-muted}` | `#d0d6e0` | 보조 본문 — 히어로 패널 메타 |
| `{colors.ink-subtle}` | `#8a8f98` | 3차 본문 — 미선택 가격 탭, 푸터 컬럼 |
| `{colors.ink-tertiary}` | `#62666d` | 4차 본문 — 비활성, 각주 |

## Semantic

마케팅에서 채도 색은 단 하나만 허용 — **녹색 status pill**. 데이터 비즈 컴포넌트(07-design-tokens)에 한해 warning/danger 2색 추가 허용.

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{colors.semantic-success}` | `#27a644` | status pill, 성공 인디케이터, 게이지 0-30, delta 양수 |
| `{colors.semantic-warning}` | `#f0a04b` | 게이지 70-90, trigger 경계 (데이터 시각화 전용) |
| `{colors.semantic-danger}` | `#d4564b` | 게이지 90+, delta 음수, trigger 발동 (데이터 시각화 전용) |
| `{colors.semantic-overlay}` | `#000000` | 모달 오버레이 스크림 (순수 검정) |

## Data Visualization (07-design-tokens 전용)

데이터 비즈 컴포넌트(`heatmap-cell` 등)에서만 사용. **마케팅 CTA·강조에 사용 금지**.

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{colors.heatmap-positive-base}` | `#2a4a3a` | 히트맵 양수 셀 base (~+20%까지 `#3a6a4a`로 그라데이션) |
| `{colors.heatmap-negative-base}` | `#3a2a2a` | 히트맵 음수 셀 base (~-10%까지 `#5a3a3a`로 그라데이션) |

**라벤더 보존 원칙 유지**: 위 4색(warning/danger/heatmap-pos/neg)은 데이터 시각화 전용. 라벤더(`{colors.primary}`)는 여전히 브랜드·1차 CTA·포커스·링크 강조 4가지 외 사용 금지.

## CSS 변수 매핑 (구현 가이드)

`src/app/globals.css`에 다음 형태로 정의 권장:

```css
:root {
  /* Brand */
  --color-primary: #5e6ad2;
  --color-primary-hover: #828fff;
  --color-primary-focus: #5e69d1;
  --color-brand-secure: #7a7fad;
  
  /* Surface */
  --color-canvas: #010102;
  --color-hairline: #23252a;
  
  /* Text */
  --color-ink: #f7f8f8;
  --color-ink-muted: #d0d6e0;
  --color-ink-subtle: #8a8f98;
  --color-ink-tertiary: #62666d;
  
  /* Semantic */
  --color-success: #27a644;
  --color-warning: #f0a04b;
  --color-danger: #d4564b;

  /* Data Visualization */
  --color-heatmap-pos-base: #2a4a3a;
  --color-heatmap-neg-base: #3a2a2a;
}
```

Tailwind v4의 `@theme`로 노출 시:

```css
@theme {
  --color-canvas: #010102;
  --color-primary: #5e6ad2;
  /* ... */
}
```

이렇게 하면 `bg-canvas`, `text-ink`, `border-hairline` 같은 의미적 유틸이 생성됩니다 — `bg-[#010102]` 같은 임의 색 사용 금지.

## 금지 사항

- ❌ `#000000` 순수 검정을 캔버스로 사용 — 항상 `#010102`(미세 푸른 틴트)
- ❌ 라벤더를 섹션 배경·카드 fill로 사용 — CTA·포커스에만
- ❌ 두 번째 채도 색 도입 (주황·분홍·녹색 등 마케팅에)
- ❌ 분위기 그라디언트·스포트라이트 카드
