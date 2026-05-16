[← README.md로 돌아가기](README.md)

# 09 — E2E Smoke (v2 GEMSTONE: 시장+모델 토글 + 7 위젯 + Refresh)

> **변경 이력**
> - v2 (2026-05-16): GEMSTONE EWS 재정의에 맞춰 책임 갱신. 사유: 사용자가 GEMSTONE 스크린샷 단언 후 정공 재정의 (옵션 D). 기존 v1 코드 처리 정책은 §"v1 코드 처리" 참고.
> - v1 (이전): KR/US/BOTH 토글 + 4 위젯 시나리오 5종.

**위임**: Friday | **위치**: `endurance/tests/e2e/dashboard.spec.ts` (Playwright) + 필요 시 `playwright.config.ts` 설정 | **의존**: Phase 1 08 (v2 Integration 완료된 `/dashboard`)

## v1 코드 처리

v1 시나리오 5종(default load, KR toggle, US toggle, BOTH toggle, scroll 보존) → **폐기, v2 시나리오 신규 작성**. v1 spec 파일(`dashboard.spec.ts`)은 코드 자체는 보존(git history 참고용)하되, 모든 test 함수를 v2 시나리오로 교체. fixture(`tests/fixtures/dashboard-snapshot.json`)는 02 v2 `DashboardSnapshot` 시그니처 기준 재생성 의무.

- v1 fixture: v1 `DashboardMacroBlock` 4 필드 → 폐기
- v2 fixture: `DashboardGemstoneBlock`(intensity·forwardExpectancy·performance·modelInputs) + `DashboardModelMeta` 기준 신규 작성
- v1 testid 잔재(`widget-pe-cards`·`widget-volatility-sparkline`·`widget-term-spread-chart`·`widget-early-warning-gauge`) → v2 testid(`widget-intensity-gauge`·`widget-stage-badge`·`widget-forward-expectancy`·`widget-performance-analytics`·`widget-model-inputs`·`widget-model-meta`·`widget-refresh`)로 교체

## Purpose

Phase 1 종료 게이트. **실제 브라우저에서 `/dashboard` 페이지가 KR/US/BOTH 3 모드로 동작**함을 자동화된 e2e 시나리오로 검증한다. 단위·통합 테스트만으로는 SSR + Server Component + Client Toggle + 실제 네트워크가 결합한 흐름을 잡지 못함 — 본 자산이 그 갭을 메움.

자체 평가 금지(헌법 §0-1 Step 4): 본 시나리오 통과 = Phase 1 객관적 완료 증명. 미통과면 어떤 단위 테스트가 통과해도 Phase 1 미완료.

## 의존성

- **사용하는 자산**: Phase 1 08 (실제 `/dashboard` 페이지)
- **이걸 사용하는 자산**: 없음 (검증 최종)

## Public Interface

### Playwright 시나리오 7종 (v2)

```typescript
// endurance/tests/e2e/dashboard.spec.ts
import { test, expect } from "@playwright/test";

test.describe("/dashboard Phase 1 v2 GEMSTONE smoke", () => {
  test("default load → BOTH market + model1_forced, 7 widgets rendered", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator('[data-testid="market-toggle"]')).toBeVisible();
    await expect(page.locator('[data-testid="model-toggle"]')).toBeVisible();
    // v2 7 위젯 testid 의무 (08에서 박제)
    await expect(page.locator('[data-testid="widget-intensity-gauge"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-stage-badge"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-forward-expectancy"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-performance-analytics"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-model-inputs"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-model-meta"]')).toBeVisible();
    await expect(page.locator('[data-testid="widget-refresh"]')).toBeVisible();
  });

  test("market toggle KOSPI200 → URL updates, widgets re-fetch", async ({ page }) => {
    await page.goto("/dashboard?market=BOTH");
    await page.locator('[data-testid="market-toggle-KOSPI200"]').click();
    await expect(page).toHaveURL(/market=KR/);
    await expect(page.locator('text=KOSPI200')).toBeVisible();
  });

  test("market toggle S&P 500 → URL updates, widgets re-fetch", async ({ page }) => {
    await page.goto("/dashboard?market=BOTH");
    await page.locator('[data-testid="market-toggle-SP500"]').click();
    await expect(page).toHaveURL(/market=US/);
    await expect(page.locator('text=S&P 500')).toBeVisible();
  });

  test("model toggle Model 2 Optimal → URL updates + model meta changes", async ({ page }) => {
    await page.goto("/dashboard?market=BOTH");
    const beforeSharpe = await page.locator('[data-testid="widget-model-meta"]').textContent();
    await page.locator('[data-testid="model-toggle-model2_optimal"]').click();
    await expect(page).toHaveURL(/model=model2_optimal/);
    const afterSharpe = await page.locator('[data-testid="widget-model-meta"]').textContent();
    expect(afterSharpe).not.toEqual(beforeSharpe); // OOS Sharpe 값 변경
  });

  test("Stage 1-5 badge displays expected stage from intensity score", async ({ page }) => {
    await page.goto("/dashboard?market=KR");
    const stageBadge = page.locator('[data-testid="widget-stage-badge"]');
    await expect(stageBadge).toBeVisible();
    // fixture 시나리오에서 intensity.score=74 → Stage 4 (Warning) 라벨 표시
    await expect(stageBadge).toContainText(/Stage [1-5]/);
  });

  test("Forward Expectancy 5 bucket 표 — 5 rows with horizon labels", async ({ page }) => {
    await page.goto("/dashboard?market=KR");
    const table = page.locator('[data-testid="widget-forward-expectancy"]');
    await expect(table).toBeVisible();
    // 5 horizon bucket: 5d / 20d / 60d / 120d / 250d
    await expect(table.locator('text=/5d|20d|60d|120d|250d/')).toHaveCount(5);
  });

  test("Performance Analytics chart + 3 metrics (cumReturn, Sharpe, MDD)", async ({ page }) => {
    await page.goto("/dashboard?market=KR");
    const widget = page.locator('[data-testid="widget-performance-analytics"]');
    await expect(widget).toBeVisible();
    await expect(widget.locator('text=/Cumulative|누적/i')).toBeVisible();
    await expect(widget.locator('text=/Sharpe/i')).toBeVisible();
    await expect(widget.locator('text=/MDD|Drawdown/i')).toBeVisible();
  });

  test("MODEL INPUTS — 7 sparkline cards with gemstone IDs", async ({ page }) => {
    await page.goto("/dashboard?market=KR");
    const widget = page.locator('[data-testid="widget-model-inputs"]');
    await expect(widget).toBeVisible();
    // 7 GEMSTONE 카드: garnet/emerald/moonstone/sapphire/topaz/ruby/amber
    await expect(widget.locator('[data-testid^="model-input-card-"]')).toHaveCount(7);
  });

  test("Refresh button → snapshot.generatedAt updates", async ({ page }) => {
    await page.goto("/dashboard?market=KR");
    const refresh = page.locator('[data-testid="widget-refresh"]');
    await expect(refresh).toBeVisible();
    await refresh.click();
    // 로딩 indicator 표시 후 다시 데이터 visible — 자세 검증은 자산 17 단위 테스트
    await expect(refresh).toBeEnabled();
  });

  test("scroll position preserved on toggle (router.replace { scroll: false })", async ({ page }) => {
    await page.goto("/dashboard");
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.locator('[data-testid="market-toggle-KOSPI200"]').click();
    const scrollY = await page.evaluate(() => window.scrollY);
    expect(scrollY).toBeGreaterThanOrEqual(400);
  });
});
```

### data-testid 명명 규약 v2 (08에서 박제)

08-dashboard-integration v2가 다음 data-testid를 위젯·토글에 박는 의무 (SSOT는 08 명세):

| 컴포넌트 | data-testid |
|---------|-------------|
| Market Toggle 컨테이너 (자산 16) | `market-toggle` |
| Market segment (v2 라벨 갱신) | `market-toggle-KOSPI200`, `market-toggle-SP500`, `market-toggle-BOTH` |
| Model Toggle 컨테이너 (자산 12) | `model-toggle` |
| Model segment | `model-toggle-model1_forced`, `model-toggle-model2_optimal` |
| INTENSITY 게이지 + Stage 배지 (자산 11) | `widget-intensity-gauge`, `widget-stage-badge` |
| Model 메타 카드 (자산 12) | `widget-model-meta` |
| Forward Expectancy 5 bucket 표 (자산 13) | `widget-forward-expectancy` |
| Performance Analytics 차트+메트릭 (자산 14) | `widget-performance-analytics` |
| MODEL INPUTS 7 카드 grid (자산 15) | `widget-model-inputs`, `model-input-card-{gemstoneId}` |
| Refresh 버튼 (자산 17) | `widget-refresh` |
| Error Badge Row | `error-badge-row`, `error-badge-KR`, `error-badge-US` |

본 자산이 e2e 시나리오를 박는 시점에 08 명세에 위 data-testid 명명 규약을 동기 갱신 의무 (헌법 §2 SSOT — testid는 e2e와 컴포넌트가 공유하는 식별자).

## Implementation Notes

- **Playwright 도입**: `npm install -D @playwright/test` + `npx playwright install`. dev server 자동 기동 (`webServer.command: "npm run dev"`)
- **네트워크 mock**: yfinance·ML inference flaky → Playwright `page.route()`로 `/api/dashboard` fixture 사용. fixture 파일: `tests/fixtures/dashboard-gemstone-snapshot.json`
- **`data-testid` 의무**: i18n·UI 변경에 안정. label 텍스트 의존 금지 (caller-driven 안티패턴)
- **v2 시나리오 7~10종**: default load + market 토글(KOSPI200/SP500) + model 토글 + Stage 배지 + Forward Expectancy 표 + Performance 차트 + MODEL INPUTS 7카드 + Refresh + scroll 보존
- **헌법 §6 escape hatch**: 없음. production CI 게이트

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| 08 v2의 data-testid 명명 | 본 자산이 의존. 08 SSOT |
| 01 v2 토글 URL 동작 + 라벨 갱신 | 본 자산이 검증. 01 v2 변경 시 본 시나리오 갱신 |
| 02 v2 응답 fixture | 본 자산이 mock으로 박음. 02 v2 스키마 변경 시 fixture 재생성 의무 |
| `playwright.config.ts` 신규 도입 | endurance 프로젝트 최초 e2e 인프라 |

## Test Strategy

### 시나리오 통과 기준 (헌법 §0-1 Step 3 — 신기능 + 비동기)
- 정상 호출 6 조합(market × model) 모두 7 위젯 렌더
- 토글 데이터 갱신: URL + 위젯 내용 동기
- AbortSignal: 빠른 토글 시 마지막 선택 데이터 안정
- 재진입 atomicity: 더블 클릭 시 위젯 중복 렌더 0건
- i18n 토글 시나리오: Phase 2+ 도입 시 추가 의무 (현재 미적용)

### CI 통합
- `npm run test:e2e` GitHub Actions 실행. fixture로 외부 API 의존 0건

## Verification

- [ ] `endurance/tests/e2e/dashboard.spec.ts` v2 시나리오 7~10종 작성
- [ ] `playwright.config.ts` + webServer 자동 기동
- [ ] `tests/fixtures/dashboard-gemstone-snapshot.json` v2 시그니처 박힘
- [ ] `npm run test:e2e` 로컬 통과
- [ ] v1 fixture·시나리오 잔재 grep 0건 (`pe12mForward\|widget-pe-cards\|widget-term-spread-chart` 등)
- [ ] 08 v2 data-testid 규약 동기 박제 확인
- [ ] fixture로 외부 API 의존 0건

## Open Questions

1. **CI 인프라**: endurance 프로젝트 CI 워크플로우 미존재 가능성. 본 PR vs 후속 분리 결정.
2. **시각 회귀(`toHaveScreenshot`)**: Phase 2+ baseline 안정화 후 도입 검토.
3. **모바일 e2e**: Phase 1 desktop만. mobile은 Phase 2+.
4. **fixture zod 검증**: 02 v2 스키마와 fixture 자동 정합 검증 — Phase 2+ 자동화.
5. **i18n 토글 시나리오**: Phase 2+ i18n 도입 후 헌법 §0-1 Step 3 "마운트 중 언어 토글" 추가 의무.
