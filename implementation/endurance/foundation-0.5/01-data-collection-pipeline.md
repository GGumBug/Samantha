[← README.md로 돌아가기](README.md)

# 01 — Data Collection Pipeline (yfinance + FRED + ECOS, 2005~ 일별)

**위임**: HAL | **위치**: `endurance/src/lib/data/collectors/`, `endurance/data/raw/` | **의존**: Foundation 02 (DB Schema), 04 (yfinance Client), 09 (sync-scheduler)

## Purpose

GEMSTONE 7 변수 계산의 **원시 데이터 단일 진입점**. yfinance(가격·거래량), FRED(거시 시계열), ECOS(KR 시장 보완)을 일별 OHLCV/시계열 row 로 통합 수집하고, 2005-01-01 ~ today 범위를 SQLite 에 적재한다.

수집 자체는 sync-scheduler step 으로 등록 — 일일 cron 으로 누락 분만 incremental fetch. 본 자산이 안정화되어야 02 변수 계산 엔진이 결정론적으로 동작.

## 의존성

- **사용하는 자산**: Foundation 02 (DB Schema — `prices_daily`, `macro_series`, `index_universe` 테이블 확장), 04 (yfinance Client — 시세 fetch), 09 (sync-scheduler — `collectMarketData` step 등록)
- **이걸 사용하는 자산**: 02 (변수 계산 엔진), 03 (학습 데이터셋 생성기), 06 (백테스트 엔진)

## Public Interface

```typescript
// === Collectors ===

/** yfinance — 지수·종목 OHLCV 일별 */
export async function collectYfinanceDaily(params: {
  tickers: string[];          // ["^KS200", "^GSPC", "CL=F", ...]
  startDate: string;          // ISO date, 기본 "2005-01-01"
  endDate: string;            // ISO date, 기본 today
  incremental?: boolean;      // true 면 DB last_date 이후만 fetch
}): Promise<Result<{ rowsInserted: number; tickers: string[] }>>;

/** FRED — 거시 시계열 */
export async function collectFredSeries(params: {
  seriesIds: string[];        // ["T10Y2Y", "T10YIE", "VIXCLS", "MOVE" or "DTB3"]
  startDate?: string;
  endDate?: string;
  incremental?: boolean;
}): Promise<Result<{ rowsInserted: number; seriesIds: string[] }>>;

/** ECOS — KR 시장 보완 (KOSPI200 시총·거래량 보완, KR CPI) */
export async function collectEcosSeries(params: {
  statCodes: string[];        // ECOS 통계표 코드
  startDate?: string;
  endDate?: string;
  incremental?: boolean;
}): Promise<Result<{ rowsInserted: number; statCodes: string[] }>>;

/** KOSPI200 종목 리스트 (한국거래소 정적 CSV 분기 갱신) */
export async function refreshKospi200Universe(params: {
  csvPath: string;            // `endurance/data/raw/kospi200/<YYYY-MM-DD>.csv`
}): Promise<Result<{ tickers: string[]; effectiveDate: string }>>;

/** 통합 entry point (sync-scheduler step) */
export async function collectMarketData(): Promise<SyncStepReport>;
```

## Implementation Notes

- **incremental fetch**: 각 collector 는 DB 의 `MAX(date) WHERE ticker=?` 를 조회하고 그 다음날부터 fetch. 첫 실행만 2005-01-01 시작 — 백필 1회.
- **API key 격리**: FRED `FRED_API_KEY`, ECOS `ECOS_API_KEY` 는 환경변수 only. 코드에 박지 않음 (헌법 §0-1 Step 3 — 인증/시크릿 boundary).
- **rate limit**: yfinance 는 Foundation 04 의 client 가 처리. FRED 는 60req/min, ECOS 는 1000req/day — collector 내부 throttle (간단한 `setTimeout` 충분, 큐 라이브러리 도입 안 함 — 헌법 §5 오버엔지니어링 회피).
- **Fed Policy Rate Uncertainty 대용**: MOVE Index(`MOVE` 또는 BofA `ML_MOVE`) 우선 시도, 실패 시 3M T-Bill 변동성(`DTB3` rolling std) — Step 4 학습 시 어느 쪽이 라벨 분산 잘 설명하는지 비교 후 확정.
- **결정론**: 같은 날짜 범위 재호출 시 결과 동일 (UPSERT). 외부 API 변동 시 raw 응답은 `endurance/data/raw/<source>/<date>.json` 저장 — 재현 가능성 보장.
- **헌법 §6 escape hatch**: 한국거래소 KOSPI200 종목 리스트 CSV 다운로드는 1회성 수동 단계 — 자동 스크랩 도입 안 함 (분기 1회 운영). 분기 갱신 누락 시 alert 별도 명세 안 박음.

## Test Strategy

- **단위**: 각 collector mock fetch 로 incremental 분기 검증 (`MAX(date)` 정상 / 빈 DB / 휴장일)
- **통합**: 2005-01-01 ~ 2005-02-28 1개월 백필 → DB row 수 검증 (KOSPI200 영업일 ≈ 40개)
- **재현성**: 같은 날짜로 2회 호출 시 INSERT 0건 (UPSERT 작동)
- **헌법 §0-1 Step 3 신기능**: ① 정상 호출 ② 빈 응답(휴장일) ③ 인증 실패 ④ 부분 실패 시 다른 source 계속

## Verification

- [ ] 4 collector 함수 export, `Result<T>` 일관성
- [ ] sync-scheduler 에 `collectMarketData` step 등록
- [ ] 2005-01-01 ~ today 백필 1회 완료, DB row 수 sanity check (`prices_daily` ≥ 50만건)
- [ ] FRED·ECOS API key 환경변수 only — grep 으로 코드 내 키 0건
- [ ] raw 응답 캐싱 디렉토리(`endurance/data/raw/`) 구조 확인
- [ ] 두 번째 호출 시 외부 API 0건 (캐시·incremental 검증)

## Open Questions

1. **MOVE Index 접근성**: FRED 에 MOVE 시리즈가 무료 공개되어 있는지 확인 필요. 막히면 T-Bill 변동성 대용 — 04 학습 단계에서 검증.
2. **ECOS 통계표 코드 SSOT**: 사용할 ECOS 시리즈를 어디 박을지 — `endurance/src/lib/data/collectors/ecos-series.ts` 에 상수 객체로 박고 본 명세에 링크. 구현 시 결정.
3. **백필 1회 비용**: 2005~ 일별 백필이 yfinance rate limit 에 걸리지 않는지. 걸리면 종목별 batch + sleep — 구현 시 측정.
