[← README.md로 돌아가기](README.md)

# 02 — `/api/dashboard` Data API (v2 GEMSTONE EWS)

> **변경 이력**
> - v2 (2026-05-16): GEMSTONE EWS 재정의에 맞춰 책임 갱신. 사유: 사용자가 GEMSTONE 스크린샷 단언 후 정공 재정의 (옵션 D). 기존 v1 구현 코드는 이 명세 §"v1 코드 처리"에 따라 처리.
> - v1 (이전): P/E·EPS·Term Spread·Volatility 4 필드 placeholder 산식.

**위임**: HAL | **위치**: `endurance/src/lib/dashboard/data.ts` (단일 진입점) + `endurance/src/app/api/dashboard/route.ts` (HTTP wrapper, 선택) | **의존**: Foundation 01 (Types), 02 (DB), 03 (Market Router), 04 (yfinance), 05 (FX), Phase 0.5 05 (ML inference), Phase 0.5 06 (Backtest)

## v1 코드 처리

v1 `DashboardSnapshot` 시그니처는 **완전 교체**. 보존 대상 0건, 마이그레이션 4건:

- v1 `DashboardMacroBlock`(`pe12mForward`·`epsGrowth1y`·`dailyReturnPct`·`volatility30d`·`volatilitySeries`·`termSpread`·`termSpreadSeries`·`earlyWarningScore`) → v2 `DashboardGemstoneBlock`(7 MODEL INPUTS + INTENSITY + Stage + Forward Expectancy + Performance Analytics)으로 교체
- v1 `early-warning.ts` placeholder 산식 함수(`calculateEarlyWarning`) → Phase 0.5 05 `infer()` 호출로 교체. v1 함수는 폐기(파일 자체는 보존하되 본문은 `@deprecated` + 본 v2 진입점 호출)
- v1 단위 테스트 10건(v1 placeholder 산식 검증) → 폐기, v2 시그니처 기준 단위 테스트 재작성
- v1 yfinance·FX 클라이언트 결합 흐름 → v2에서도 재사용 + Phase 0.5 05 inference 호출 + Phase 0.5 06 backtest report 로드 결합

## Purpose

`/dashboard` 페이지(GEMSTONE EWS)가 필요로 하는 **모든 거시·ML·백테스트 데이터를 단일 함수 호출로 정규화 응답**으로 반환한다. Phase 0 yfinance·FX 클라이언트 + Phase 0.5 05 ML inference 어댑터 + Phase 0.5 06 백테스트 report 결합 결과를 `DashboardSnapshot` 한 객체로 합쳐 페이지·위젯 11~17(A~G)에 전달한다.

이 자산은 **본 Phase 1의 데이터 SSOT** 이다 — 위젯 11~17은 본 함수가 반환한 `DashboardSnapshot`만 읽으며, 각자 외부 API·ML inference·backtest report를 호출하지 않는다(헌법 §2 SSOT). 위젯이 각자 호출하면 동일 데이터 다중 페치 + 캐시 불일치 + 부분 실패 처리 분산 → 헌법 §2 위반.

## 의존성

- **사용하는 자산**:
  - Foundation 01 — `Market`, `MacroSnapshot`, `OHLCV`, `Result<T>` 타입
  - Foundation 02 — DB 캐시 (선택, `macro_snapshots` 테이블에 일별 캐시)
  - Foundation 03 — `market-router` (KOSPI/NASDAQ 식별자 → yfinance 심볼 매핑)
  - Foundation 04 — `yfinance-client` (시세·재무 메타)
  - Foundation 05 — `fx-client` (KRW/USD 환산 — Phase 1에서는 노출 안 하지만 호출 흐름 유지)
- **이걸 사용하는 자산**:
  - Phase 1 01 (route shell이 SSR 시점에 호출)
  - Phase 1 04, 05, 06, 07 (props로 분배받음, 직접 호출 금지)
  - Phase 1 08 (Integration에서 위젯에 분배)

## Public Interface

### 라이브러리 함수 (단일 진입점)

```typescript
// src/lib/dashboard/data.ts
import type { Market, Result } from "@/types";
import type { InferenceOutput } from "@/lib/ml";          // Phase 0.5 05
import type { BacktestReport } from "@/lib/backtest";     // Phase 0.5 06
import type { GemstoneVariables } from "@/lib/variables"; // Phase 0.5 02

export type DashboardMarket = "KR" | "US" | "BOTH";
export type ModelKind = "model1_forced" | "model2_optimal"; // 헤더 토글 (자산 12)

export interface DashboardGemstoneBlock {
  market: Market;                          // "KR" (KOSPI200) | "US" (S&P 500)
  indexSymbol: string;                     // "^KS200" | "^GSPC"
  asOf: string;                            // ISO date (가장 최근 거래일)

  // INTENSITY 게이지 + Stage 배지 (자산 11)
  intensity: {
    score: number;                         // 0-100 (예: 74)
    stage: 1 | 2 | 3 | 4 | 5;              // Stage 1-5 (Phase 0.5 06 stages.ts SSOT)
    stageLabelKey: string;                 // "ews.stage.normal|watch|caution|warning|critical"
    weightingHintKey: string;              // "ews.weighting.expand|reduce" — "비중 확대/축소"
    modelKind: "mlp" | "svm_rbf";
    modelTrainedAt: string;
  };

  // FORWARD EXPECTANCY 5 bucket (자산 13)
  forwardExpectancy: {
    buckets: Array<{
      horizonDays: number;                 // 5 / 20 / 60 / 120 / 250
      expectancy: number;                  // 평균 forward return (%)
      hitRate: number;                     // 0-1
      sampleSize: number;
    }>;
  };

  // PERFORMANCE ANALYTICS (자산 14)
  performance: {
    equityCurve: Array<{ date: string; nav: number; benchmarkNav: number }>;
    metrics: {
      cumulativeReturnVsBenchmark: number; // % delta
      sharpe: number;
      maxDrawdown: number;                 // 음수 %
    };
  };

  // MODEL INPUTS 7 변수 카드 (자산 15)
  modelInputs: Array<{
    gemstoneId: "garnet" | "emerald" | "moonstone" | "sapphire" | "topaz" | "ruby" | "amber";
    currentValue: number;
    zScore: number;
    sparkline: Array<{ date: string; value: number }>; // 90포인트 권장
    regimeKey: "modelInput.regime.neutral" | "modelInput.regime.reversion";
  }>;
}

export interface DashboardModelMeta {
  // 자산 12 (모델 메타 카드)
  modelKind: ModelKind;
  selectedVariables: Array<2 | 8 | 9 | 16>; // Model 1 Forced [2,8,9,16] / Model 2 Optimal: 동적
  oosSharpe: number;
  oosCumulativeReturn: number;             // %
  oosFalseAlarmRate: number;
}

export interface DashboardSnapshot {
  generatedAt: string;                     // ISO timestamp
  selectedModel: ModelKind;                // 자산 12 토글 상태
  modelMeta: DashboardModelMeta;
  blocks: DashboardGemstoneBlock[];        // market 선택에 따라 1 또는 2개
  errors: { market: Market; code: string; message: string }[]; // 부분 실패 가시화
}

export async function getDashboardSnapshot(
  market: DashboardMarket,
  options?: {
    signal?: AbortSignal;
    force?: boolean;                       // 캐시 무시 (자산 17 Refresh 버튼)
    modelKind?: ModelKind;                 // default "model1_forced"
  },
): Promise<DashboardSnapshot>;
```

### HTTP Route Handler (선택)

Server Component가 직접 `getDashboardSnapshot`을 호출하면 HTTP 라우트는 필요 없음. 그러나 Client 측 refresh 버튼 등을 위해 thin wrapper 제공:

```
GET /api/dashboard?market=KR | US | BOTH
→ 200 application/json: DashboardSnapshot
→ 4xx: { error: string }  (signal abort 시 499 권장)
```

## Implementation Notes

- **단일 진입점 의무 (헌법 §2 SSOT)**: 04~07 위젯이 각자 yfinance·FX를 호출하지 않는다. 본 함수가 합쳐 반환. **위젯 명세 검증 시 외부 API import 0건 grep 의무**
- **부분 실패 가시화**: KR 성공 + US 실패 시 throw 금지. `blocks=[KR]` + `errors=[{market:"US", ...}]`로 양쪽 가시. 페이지는 KR 카드 + US 자리에 trigger-badge로 에러 표시
- **`AbortSignal` 의무 (헌법 §0-1 Step 3 비동기 시나리오)**: 위젯 마운트 중 시장 토글 시 이전 fetch 취소. `getDashboardSnapshot(market, { signal })`로 전파
- **재진입 atomicity**: 동일 market 동시 호출 시 in-flight dedup 권장(`Map<market, Promise>`). 캐시 hit이 먼저 일어나면 자동으로 해결
- **캐시 정책** (Foundation 02 `macro_snapshots` 테이블):
  - 일별 캐시. 같은 날짜 + market 조합은 DB에서 즉시 반환 (외부 API 0건)
  - `force: true`면 캐시 무시 + 신규 페치 + DB 갱신
  - TTL: 거래일 종가는 다음 거래일까지 변동 없음 → 자정 KST 기준 만료
- **`BOTH` 분기**: `Promise.allSettled([fetchKR, fetchUS])` — 한쪽 reject가 다른 쪽 차단하지 않음
- **헌법 §6 escape hatch**: 본 자산은 production 코드. escape hatch 없음

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Foundation 04 `yfinance-client` 인터페이스 | 본 함수가 호출. 시그니처 변경 시 본 자산 + 위젯 11~17 호출 사슬 일괄 갱신 |
| Phase 0.5 05 `infer()` 시그니처 | 본 함수가 호출 (각 시점/모델별 INTENSITY 산출). 변경 시 동기 갱신 |
| Phase 0.5 06 `BacktestReport` 스키마 | 본 함수가 로드 (Performance Analytics + Forward Expectancy). 변경 시 동기 갱신 |
| `DashboardGemstoneBlock` v2 신규 타입 | 본 자산이 SSOT. 위젯 11~17이 본 타입을 props로 받음 |
| v1 `DashboardMacroBlock` 폐기 | v1 import 잔재 grep 0건 확인 의무 |

### 헌법 §0-1 Step 2 합리화 회피

- "위젯이 자기 데이터 직접 페치하면 단순": ❌ 동일 데이터 4번 페치 + 부분 실패 분산 + 캐시 동기화 불가능 → SSOT 위반
- "BOTH 시 한쪽 실패하면 throw가 단순": ❌ KR만 보여줄 수 있는데 전체 화면 에러는 UX 손실 → `Promise.allSettled` 의무

## Test Strategy

### 단위·통합
- KR/US/BOTH 호출 → blocks 길이 정합 + 부분 실패 시 `errors[]` 가시화 (yfinance mock US reject)
- DB 캐시 hit 시 외부 API call count 0 + `force: true` 시 캐시 무시
- ML inference mock 결과가 `intensity.score`로 정확 전달 (Phase 0.5 05 SSOT 의무)

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 비동기/fetch + 신기능)
- 정상 + AbortSignal cancel + 재진입 atomicity + 에러 경계 (`errors[]` throw 0건)

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 신기능/API 라우트 추가)
- ✅ 정상 호출 + null/empty (시장 휴장일 응답)
- ✅ zod 검증: yfinance·ML inference 응답을 `DashboardGemstoneBlock`으로 정규화
- ✅ 인증/시크릿 boundary: yfinance API key는 server-only env. Client 노출 0건 grep

## Verification

- [ ] `endurance/src/lib/dashboard/data.ts` 존재 + `getDashboardSnapshot` export
- [ ] 단위 테스트 6개 이상 통과 (KR/US/BOTH × 정상/부분실패/AbortSignal)
- [ ] `tsc --noEmit` 무경고
- [ ] yfinance 호출 시 Phase 0 04 클라이언트만 사용 (`grep "yahoo-finance2" src/lib/dashboard/data.ts` 0건 — Phase 0 04를 우회하지 않음)
- [ ] DB 캐시 hit 시 외부 API call count 0건 (통합 테스트로 증명)
- [ ] `Result<T>` 또는 `errors` 배열로 부분 실패 가시화 — throw 0건 (정상 흐름)
- [ ] HTTP wrapper `/api/dashboard` 라우트(선택): 동일 응답 + 4xx 처리
- [ ] v2 시그니처: `DashboardGemstoneBlock` 7 필드(intensity·forwardExpectancy·performance·modelInputs·market·indexSymbol·asOf) + `DashboardModelMeta` 박힘
- [ ] v1 잔재 grep: `DashboardMacroBlock\|pe12mForward\|epsGrowth1y\|volatility30d\|termSpreadSeries\|earlyWarningScore` 본 파일 0건
- [ ] Phase 0.5 05 `infer()` 호출 — `getDashboardSnapshot` 내부 import 확인 (grep)
- [ ] Phase 0.5 06 backtest report 로드 — `equityCurve`, `expectancyByBucket` 파일 또는 in-memory cache 진입 확인
- [ ] anti-pattern §2-0-1 Pattern A·B grep: `(name|description|label|title|stageLabel):\s*string` 본 타입 정의에서 0건 — i18n 키만 박음 (`stageLabelKey`, `regimeKey` 등)

## Open Questions

1. **HTTP wrapper 필수 여부**: 자산 17 Refresh 버튼이 Server Action으로 처리하면 HTTP 라우트 불필요. 자산 17 결정 후 본 명세 동기 갱신.
2. **시장 휴장일 처리**: 한국·미국 휴일 다름. `asOf` 다른 날짜 가능. UI 명시 위치 — 자산 11/15에서 결정.
3. **`DashboardGemstoneBlock` 시계열 필드 직렬화 비용**: `performance.equityCurve`가 ~3000+ 포인트 → JSON 직렬화 비용. 02가 downsampling 박을지 or 자산 14 전달 시점 결정.
