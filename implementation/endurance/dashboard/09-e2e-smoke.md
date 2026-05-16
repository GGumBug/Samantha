[← README.md로 돌아가기](README.md)

# 09 — E2E Smoke (KR / US / 양쪽 토글)

**위임**: Friday | **위치**: `endurance/tests/e2e/dashboard.spec.ts` (Playwright) + 필요 시 `playwright.config.ts` 설정 | **의존**: Phase 1 08 (Integration 완료된 `/dashboard`)

## Purpose

Phase 1 종료 게이트. **실제 브라우저에서 `/dashboard` 페이지가 KR/US/BOTH 3 모드로 동작**함을 자동화된 e2e 시나리오로 검증한다. 단위·통합 테스트만으로는 SSR + Server Component + Client Toggle + 실제 네트워크가 결합한 흐름을 잡지 못함 — 본 자산이 그 갭을 메움.

자체 평가 금지(헌법 §0-1 Step 4): 본 시나리오 통과 = Phase 1 객관적 완료 증명. 미통과면 어떤 단위 테스트가 통과해도 Phase 1 미완료.

## 의존성

- **사용하는 자산**: Phase 1 08 (실제 `/dashboard` 페이지)
- **이걸 사용하는 자산**: 없음 (검증 최종)

## Public Interface

### Playwright 시나리오 3종

```typescript
// endurance/tests/e2e/dashboard.spec.ts
import { test, expect } from "@playwright/test";

test.describe("/dashboard Phase 1 smoke", () => {
  test("default load → BOTH market, 4 widgets rendered", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator('[data-testid="market-toggle"]')).toBeVisible();
    await expect(page.locator('[data-testid="market-toggle"] [aria-checked="true"]')).toHaveText(/BOTH|양쪽/);
    // 4 위젯 data-testid 의무 (08에서 박제)
    await expect(page.locator('[data-testid="widget-pe-cards"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-volatility-sparkline"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-term-spread-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-early-warning-gauge"]')).toBeVisible();
  });

  test("toggle KR → URL updates, widgets re-fetch with KR data", async ({ page }) => {
    await page.goto("/dashboard?market=BOTH");
    await page.locator('[data-testid="market-toggle-KR"]').click();
    await expect(page).toHaveURL(/market=KR/);
    // KOSPI 라벨 표시, NASDAQ 자리 비움
    await expect(page.locator('text=KOSPI')).toBeVisible();
    await expect(page.locator('text=NASDAQ')).not.toBeVisible();
  });

  test("toggle US → URL updates, widgets re-fetch with US data", async ({ page }) => {
    await page.goto("/dashboard?market=BOTH");
    await page.locator('[data-testid="market-toggle-US"]').click();
    await expect(page).toHaveURL(/market=US/);
    await expect(page.locator('text=NASDAQ')).toBeVisible();
    await expect(page.locator('text=KOSPI')).not.toBeVisible();
  });

  test("toggle BOTH → both markets data visible", async ({ page }) => {
    await page.goto("/dashboard?market=KR");
    await page.locator('[data-testid="market-toggle-BOTH"]').click();
    await expect(page).toHaveURL(/market=BOTH/);
    await expect(page.locator('text=KOSPI')).toBeVisible();
    await expect(page.locator('text=NASDAQ')).toBeVisible();
  });

  test("scroll position preserved on toggle (router.replace { scroll: false })", async ({ page }) => {
    await page.goto("/dashboard");
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.locator('[data-testid="market-toggle-KR"]').click();
    const scrollY = await page.evaluate(() => window.scrollY);
    expect(scrollY).toBeGreaterThanOrEqual(400); // scroll 보존 (이동 시 약간의 reflow는 허용)
  });
});
```

### data-testid 명명 규약 (08에서 박제)

08-dashboard-integration이 다음 data-testid를 위젯·토글에 박는 의무:

| 컴포넌트 | data-testid |
|---------|-------------|
| Market Toggle 컨테이너 | `market-toggle` |
| Toggle segment (각각) | `market-toggle-KR`, `market-toggle-US`, `market-toggle-BOTH` |
| P/E Metric Cards | `widget-pe-cards` |
| Volatility Sparkline | `widget-volatility-sparkline` |
| Term Spread Chart | `widget-term-spread-chart` |
| Early Warning Gauge | `widget-early-warning-gauge` |
| Error Badge Row | `error-badge-row` |

본 자산이 e2e 시나리오를 박는 시점에 08 명세에 위 data-testid 명명 규약을 동기 갱신 의무 (헌법 §2 SSOT — testid는 e2e와 컴포넌트가 공유하는 식별자).

## Implementation Notes

- **Playwright 설치**: Phase 1 최초 e2e이므로 `npm install -D @playwright/test` + `npx playwright install` 필요. **본 PR이 최초 도입**
- **dev server 실행**: Playwright config에서 `webServer: { command: "npm run dev", port: 3000 }` 자동 기동
- **네트워크 mock 여부**: 실제 yfinance 호출은 CI에서 flaky → MSW 또는 Playwright `page.route()`로 `/api/dashboard` 응답 fixture 사용 권장. **fixture 데이터는 `tests/fixtures/dashboard-snapshot.json`에 박제**
- **`data-testid` 의무**: e2e가 시각·label 텍스트에 의존하면 i18n·UI 변경 시 깨짐. data-testid는 UI 변경과 무관한 안정 식별자
- **시나리오 5종이 본 자산 범위**: default load, KR toggle, US toggle, BOTH toggle, scroll 보존. 그 외(예: refresh, 에러 상태)는 Phase 2+ 추가
- **헌법 §6 escape hatch**: 없음. 본 자산은 production CI 게이트

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| 08의 컴포넌트 data-testid 명명 | 본 자산이 의존. 08 명세에 명명 규약 박제 의무 |
| 01의 토글 URL 동작 (`?market=`) | 본 자산이 검증. 01 명세 변경 시 본 시나리오 갱신 |
| 02의 응답 fixture | 본 자산이 mock으로 박음. 02 응답 스키마 변경 시 fixture 갱신 의무 |
| `playwright.config.ts` 신규 도입 | endurance 프로젝트 최초 e2e 인프라. CI 통합 후속 작업 명시 |

### 헌법 §0-1 Step 2 합리화 회피

- "수동 시각 검증으로 충분": ❌ Phase 1 종료 후 Phase 2~5에서 회귀 발생 시 자동 감지 불가. e2e 박제 의무
- "data-testid 안 박고 label 텍스트로 잡기": ❌ i18n·문구 변경 시 깨짐. data-testid 의무

## Test Strategy

### 시나리오 통과 기준 (헌법 §0-1 Step 3 — 신기능 / e2e 시장 토글)
- ✅ 정상 호출: KR/US/BOTH 3 모드 모두 4 위젯 렌더
- ✅ 토글 시 데이터 갱신: URL 변경 + 위젯 내용 변경
- ✅ 양쪽 모드 동시 표시: KOSPI + NASDAQ 텍스트 모두 visible
- ✅ scroll 보존: 토글 시 페이지 스크롤 위치 유지
- ✅ null/empty edge: 02 응답 빈 blocks fixture 시나리오(선택, Phase 1.1) — 본 PR은 정상 흐름만

### 비동기 시나리오 (헌법 §0-1 Step 3 — Server Action / fetch)
- ✅ 정상 완료: 위젯 4종 모두 렌더 후 visible
- ✅ 토글 중 이전 fetch 취소: KR → US → KR 빠르게 토글 시 화면이 마지막 KR 데이터로 안정 (AbortSignal 동작 — 02 의무)
- ✅ 재진입 atomicity: 동일 market 빠른 더블 클릭 시 위젯 중복 렌더 0건

### CI 통합
- GitHub Actions(또는 동등)에서 `npm run test:e2e` 실행
- fixture 사용 → 외부 API 의존 0건 (재현성 보장)

## Verification

- [ ] `endurance/tests/e2e/dashboard.spec.ts` 존재 + 시나리오 5종 작성
- [ ] `playwright.config.ts` 존재 + webServer 자동 기동
- [ ] `tests/fixtures/dashboard-snapshot.json` 존재 + 02 응답 형태
- [ ] `npm run test:e2e` 로컬에서 통과 (전 5 시나리오)
- [ ] 08 명세에 data-testid 명명 규약 동기 박제 (Verification 항목)
- [ ] CI에서 e2e 시나리오 실행 가능 — 본 PR 또는 후속 PR
- [ ] fixture 데이터로 외부 API 의존 0건 검증

## Open Questions

1. **CI 인프라**: 현재 endurance 프로젝트에 CI 워크플로우 미존재 가능성. 본 자산이 CI 워크플로우(`.github/workflows/e2e.yml` 또는 동등)도 함께 박을지 — **Phase 1 scope 외 가능성**. 합리적 분리: 본 PR은 로컬 통과만, CI 통합은 별도 후속 PR (Phase 1.1)
2. **시각 회귀(스크린샷)**: Playwright `toHaveScreenshot()` 으로 시각 회귀 자동 감지 가능. 헌법 §4 검증 가치 큼. 그러나 Phase 1 초기에는 baseline 스크린샷 fluctuation 위험 — Phase 2+ 도입
3. **모바일 e2e**: Playwright `devices['iPhone 13']` 시뮬레이션 가능. Phase 1 desktop만 검증, mobile은 Phase 2+
4. **fixture 데이터 SSOT**: fixture가 02 응답 스키마와 어긋나면 silent fail. zod로 fixture를 02 응답 스키마에 매번 검증할지 — Phase 2+ 자동화. Phase 1은 수동 동기
5. **i18n 토글 시나리오**: i18n 미도입 상태이므로 본 자산 시나리오에 없음. i18n 도입 후 헌법 §0-1 Step 3 "마운트 중 언어 토글" 시나리오 추가 의무
