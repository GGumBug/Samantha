[← README.md로 돌아가기](README.md)

# 01 — Route Shell + Market Toggle + Layout

**위임**: Friday | **위치**: `endurance/src/app/dashboard/page.tsx` + `endurance/src/app/dashboard/_components/MarketToggleHeader.tsx` (Client) | **의존**: Foundation 07 `market-toggle` 토큰, Foundation 01 `Market` 타입

## Purpose

`/dashboard` 페이지의 **Server Component 진입점** 과 **헤더의 시장 토글(KOSPI / NASDAQ / 양쪽 동시)** 을 박는다. 페이지 본문(04~07 위젯)을 담을 레이아웃 그리드와, 시장 선택 상태가 URL search param(`?market=KR|US|BOTH`)으로 보존되도록 한다.

본 자산은 데이터 페치를 하지 않는다 — 02-data-api가 단일 진입점이며, 02가 반환한 `DashboardSnapshot`을 위젯에 props로 분배한다. 헌법 §0-1 Step 1 영향 분석: `Market` 타입은 Foundation 01에서 박힌 SSOT이며 본 페이지는 그 타입을 그대로 import한다 (새 타입 정의 0건).

## 의존성

- **사용하는 자산**:
  - Foundation 01 — `Market` 타입(`"KR" | "US"`). Phase 1에서 `"BOTH"` 노출이 필요하면 page 로컬 타입(`type DashboardMarket = Market | "BOTH"`)으로 확장(Foundation 01은 건드리지 않음 — SSOT 보존)
  - Foundation 07 — `market-toggle` 토큰 (CSS 토큰 + 컴포넌트 wrapper)
  - Phase 1 02 — `getDashboardSnapshot(market)` 진입점
- **이걸 사용하는 자산**: Phase 1 08 (Integration이 본 shell 안에 04~07 위젯을 꽂음)

## Public Interface

### 라우트

```
GET /dashboard?market=KR | US | BOTH (default: BOTH)
```

### Server Component

```typescript
// src/app/dashboard/page.tsx
import { Market } from "@/types";
import { getDashboardSnapshot } from "@/lib/dashboard/data";
import { MarketToggleHeader } from "./_components/MarketToggleHeader";

type DashboardMarket = Market | "BOTH";

interface DashboardPageProps {
  searchParams: Promise<{ market?: string }>; // Next.js 15 App Router
}

export default async function DashboardPage({ searchParams }: DashboardPageProps) {
  const { market: raw } = await searchParams;
  const market: DashboardMarket = parseMarket(raw); // unknown → "BOTH"
  const snapshot = await getDashboardSnapshot(market);
  return (
    <main className="mx-auto max-w-[1280px] px-6 py-section">
      <MarketToggleHeader current={market} />
      <DashboardGrid market={market} snapshot={snapshot} />
    </main>
  );
}
```

### Client Component (Market Toggle)

```typescript
// src/app/dashboard/_components/MarketToggleHeader.tsx
"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";

export type DashboardMarket = "KR" | "US" | "BOTH";

interface MarketToggleHeaderProps {
  current: DashboardMarket;
}

export function MarketToggleHeader({ current }: MarketToggleHeaderProps): JSX.Element;
```

토글 클릭 시 `router.replace(`${pathname}?market=${next}`, { scroll: false })`. SSR 재진입이 필요하므로 `replace` 사용 — `router.push`는 history 누적.

### DashboardGrid (Server 컴포넌트, 08에서 구현)

본 자산은 placeholder만 정의:

```typescript
// 본 자산 단독 머지 시점에는 grid 안에 "Phase 1 위젯 작업 중" placeholder 표시.
// 08-dashboard-integration이 04~07 위젯을 실제로 꽂는다.
interface DashboardGridProps {
  market: DashboardMarket;
  snapshot: DashboardSnapshot;  // 02-data-api가 export
}
```

## Implementation Notes

- **`searchParams`는 Promise (Next.js 15)** — 반드시 `await`. 동기 접근하면 build 시 경고
- **Default를 `BOTH`로 두는 이유**: Phase 1 핵심 가치는 "양 시장 한 화면 비교". 단일 시장 우선 사용자는 토글로 좁힌다
- **`parseMarket`은 본 파일 내 로컬 함수** — 외부 import 0건. 헌법 §5 오버엔지니어링 회피(1곳에서만 쓰는 인터페이스 안 만듦)
- **Client Component는 Toggle Header만** — `useSearchParams`/`useRouter`가 필요해 client. 그 외 page.tsx와 위젯은 모두 Server Component(데이터 페치는 server에서 끝남)
- **scroll 보존**: `router.replace(..., { scroll: false })` — 토글 시 페이지가 위로 튀지 않도록
- **헌법 §6 escape hatch 적용 가능 영역**: 없음. 본 자산은 production 코드. SOLID/SSOT 완전 적용

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| `Market` 타입 | Foundation 01 SSOT. 본 자산은 import만, 변경 금지 |
| `DashboardMarket = Market \| "BOTH"` | Phase 1 page 로컬. Foundation 01 오염 금지 (`BOTH`는 토글 UI 표현이지 도메인 타입 아님) |
| `?market=` query param | Phase 1 새 contract. 02·08·09가 동일 contract 의존 → 본 명세가 SSOT |

### 헌법 §0-1 Step 2 합리화 회피

- "BOTH도 Foundation 01에 추가하면 간단": ❌ Foundation 01은 도메인 타입(KR/US 시장 자체). BOTH는 UI 토글 표현. SSOT 차원 다름 (코드 식별자 vs UI 표시) → 분리 유지

## Test Strategy

### 단위
- `parseMarket("KR") === "KR"`, `parseMarket("XX") === "BOTH"`, `parseMarket(undefined) === "BOTH"`
- `MarketToggleHeader` 렌더 시 `current="KR"` → KR segment에 `aria-checked="true"`
- **ARIA 정정 사유**: Foundation 07 `role="radiogroup"` 패턴에 따라 자식은 `aria-checked` 사용 (`aria-pressed`는 toggle button 패턴, `radiogroup`과 불일치)

### 통합 (Server Component)
- `/dashboard` 요청 → 200
- `/dashboard?market=KR` → snapshot이 KR만 요청한 응답으로 호출됨 (02 mock)
- `/dashboard?market=XX` → BOTH로 fallback (200, no throw)

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 신기능/API 라우트 추가)
- ✅ 정상 호출: `/dashboard?market=KR|US|BOTH` 3종 모두 200
- ✅ null/empty/edge: `?market=`, `?market=undefined`, query param 누락 → BOTH fallback
- ✅ 입력 검증: `parseMarket`이 zod 또는 narrow union으로 무효 값 차단
- ✅ 인증/시크릿 boundary: 본 라우트는 인증 없음(Phase 1 단일 사용자). 차후 인증 추가 시 본 명세 갱신

### 표준 검증 시나리오 (i18n)
- Phase 1 현재 i18n 미적용 — Open Questions에 "마운트 중 언어 토글 시나리오 미적용" 명시
- 추후 i18n 도입 시 헌법 §2-0-1 데이터 흐름 String Snapshot 절대 금지 적용 의무

## Verification

- [ ] `endurance/src/app/dashboard/page.tsx` 존재 + Server Component (default async export)
- [ ] `endurance/src/app/dashboard/_components/MarketToggleHeader.tsx` 존재 + `"use client"` 디렉티브
- [ ] `tsc --noEmit` 무경고
- [ ] `/dashboard` 접근 시 200 + 토글 헤더 시각 확인 (Foundation 07 토큰 일치)
- [ ] `/dashboard?market=KR` 클릭 → URL 갱신 + 페이지 reload 시 KR 토글 active 보존
- [ ] 토글 변경 시 page scroll 위치 보존 (scroll: false)
- [ ] 02-data-api 미머지 시점: `getDashboardSnapshot`을 stub으로 두고 placeholder grid 렌더 — shell 단독 머지 가능
- [ ] grep으로 `Market` 타입의 새 정의 0건 확인 (Foundation 01 SSOT 준수)

## Open Questions

1. **`DashboardMarket = Market | "BOTH"` 위치**: 본 page 파일에 둘지, 별도 `src/app/dashboard/types.ts`에 둘지. 위젯들이 import 할 가능성이 있으므로 page 분리 폴더로 옮기는 게 자연스러우나, Phase 1 단계에서 사용처가 1~2곳뿐이면 본 파일 유지(헌법 §5 — 사용처 1곳뿐인 모듈 분리 회피)
2. **i18n 적용 시점**: Phase 1에서는 한국어 단일 운용. Phase 2+ 에서 i18n 도입 시 본 shell + 04~07 위젯 모두 `useTranslation` 구독으로 마이그레이션 필요 (헌법 §2-0-1 적용)
3. **Mobile 토글 위치**: 1280px 데스크톱 기준 헤더 우측 고정. 375px 모바일에서 어디 둘지(상단 풀폭 vs 햄버거 안) — 08-integration에서 결정
4. **`router.replace` vs `router.push` 트래킹 영향**: 사용자가 KR↔US 자주 토글하면 history에 안 남는 게 자연스러움. 그러나 "뒤로 가기로 이전 시장 복귀" UX는 손실 — 사용자 검증 후 결정
