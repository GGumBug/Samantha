[← DESIGN.md로 돌아가기](DESIGN.md)

# Layout — 스페이싱·그리드·엘리베이션·셰이프

## Spacing — 4px 베이스

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{spacing.xxs}` | 4px | 인라인 간격, 작은 칩 패딩 |
| `{spacing.xs}` | 8px | 버튼 내부 vertical 패딩, 작은 갭 |
| `{spacing.sm}` | 12px | 인풋 horizontal 패딩, 중간 갭 |
| `{spacing.md}` | 16px | 카드 내부 콘텐츠 갭, 기본 갭 |
| `{spacing.lg}` | 24px | 카드 내부 패딩 (피처/가격 카드) |
| `{spacing.xl}` | 32px | 카드 내부 패딩 (testimonial), 패널 외부 갭 |
| `{spacing.xxl}` | 48px | CTA 배너 내부 패딩 |
| `{spacing.section}` | 96px | 섹션 간 vertical 간격 |

## 컴포넌트별 패딩 표준

| 컴포넌트 | 패딩 (vertical · horizontal) |
|----------|-----------------------------|
| Pill 버튼 (Linear 컴팩트 스펙) | 8px · 14px |
| 폼 인풋 | 8px · 12px |
| 피처/가격 카드 | 24px (전 방향) |
| Testimonial 카드 | 32px (전 방향) |
| CTA 배너 | 48px (전 방향) |
| 푸터 | 64px · 32px |

## Grid & Container

- **Max content width**: 1280px (`max-w-screen-xl` 또는 커스텀)
- **카드 그리드**: 데스크톱 3-up · 태블릿 2-up · 모바일 1-up
- **가격 티어**: 데스크톱 3-up + 비교 strip
- **제품 스크린샷 패널**: 콘텐츠 폭 100% — 주인공이므로

```tsx
// 표준 컨테이너 패턴
<div className="mx-auto max-w-[1280px] px-4 md:px-6 lg:px-8">
  {children}
</div>
```

## 여백 철학

> **다크 캔버스가 곧 여백**입니다.

- 섹션 분리는 `{spacing.section}` 96px vertical 갭이 아니라 **surface lift**로 표현 (canvas → surface-1)
- 패널 내부에서는 `{spacing.lg}` 24px 갭으로 콘텐츠 블록 분리
- 흰색 사이의 빈 공간 개념 금지 — 어둠 속 lift 차이로 구획

## Elevation — 4단계 + Focus

Linear의 깊이는 surface ladder + hairline border가 담당. **drop shadow는 다크 모드에서 거의 사용 안 함**.

| 레벨 | 처리 | 사용처 |
|------|------|-------|
| 0 (flat) | 그림자·테두리 없음 | 본문 텍스트, 히어로 텍스트, 푸터 |
| 1 (charcoal lift) | `{colors.surface-1}` 배경 + 1px `{colors.hairline}` | 기본 카드, 제품 패널 |
| 2 (surface-2 lift) | `{colors.surface-2}` 배경 + 1px `{colors.hairline-strong}` | 추천 가격 카드, 호버된 카드 |
| 3 (surface-3 lift) | `{colors.surface-3}` 배경 | 서브 내비, 드롭다운 메뉴 |
| 4 (focus ring) | 2px `{colors.primary-focus}` outline @ 50% opacity | 포커스된 인풋·버튼 |

### 장식 깊이

- **제품 UI 스크린샷이 dominant decorative depth**
- 분위기 그라디언트 금지·스포트라이트 카드 금지
- **Subtle white edge highlight**: lifted 패널 상단에 1px 흰색 (rgba(255,255,255,0.04)) — "픽셀 렌더링" 느낌

```css
.surface-1 {
  background: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-top-color: rgba(255, 255, 255, 0.04); /* 미세 상단 하이라이트 */
}
```

## Shapes — Border Radius 스케일

| 토큰 | 값 | 사용처 |
|------|-----|-------|
| `{rounded.xs}` | 4px | 작은 칩, status 배지 |
| `{rounded.sm}` | 6px | 인라인 태그 |
| `{rounded.md}` | 8px | **모든 버튼**, 폼 인풋 |
| `{rounded.lg}` | 12px | 가격/피처/testimonial 카드 |
| `{rounded.xl}` | 16px | **제품 스크린샷 패널** |
| `{rounded.xxl}` | 24px | 오버사이즈 CTA 배너 (드물게) |
| `{rounded.pill}` | 9999px | 가격 탭 토글, status pill |
| `{rounded.full}` | 9999px | 아바타 원 |

### 셰이프 결정 트리

```
인터랙티브 요소인가?
├─ 버튼·인풋 → {rounded.md} 8px (절대 pill 금지)
├─ 가격 탭·status → {rounded.pill}
└─ 아바타 → {rounded.full}

콘텐츠 컨테이너인가?
├─ 일반 카드 → {rounded.lg} 12px
├─ 제품 스크린샷 → {rounded.xl} 16px
└─ 메가 CTA → {rounded.xxl} 24px (드물게)
```

## 사진·일러스트 지오메트리

- 제품 UI 스크린샷: `{rounded.xl}` 16px 타일, 외부 패딩 `{spacing.lg}` 24px
- 고객사 로고 타일: `{colors.canvas}` 위 ~24px 로고 높이, 테두리 없음
- testimonial 아바타: `{rounded.full}` 32~40px

## Tailwind v4 매핑 예

```css
@theme {
  --spacing-xxs: 0.25rem;  /* 4px */
  --spacing-xs: 0.5rem;
  --spacing-sm: 0.75rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-xxl: 3rem;
  --spacing-section: 6rem;
  
  --radius-xs: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-pill: 9999px;
}
```

이렇게 하면 `p-lg`, `rounded-md` 같은 의미적 유틸이 작동합니다.
