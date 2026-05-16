[← README.md로 돌아가기](README.md)

# 16 — Market Toggle GEMSTONE 갱신 (자산 F)

**위임**: Friday | **위치**: `endurance/src/app/dashboard/_components/MarketToggleHeader.tsx` (자산 01 v2 갱신과 동일 파일) | **의존**: Foundation 07 `market-toggle` 토큰, 자산 01 v2 갱신 결과

## Purpose

GEMSTONE 스크린샷 패턴에 맞춰 **시장 토글 라벨을 KOSPI200 / S&P 500 / BOTH로 갱신**. 자산 01-route-shell v2 §"v1 코드 처리"와 동일 결과를 본 명세에서 **단일 책임 SSOT**로 박는다.

자산 01의 v2 갱신과 본 자산은 **동일 컴포넌트 파일을 다루지만 분리 명세 이유**:
- 자산 01 = 페이지 진입점(Server Component) + 토글 헤더 책임. v2 갱신은 라벨 변경 부분만.
- 자산 16 = GEMSTONE 디자인 정합성 책임(라벨·data-testid·radiogroup wrapper) — SSOT 단일 진입점.

PR 머지 시 자산 01 v2와 자산 16은 **동일 파일 변경을 공유**. 시니어 판단으로 둘 중 하나의 PR에 함께 박고 나머지는 명세만 갱신.

## 의존성

- **사용하는 자산**:
  - Foundation 07 `market-toggle` 토큰 (radiogroup wrapper, testIdPrefix prop)
  - 자산 01 v2 (DashboardPage 진입점 SSR 흐름)
- **이걸 사용하는 자산**: Phase 1 08 (Integration — 헤더 좌측 배치)

## Public Interface

자산 01 v2의 시그니처와 동일:

```typescript
"use client";

export type DashboardMarket = "KR" | "US" | "BOTH";

const MARKET_DISPLAY_LABELS: Record<DashboardMarket, string> = {
  KR: "KOSPI200",
  US: "S&P 500",
  BOTH: "BOTH",
};

const MARKET_TESTID_SUFFIX: Record<DashboardMarket, string> = {
  KR: "KOSPI200",
  US: "SP500",
  BOTH: "BOTH",
};

interface MarketToggleHeaderProps {
  current: DashboardMarket;
}

export function MarketToggleHeader(props: MarketToggleHeaderProps): JSX.Element;
```

표시 형태:

```
[ KOSPI200 ] [ S&P 500 ] [ BOTH ]
```

data-testid:
- 컨테이너: `market-toggle`
- segment: `market-toggle-KOSPI200`, `market-toggle-SP500`, `market-toggle-BOTH`

## Implementation Notes

- **자산 01과 동일 컴포넌트 — 시그니처 표 SSOT는 본 명세**: 자산 01 v2 §"v1 코드 처리"가 동일 결과 박지만 본 명세가 시각·접근성 SSOT (Joi 영역 매핑). Friday(자산 01) + Joi 모두 본 명세 참조 의무.
- **표시 라벨 vs 도메인 식별자 분리 (헌법 §2 차원)**:
  - 도메인 식별자: `Market = "KR" | "US"` (Foundation 01 SSOT) + `BOTH` 로컬 (자산 01)
  - URL search param: `?market=KR|US|BOTH` (v1 그대로 보존 — 외부 link 호환성)
  - 표시 라벨: `KOSPI200` / `S&P 500` / `BOTH` (v2 갱신)
  - data-testid: `market-toggle-KOSPI200` / `market-toggle-SP500` / `market-toggle-BOTH` (v2 갱신)
- **i18n key 적용 (Phase 2+ 도입 시)**: 현재 라벨은 영어 단일(`KOSPI200`, `S&P 500`). Phase 2 i18n 도입 시 `market.label.kospi200` / `market.label.sp500` 키 박혀야 함. 본 명세 갱신 의무.
- **Foundation 07 radiogroup wrapper testIdPrefix prop**: 본 자산이 `testIdPrefix="market-toggle"` 박음. 자산 12(모델 토글)는 `testIdPrefix="model-toggle"`. wrapper SSOT 보존.

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Foundation 07 `MarketToggle` wrapper testIdPrefix prop | 본 자산 + 자산 12가 의존. wrapper 변경 시 양쪽 영향 |
| 자산 01 v2 표시 라벨/testid 갱신 | 본 명세가 SSOT. 자산 01 §"v1 코드 처리"가 본 명세 참조 |
| 자산 09 e2e 시나리오 testid (`market-toggle-KOSPI200` 등) | 본 명세가 SSOT |

### 헌법 §0-1 Step 2 합리화 회피

- "라벨을 caller(page.tsx)가 props로 전달": ❌ caller-driven UI string snapshot (§2-0-1). 컴포넌트 내부 매핑 의무
- "URL search param도 KOSPI200/SP500으로 갱신": ❌ 외부 link/북마크 호환성 손실. URL param은 v1 그대로 유지가 SSOT

## Test Strategy

### 단위
- `MARKET_DISPLAY_LABELS.KR === "KOSPI200"` (라벨 매핑 SSOT)
- `MARKET_TESTID_SUFFIX.US === "SP500"`
- `current="KR"` 렌더 시 KOSPI200 segment aria-checked=true + 텍스트 "KOSPI200" 표시
- 토글 클릭 → `router.replace(...?market=US...)` URL 갱신 (search param은 KR/US/BOTH 도메인 식별자 유지)

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 신기능 + i18n 마운트 토글)
- 정상 토글: KR/US/BOTH 클릭 시 URL + aria-checked 정합
- i18n: 마운트 중 언어 토글 시 라벨 자동 갱신 — Phase 1 i18n 미적용 상태이므로 본 항목은 Phase 2+ 도입 시 검증 의무 (caller-driven string 0건 grep 박혀 있어야 함)
- anti-pattern §2-0-1 grep 0건 (라벨 매핑은 컴포넌트 내부 const, props로 라벨 string 받지 않음)

## Verification

- [ ] `MARKET_DISPLAY_LABELS` 매핑 상수 본 컴포넌트 내부에 존재 (자산 01과 동일 파일)
- [ ] data-testid `market-toggle-KOSPI200` / `market-toggle-SP500` / `market-toggle-BOTH` 박힘
- [ ] grep `market-toggle-KR\|market-toggle-US` 본 파일 0건 (v1 testid 잔재 제거)
- [ ] grep "KR" "US" 문자열 표시 라벨로 사용 0건 (표시는 KOSPI200/SP500)
- [ ] URL search param 키는 v1 그대로 (`?market=KR|US|BOTH`) — 외부 호환성 보존 검증
- [ ] Foundation 07 radiogroup wrapper testIdPrefix prop 사용
- [ ] anti-pattern §2-0-1 grep 0건
- [ ] 자산 01 §"v1 코드 처리" 동기 갱신 확인 (SSOT 일치)

## Open Questions

1. **i18n 적용 시점**: Phase 1 한국어 단일이지만 라벨이 영어(`KOSPI200` · `S&P 500`). Phase 2 i18n 도입 시 키 보존 명세 갱신 의무. 초안은 영어 단일.
2. **"S&P 500" vs "SP500" 표기**: HTML 표시는 `S&P 500` (앰퍼샌드 + 공백). testid는 `SP500` (URL-safe). 일관 표기 우선.
3. **모바일 토글 위치**: 자산 01 Open Q와 동일. 자산 08 integration이 결정.
