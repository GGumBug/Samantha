[← DESIGN.md로 돌아가기](DESIGN.md)

# Components — 컴포넌트 명세

각 컴포넌트는 토큰만 참조해야 합니다 — 임의 색상/크기 사용 금지.

## Buttons

### `button-primary` — 라벤더 CTA

모든 페이지의 기본 1차 CTA.

| 속성 | 값 |
|------|-----|
| Background | `{colors.primary}` |
| Text | `{colors.on-primary}` (흰색) |
| Type | `{typography.button}` 14px / 500 |
| Padding | 8px · 14px |
| Radius | `{rounded.md}` 8px |
| Hover | background → `{colors.primary-hover}` |
| Pressed | background → `{colors.primary-focus}` |

### `button-secondary` — 차콜 보조 CTA

"Sign in", "Read changelog" 같은 2차 액션.

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Text | `{colors.ink}` |
| Type | `{typography.button}` |
| Padding | 8px · 14px |
| Radius | `{rounded.md}` 8px |
| Border | 1px `{colors.hairline}` |

### `button-tertiary` — 평문 텍스트 버튼

| 속성 | 값 |
|------|-----|
| Background | `{colors.canvas}` (투명) |
| Text | `{colors.ink}` |
| Padding | 8px · 14px |
| Radius | `{rounded.md}` 8px |

### `button-inverse` — 흰색 inverse CTA

소수 섹션 오프너에서만.

| 속성 | 값 |
|------|-----|
| Background | `{colors.inverse-canvas}` |
| Text | `{colors.inverse-ink}` |
| Padding | 8px · 14px |
| Radius | `{rounded.md}` 8px |

## Pricing Tabs

### `pricing-tab-default` + `pricing-tab-selected`

`/pricing` 페이지의 pill toggle.

| 상태 | Background | Text | Padding | Radius |
|------|-----------|------|---------|--------|
| default | `{colors.canvas}` | `{colors.ink-subtle}` | 6px · 14px | `{rounded.pill}` |
| selected | `{colors.surface-2}` | `{colors.ink}` | 6px · 14px | `{rounded.pill}` |

선택 = surface lift. 색 변화가 아니라 표면 단계 변화로 표현.

## Cards & Containers

### `pricing-card` — 가격 티어

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Text | `{colors.ink}` |
| Type | `{typography.body}` |
| Padding | 24px |
| Radius | `{rounded.lg}` 12px |
| Border | 1px `{colors.hairline}` |

### `pricing-card-featured` — 추천 티어

`pricing-card`와 동일하되 background → `{colors.surface-2}`. **lavender 강조 금지** — surface lift로 강조.

### `feature-card` — 일반 피처 하이라이트

`pricing-card`와 동일 스펙. 일반 피처 그리드 셀.

### `product-screenshot-card` — 주인공 카드

높은 충실도의 Linear 앱 UI 스크린샷을 감싸는 액자.

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Padding | 24px |
| Radius | `{rounded.xl}` **16px** (다른 카드와 다름) |

스크린샷 자체는 aspect ratio 보존, crop 금지.

### `testimonial-card` — 고객 인용 카드

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Text | `{colors.ink}` |
| Type | `{typography.body-lg}` |
| Padding | 32px |
| Radius | `{rounded.lg}` 12px |
| Avatar | `{rounded.full}` 32~40px |

### `customer-logo-tile` — 고객사 로고 마키

| 속성 | 값 |
|------|-----|
| Background | `{colors.canvas}` (자체 배경 없음) |
| Text | `{colors.ink-subtle}` |
| Type | `{typography.caption}` |
| Padding | 16px |
| Radius | `{rounded.xs}` 4px |
| Logo height | ~24px |

### `cta-banner` — 페이지 하단 CTA 패널

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Type | `{typography.headline}` |
| Padding | 48px |
| Radius | `{rounded.lg}` 12px |

## Inputs & Forms

### `text-input` + `text-input-focused`

`/contact/sales`, 가입 오버레이의 폼 필드.

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Text | `{colors.ink}` |
| Type | `{typography.body}` |
| Padding | 8px · 12px |
| Radius | `{rounded.md}` 8px |
| Focus | 2px `{colors.primary-focus}` outline @ 50% opacity |

포커스 시 surface는 그대로, 외곽선만 추가.

## Status & Build Page

### `changelog-row` — `/build` 행

| 속성 | 값 |
|------|-----|
| Background | `{colors.canvas}` |
| Type | `{typography.body}` |
| Padding | 24px (vertical) · 0 |
| Border | 하단 1px `{colors.hairline}` |

### `status-badge` — 작은 status pill

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-2}` |
| Text | `{colors.ink-muted}` |
| Type | `{typography.caption}` |
| Padding | 2px · 8px |
| Radius | `{rounded.pill}` |

성공 상태는 background → `{colors.semantic-success}` 사용 가능 (마케팅 유일 채도 색).

## Navigation

### `top-nav` — 스티키 다크 바

레이아웃: 좌측 wordmark · 중앙 nav 링크 · 우측 (`button-secondary` "Sign in" + `button-primary` "Get started") 페어.

| 속성 | 값 |
|------|-----|
| Background | `{colors.canvas}` |
| Text | `{colors.ink}` |
| Type | `{typography.body-sm}` 14px |
| Height | 56px |

**로고 자리**: 현재 placeholder (24px 높이 빈 박스). 회사 로고 결정 후 교체.

## Footer

### `footer` — 빽빽한 링크 그리드

좌측 wordmark + 다중 컬럼 링크.

| 속성 | 값 |
|------|-----|
| Background | `{colors.canvas}` |
| Text | `{colors.ink-subtle}` |
| Type | `{typography.caption}` |
| Padding | 64px · 32px |
