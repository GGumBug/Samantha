[← DESIGN.md로 돌아가기](DESIGN.md)

# Components — Data Viz (07-design-tokens)

데이터 대시보드 전용 7종 토큰. 마케팅 컴포넌트는 [components.md](components.md) 참고.

**핵심 원칙**:
- **라벤더 희소** — 7종 어디에도 라벤더 fill 사용 금지(브랜드·1차 CTA·포커스·링크 강조 4가지 외 0건). 차트 다중 시리즈에는 라벤더 명도 시퀀스 허용.
- **임의 hex 금지** — 모든 색상은 `var(--color-*)` 토큰 변수 경유.
- **다크 모드 단일** — `dark:` variant 없음.
- **Pretendard 적용** — 모든 텍스트는 `font-display`. 숫자 셀은 `font-feature-settings: 'tnum'`.

명세 원본 SSOT → [../implementation/endurance/foundation/07-design-tokens.md](../implementation/endurance/foundation/07-design-tokens.md).

## 1. `data-table` — 정렬·필터·페이지네이션 표

기반: TanStack Table v8 (헤드리스). 마크업은 디자인 시스템 토큰 적용한 자체 wrapper.

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Header text | `{typography.eyebrow}` (`{colors.ink-subtle}`) |
| Body text | `{typography.body-sm}` (`{colors.ink}`) |
| Row hover | `{colors.surface-2}` |
| Selected row | 좌측 2px `{colors.primary-focus}` border |
| Cell border | hairline-tertiary 1px bottom만 (cell 좌우 border 금지) |
| Cell padding | 12px · 16px |
| Numeric cell | `font-feature-settings: 'tnum'` (자릿수 정렬) |
| Sort indicator | 우측 8px 화살표 (`{colors.ink-subtle}` → 활성 `{colors.primary}`) |

접근성: 헤더 정렬 키보드(Enter/Space) 활성, `aria-sort` 속성.

## 2. `chart-container` — 차트 wrapper

| 속성 | 값 |
|------|-----|
| Background | `{colors.canvas}` (surface-1 위에 캔버스로 끊어 시각 분리) |
| Padding | 16px (mobile) · 24px (desktop) |
| Radius | `{rounded.lg}` |
| Title | `{typography.eyebrow}` 위쪽 |
| Tooltip | surface-2 + hairline-strong 1px |
| Grid line | `{colors.hairline-tertiary}` 1px |
| Axis label | `{typography.caption}` (`{colors.ink-subtle}`) |
| 라인 색 | `{colors.primary}` 단일 / 다중 시리즈는 라벤더 명도 시퀀스 |

## 3. `gauge-meter` — 0~100 조기 경보 게이지

반원형 SVG 게이지 (Recharts 등 외부 라이브러리 의존 금지, ~80줄 자체 구현).

색 구간:
- `0~30`: `{colors.semantic-success}` (#27a644) — 안전
- `30~70`: `{colors.ink-muted}` — 중립
- `70~90`: `{colors.semantic-warning}` (#f0a04b) — 경계
- `90~100`: `{colors.semantic-danger}` (#d4564b) — 경고

크기 옵션:
- `sm` 80×40px (대시보드 사이드)
- `md` 160×80px (히어로)
- `lg` 240×120px (상세 페이지)

접근성: `role="meter"`, `aria-valuenow`, `aria-valuemin=0`, `aria-valuemax=100` 필수.

## 4. `heatmap-cell` — 섹터 수익률 히트맵 셀

| 속성 | 값 |
|------|-----|
| 음수(-10%~0%) | `{colors.heatmap-negative-base}` (#3a2a2a) ~ `#5a3a3a` 그라데이션 |
| 중립(0% 근처) | `{colors.surface-2}` |
| 양수(0~+20%) | `{colors.heatmap-positive-base}` (#2a4a3a) ~ `#3a6a4a` 그라데이션 |
| Text | `{colors.ink}` 또는 `{colors.ink-muted}` (대비 자동) |
| Border | 1px `{colors.hairline-tertiary}` |
| Padding | 12px |

라벤더 사용 안 함 — 라벤더는 브랜드·CTA 전용(헌법 §1).

## 5. `metric-card` — 단일 거시 지표 카드

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` + 1px `{colors.hairline}` |
| Padding | 20px |
| Radius | `{rounded.lg}` |
| Label | `{typography.eyebrow}` (`{colors.ink-subtle}`) |
| Value | `{typography.display-md}` (40px / 600) |
| Delta | 14px / 500, 양수 `{colors.semantic-success}` / 음수 `{colors.semantic-danger}` |
| Sparkline (선택) | 우측 60×24px chart-container 미니 |

## 6. `market-toggle` — KOSPI/NASDAQ/양쪽 3-state segmented

위치: `/dashboard`, `/sectors`, `/screener` 헤더 우측 고정.

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Active segment | `{colors.surface-2}` + 1px `{colors.hairline-strong}` |
| Inactive | 투명 배경, text `{colors.ink-subtle}` |
| Segment padding | 6px · 14px |
| Radius (전체) | `{rounded.pill}` |
| Text | `{typography.button}` |

접근성: `role="radiogroup"`, 각 segment `role="radio"` + `aria-checked`. 키보드 ←/→ 이동.

## 7. `trigger-badge` — invalidation trigger 발동 표시 (3 상태)

| 상태 | 배경 | Text |
|------|------|------|
| 미발동 (idle) | `{colors.surface-2}` | `{colors.ink-subtle}` |
| 활성 (fired) | `{colors.semantic-danger}` (#d4564b) | `{colors.canvas}` |
| 음소거 (muted) | `{colors.surface-3}` | `{colors.ink-tertiary}` |

| 속성 | 값 |
|------|-----|
| Padding | 2px · 8px |
| Radius | `{rounded.pill}` |
| Type | `{typography.caption}` |
