[← README.md로 돌아가기](README.md)

# 07 — Design Tokens (데이터 비즈 컴포넌트 7종)

**위임**: Joi | **위치**: `design-system/components.md` 확장 + `endurance/src/components/{data-table,chart,gauge,heatmap,metric,market-toggle,trigger-badge}/` | **의존**: 01-types

## Purpose

기존 디자인 시스템(`design-system/components.md`)은 마케팅 카피·CTA·카드 중심. 데이터 대시보드는 **표·차트·게이지·히트맵** 중심이라 새 토큰 7종이 필요하다. 마케팅 스택과 동일한 다크 캔버스·라벤더 강조·Pretendard 정신을 유지하면서 **정량 데이터 표시에 최적화**된 컴포넌트 명세를 박는다.

토큰만 명세하고 실제 구현은 08-chart-library 결정 후. 이 명세는 **시각 SSOT**이며 모든 페이지가 임의 색상·크기 사용하지 않고 본 토큰 경유.

## 의존성

- **사용하는 자산**: 01-types (Market, OHLCV 등 데이터 형태 참조)
- **이걸 사용하는 자산**: 08-chart-library, 10-preview-page, 모든 Phase 1+ 페이지

## 7종 신규 토큰

### 1. `data-table` — 정렬·필터·페이지네이션 표

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Header text | `{typography.eyebrow}` (`{colors.ink-subtle}`) |
| Body text | `{typography.body-sm}` (`{colors.ink}`) |
| Row hover | `{colors.surface-2}` |
| Selected row | `{colors.primary-focus}` 좌측 2px border |
| Border (cell) | 없음 (행 구분은 hairline-tertiary 1px bottom만) |
| Padding (cell) | 12px · 16px |
| Numeric cell | `font-feature-settings: 'tnum'` (자릿수 정렬) |
| Sort indicator | 우측 8px 화살표 (`{colors.ink-subtle}` → 활성 시 `{colors.primary}`) |

기반: TanStack Table v8 (헤드리스). 마크업은 디자인 시스템 토큰 적용한 자체 wrapper.

### 2. `chart-container` — 차트 wrapper

| 속성 | 값 |
|------|-----|
| Background | `{colors.canvas}` (차트 자체는 surface-1 위지만 차트 영역은 canvas로 끊어 시각 분리) |
| Padding | 16px (모바일) · 24px (데스크톱) |
| Border-radius | `{rounded.lg}` |
| Title | `{typography.eyebrow}` 위쪽 |
| Tooltip | surface-2 배경 + hairline-strong 1px |
| Grid line | `{colors.hairline-tertiary}` 1px |
| Axis label | `{typography.caption}` (`{colors.ink-subtle}`) |
| 라인 색 | `{colors.primary}` (단일) / 다중 시리즈는 라벤더 명도 시퀀스 |

### 3. `gauge-meter` — 0~100 조기 경보 게이지

반원형 SVG 게이지. 색 구간:
- 0~30: `{colors.semantic-success}` (#27a644) 안전
- 30~70: `{colors.ink-muted}` 중립
- 70~90: `#f0a04b` (커스텀, 디자인 시스템 추가) 경계
- 90~100: `#d4564b` (커스텀, 추가) 경고

크기 옵션:
- `sm` 80×40px (대시보드 사이드)
- `md` 160×80px (히어로 영역)
- `lg` 240×120px (상세 페이지)

### 4. `heatmap-cell` — 섹터 수익률 히트맵 셀

| 속성 | 값 |
|------|-----|
| 음수 (-10% ~ 0%) | `#3a2a2a` ~ `#5a3a3a` 그라데이션 |
| 중립 (0% 근처) | `{colors.surface-2}` |
| 양수 (0 ~ +20%) | `#2a4a3a` ~ `#3a6a4a` 그라데이션 |
| Text | `{colors.ink}` 또는 `{colors.ink-muted}` (대비 자동) |
| Border | 1px `{colors.hairline-tertiary}` |
| Padding | 12px |

라벤더는 사용 안 함 — 라벤더는 브랜드·CTA 전용 (헌법 §1).

### 5. `metric-card` — 단일 거시 지표 카드

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` + 1px `{colors.hairline}` |
| Padding | 20px |
| Border-radius | `{rounded.lg}` |
| Label | `{typography.eyebrow}` (`{colors.ink-subtle}`) |
| Value | `{typography.display-md}` (40px / 600) |
| Delta | 14px / 500, 양수 = `{colors.semantic-success}`, 음수 = `#d4564b` |
| Sparkline (선택) | 우측 60×24px chart-container 미니 |

### 6. `market-toggle` — KOSPI / NASDAQ / 양쪽 토글

3-state segmented control.

| 속성 | 값 |
|------|-----|
| Background | `{colors.surface-1}` |
| Active segment | `{colors.surface-2}` + 1px `{colors.hairline-strong}` |
| Inactive | 배경 투명, text `{colors.ink-subtle}` |
| Padding (segment) | 6px 14px |
| Border-radius | `{rounded.pill}` (전체) |
| Text | `{typography.button}` |

`/dashboard`, `/sectors`, `/screener` 헤더 우측 고정 위치.

### 7. `trigger-badge` — invalidation trigger 발동 표시

| 상태 | 배경 | Text |
|------|------|------|
| 미발동 | `{colors.surface-2}` | `{colors.ink-subtle}` |
| 활성 (조건 충족) | `#d4564b` (warning) | `{colors.canvas}` |
| 음소거 | `{colors.surface-3}` | `{colors.ink-tertiary}` |

| 속성 | 값 |
|------|-----|
| Padding | 2px 8px |
| Border-radius | `{rounded.pill}` |
| Type | `{typography.caption}` |

## 신규 색상 추가 (디자인 시스템 확장)

`design-system/colors.md` 의 시맨틱 섹션에 4색 추가:

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{colors.semantic-warning}` | `#f0a04b` | 게이지 70-90, trigger 경계 |
| `{colors.semantic-danger}` | `#d4564b` | 게이지 90+, delta 음수, trigger 발동 |
| `{colors.heatmap-positive-base}` | `#2a4a3a` | 히트맵 양수 base |
| `{colors.heatmap-negative-base}` | `#3a2a2a` | 히트맵 음수 base |

**라벤더 보존 원칙 유지**: 위 4색은 데이터 시각화 전용. 마케팅 CTA·강조에 사용 금지.

## Implementation Notes

- 모든 토큰은 Tailwind v4 `@theme` 블록에 추가 → `bg-warning`, `text-danger`, `bg-heatmap-pos`, etc.
- 신규 색상 4종 추가는 `design-system/colors.md` 갱신 + `endurance/src/app/globals.css` 동시 적용 (SSOT 동기)
- `data-table`, `chart-container`는 큰 컴포넌트라 자체 폴더(`src/components/data-table/`)에 분할 작성
- `gauge-meter`는 SVG 직접 작성 (~80줄). Recharts 같은 라이브러리 의존 안 함

## Test Strategy

- 시각 검증: 10-preview-page에 모든 토큰 + 모든 상태(default/hover/active/disabled) 렌더
- 접근성: `data-table` 키보드 정렬, `gauge-meter` aria-valuenow, `market-toggle` role="radiogroup"
- 다크 모드 단일 — 라이트 모드 미존재 검증 (`prefers-color-scheme: light` 시도해도 같은 색상)
- Pretendard 적용 검증: 한글·숫자 혼합 표 행에서 자릿수 정렬 (`tnum`) 동작

## Verification

- [ ] `design-system/components.md` 에 7종 토큰 섹션 추가
- [ ] `design-system/colors.md` 에 4색 추가 (warning/danger/heatmap-pos/neg)
- [ ] `endurance/src/app/globals.css` `@theme` 블록 신규 색상 추가
- [ ] 7개 컴포넌트 폴더 생성 (`src/components/{data-table,chart,gauge,heatmap,metric,market-toggle,trigger-badge}/`)
- [ ] 10-preview-page에서 모든 토큰 시각 확인 (라이트/다크 일관성, 모바일·데스크톱)
- [ ] 라벤더 사용처가 4가지(브랜드·1차 CTA·포커스·링크 강조) 외에 0건 확인 (grep)

## Open Questions

1. **히트맵 색상 공감각**: 빨강=손실/초록=이익은 한국 정서와 반대. KR 사용자 설정 토글로 색 반전 옵션 도입? Phase 0 스코프 외, V2 검토
2. **게이지 sm 크기 (80×40px)**: 모바일 대시보드에서 가독성 문제 가능. preview에서 사용자 검증 필수
3. **TanStack Table v8 도입**: 헤드리스라 의존성 작음. 거의 확정. Phase 0 시작 시 `npm install @tanstack/react-table`
