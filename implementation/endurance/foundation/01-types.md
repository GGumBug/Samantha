[← README.md로 돌아가기](README.md)

# 01 — Types (도메인 핵심 타입)

**위임**: Friday | **위치**: `src/types/index.ts` (Endurance 프로젝트) | **의존**: 없음 (루트)

## Purpose

Endurance의 모든 자산이 공유할 **도메인 핵심 타입**을 한 파일에 모은다. 시장(KR/US), 종목, 가격, 재무, 거시 지표, AI 응답까지 — 어느 자산도 자기 타입을 따로 만들지 않고 이 파일을 참조한다.

타입의 SSOT를 한 곳에 두면 (a) 자산 간 데이터 흐름이 컴파일러로 검증되고 (b) 명세 변경 시 영향 범위를 grep으로 즉시 식별 가능하다. 헌법 §2 SSOT 원칙의 타입 레이어 적용.

## 의존성

- **사용하는 자산**: 없음 (루트)
- **이걸 사용하는 자산**: 02 ~ 10 모두

## Public Interface

```typescript
// === Market & Security ===

export type Market = "KR" | "US";

export type Currency = "KRW" | "USD";

/** 종목 식별 — 정규화된 ticker (`005930.KS`, `NVDA`) */
export interface Security {
  ticker: string;        // 정규화된 ticker (시장 라우터가 결정)
  name: string;          // 영문 회사명 (Pretendard 한글 fallback 처리)
  nameKr?: string;       // 한국 회사명 (있으면)
  market: Market;
  currency: Currency;
  sector?: string;       // GICS 또는 KOSPI 분류
  industry?: string;
  exchange?: string;     // KRX·NASDAQ·NYSE
}

// === Time-series Data ===

export interface OHLCV {
  date: string;          // ISO 8601 date (YYYY-MM-DD)
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjClose?: number;     // 배당·분할 조정 종가
}

export interface QuarterlyFinancial {
  ticker: string;
  fiscalQuarter: string; // "2025Q3"
  reportDate: string;    // ISO date
  revenue: number;
  netIncome: number;
  eps: number;           // Diluted
  fcf?: number;          // Free Cash Flow
  totalAssets?: number;
  totalDebt?: number;
  roic?: number;         // 계산값 (있으면)
  currency: Currency;
}

// === Macro ===

export interface MacroSnapshot {
  date: string;
  market: Market;
  indexValue: number;        // KOSPI 또는 NASDAQ 종가
  pe12mForward?: number;     // 12M Forward P/E
  epsGrowth1y?: number;      // 1년 EPS 성장률 (%)
  termSpread?: number;       // 10Y - 2Y (%)
  dailyReturnPct?: number;
  vix?: number;              // US만
  foreignNetBuyKrw?: number; // KR만 (외국인 순매수, KRW)
}

// === Trading & Decision ===

export type Side = "BUY" | "SELL";

export type Rating = "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";

export interface Trade {
  id: number;            // SQLite rowid
  ticker: string;
  side: Side;
  quantity: number;
  price: number;
  reason: string;        // 자유 형식 마크다운
  ts: string;            // ISO timestamp
}

export interface Opinion {
  id: number;
  ticker: string;
  rating: Rating;
  thesisMd: string;      // 자유 형식 마크다운
  ts: string;
}

// === AI Response Schemas (zod runtime + TS compile) ===

export interface SwotAnalysis {
  strengths: string[];   // 3-5개
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  summary: string;       // 1-2 문장
}

export interface FiveForcesAnalysis {
  newEntrants: { score: 1|2|3|4|5; reasoning: string };
  suppliers: { score: 1|2|3|4|5; reasoning: string };
  buyers: { score: 1|2|3|4|5; reasoning: string };
  substitutes: { score: 1|2|3|4|5; reasoning: string };
  rivalry: { score: 1|2|3|4|5; reasoning: string };
  overall: 1|2|3|4|5;    // 합산 평가
}

// === Result/Error wrapper (HTTP boundary 일관성) ===

export type Result<T, E = string> =
  | { ok: true; data: T }
  | { ok: false; error: E };
```

## Implementation Notes

- **모든 날짜는 ISO 8601 string**: `Date` 객체 사용 금지. 직렬화·zod·DB·차트 모두 string 우선
- **숫자 타입은 `number`만**: BigInt 사용 금지 (Recharts·zod 호환성). KRW 큰 금액은 정밀도 한계 인지 — 100경 단위까지 안전
- **선택적 필드는 `?:`로 명시**: `null` 사용 금지. DB에서는 NULL → `undefined`로 변환
- **enum 대신 string literal union**: `Market = "KR" | "US"` — 직렬화·zod 친화
- **`Result<T>` 도입 이유**: API boundary에서 throw 의존하지 않고 명시적 분기. 헌법 §0-1 Step 3 (에러 시나리오 검증) 적용
- **zod 스키마는 본 파일 아닌 `src/types/schemas.ts`로 분리** (선택) — 컴파일 타입과 런타임 검증을 같은 파일에 두면 import 그래프가 무거워짐

## Test Strategy

- **컴파일 검증**: `npm run lint` + `tsc --noEmit` 통과
- **타입 사용 예제**: `src/types/__tests__/types.example.ts` 에 5~10개 사용 예 작성. 변경 시 컴파일 깨지면 사용처에 영향 신호
- **zod 스키마 round-trip**: 스키마 정의 시, `T → JSON → parse → T` 동등성 1회 테스트

## Verification

- [ ] `src/types/index.ts` 파일 존재, 위 인터페이스 모두 export
- [ ] `import { Security, OHLCV, ... } from '@/types'` 형태로 다른 파일에서 import 가능
- [ ] `tsc --noEmit` 무경고
- [ ] 타입 사용 예제 파일 1개 추가 (변경 영향 감지용)
- [ ] 누군가 새 타입 추가 시 본 명세도 갱신 (SSOT 동기)

## Open Questions

1. **fiscalQuarter 형식**: `"2025Q3"` vs `{ year: 2025, quarter: 3 }` 객체 — string으로 가되 zod regex 검증 도입할지
2. **Rating enum 5단계 vs 3단계**: STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL 5단계가 너무 세분화인가? 3단계(BUY/HOLD/SELL) 시작 후 확장 가능
3. **Sector 분류 표준**: GICS(미국 표준) vs KRX 자체 분류 — 양 시장 통합 시 매핑 테이블 필요? → 09-sync-scheduler에서 다룸
