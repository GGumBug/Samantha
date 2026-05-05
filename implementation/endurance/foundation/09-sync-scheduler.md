[← README.md로 돌아가기](README.md)

# 09 — Sync Scheduler (일일 데이터 동기화 골격)

**위임**: HAL | **위치**: `src/lib/sync/` + `src/app/api/sync/route.ts` | **의존**: 02-db-schema, 04-yfinance-client, 05-fx-client

## Purpose

엔듀어런스의 모든 시계열 데이터(시세·재무·거시·환율)는 **하루에 한 번 새로고침**되어야 페이지가 최신 데이터를 사용할 수 있다. 본 자산은 일일 동기화의 **골격(orchestration)**만 박는다 — 실제 호출은 04(yfinance), 05(fx)에 위임. cron 자동 실행은 Phase 3에서 도입, **Phase 0은 수동 트리거**(사용자 버튼 또는 dev 명령) 우선.

## 의존성

- **사용하는 자산**: 02-db-schema, 04-yfinance-client, 05-fx-client
- **이걸 사용하는 자산**: 사용자 (settings 페이지 "Sync now" 버튼), 향후 cron job

## Public Interface

```typescript
// src/lib/sync/index.ts
import type { Result } from '@/types';

export interface SyncReport {
  startedAt: string;
  completedAt: string;
  durationMs: number;
  steps: Array<{
    name: string;            // "prices:US", "fx", ...
    ok: boolean;
    inserted?: number;
    updated?: number;
    error?: string;
    durationMs: number;
  }>;
  totalInserted: number;
  totalErrors: number;
}

/** 모든 watchlist 종목 + 거시 + 환율 일일 동기화 */
export async function syncAll(): Promise<Result<SyncReport>>;

/** 특정 ticker만 동기화 (사용자가 종목 페이지에서 새로고침 누를 때) */
export async function syncTicker(ticker: string): Promise<Result<SyncReport>>;

/** watchlist 자체는 syncAll의 입력. 비어있으면 sync 대상 0 */
export function getWatchlist(): string[];
```

## API Route (수동 트리거)

```typescript
// src/app/api/sync/route.ts
import { NextResponse } from 'next/server';
import { syncAll } from '@/lib/sync';

export async function POST() {
  const r = await syncAll();
  if (!r.ok) return NextResponse.json({ error: r.error }, { status: 500 });
  return NextResponse.json(r.data);
}
```

settings 페이지에서 fetch('/api/sync', { method: 'POST' }) 호출. 향후 cron으로 같은 endpoint를 호출하면 끝.

## 실행 흐름

```
syncAll() 시작
  ↓
1. 환율 sync (FX 5)        → fx_rates_daily upsert
2. 거시 지수 sync (yfinance ^KS11, ^IXIC)
                            → macro_snapshots upsert
3. watchlist 종목 prices    → 종목별 prices_daily upsert (병렬 5)
4. watchlist 종목 financials → financials_quarterly upsert (분기마다, daily는 skip)
5. SyncReport 작성 → DB의 sync_history 테이블에 저장 (선택)
```

## Implementation Notes

### 우선순위 + 실패 격리

각 step은 **독립 실행**. step 1(환율) 실패해도 step 2(거시), step 3(prices) 진행. 단, **단계 간 의존이 있으면 의존 우선** (현재는 없음 — 모두 독립).

```typescript
async function syncAll(): Promise<Result<SyncReport>> {
  const steps: SyncReport['steps'] = [];
  
  steps.push(await runStep('fx', () => syncFxLatest()));
  steps.push(await runStep('macro:KR', () => fetchMacroIndex('KR')));
  steps.push(await runStep('macro:US', () => fetchMacroIndex('US')));
  
  const watchlist = getWatchlist();
  for (const ticker of watchlist) {
    steps.push(await runStep(`prices:${ticker}`, () => 
      fetchPricesDaily(ticker, ...lastSyncedDate, today)
    ));
  }
  
  // financials는 분기 변경 시만
  if (isNewQuarter()) {
    for (const ticker of watchlist) {
      steps.push(await runStep(`financials:${ticker}`, () => 
        fetchQuarterlyFinancials(ticker)
      ));
    }
  }
  
  return { ok: true, data: buildReport(steps) };
}
```

### 멱등성 (재실행 안전)

같은 날 sync 두 번 호출해도 DB 상태 동일. 04-yfinance / 05-fx 클라이언트가 캐시 우선이라 외부 호출도 0. 멱등성은 자동 보장.

### Watchlist 출처

Phase 0에서는 settings 페이지의 텍스트 입력으로 ticker 목록 받음 (간단). Phase 1+에서 별도 watchlist 페이지·DB 테이블로 격상.

```typescript
function getWatchlist(): string[] {
  // Phase 0: localStorage 또는 settings.json
  return JSON.parse(localStorage.getItem('endurance:watchlist') ?? '[]');
}
```

### 분기 갱신 감지

```typescript
function isNewQuarter(): boolean {
  const lastSync = getLastSyncReport();
  if (!lastSync) return true;
  return getQuarter(new Date(lastSync.completedAt)) !== getQuarter(new Date());
}
```

분기 변경 시(연 4회)만 financials 호출 — yfinance에 부담 적음. 매일 호출은 낭비.

### 에러 보고

`SyncReport.steps[].error`에 사용자 노출 가능한 에러 메시지. settings 페이지에서 "Sync now" 클릭 후 결과 토스트로 표시.

## Test Strategy

- 단일 step 실패가 전체 sync 중단시키지 않음 (mock으로 step 2 throw 시 step 3+ 정상 실행)
- 동일 날짜 syncAll 2회 호출 시 외부 API 호출 0건 (캐시 hit)
- 빈 watchlist 시 step 0개로 정상 종료
- SyncReport 구조 zod 검증

## Verification

- [ ] `src/lib/sync/index.ts` 작성
- [ ] `src/app/api/sync/route.ts` 작성 (POST 핸들러)
- [ ] settings 페이지에 "Sync now" 버튼 + 결과 표시 (Phase 1 작업이지만 본 명세에 의존)
- [ ] 단위 테스트: 멱등성·실패 격리·빈 watchlist
- [ ] 통합: 실제 watchlist 3개 종목으로 수동 sync 실행 → DB에 행 추가 확인

## Open Questions

1. **자동 cron 시점**: Vercel Cron · GitHub Actions · 로컬 macOS launchd 중 어디? Phase 3에서 결정. Phase 0은 수동만
2. **sync_history 테이블**: 이전 sync 기록 추적 가치 있는가? 있으면 02-db-schema에 추가 (다음 마이그레이션). Phase 1에서 사용자 가시성 필요 시 도입
3. **부분 실패 시 사용자 알림**: 현재는 토스트로만. 중요 실패(연속 3일 실패) 시 이메일·푸시? Phase 4 (triggers와 통합)
4. **시장 휴장일 인지**: 한국·미국 휴장일에 sync 호출하면 어제 데이터 반환. 휴장일 캘린더 도입 필요? Phase 2 검토
