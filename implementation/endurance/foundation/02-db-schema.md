[← README.md로 돌아가기](README.md)

# 02 — DB Schema (SQLite 9개 테이블 + 마이그레이션)

**위임**: HAL | **위치**: `src/lib/db.ts` + `src/lib/db-schema.ts` + `data/endurance.db` | **의존**: 01-types

## Purpose

Endurance의 모든 영구 데이터(시세·재무·매매·의견·거시·환율)를 단일 SQLite 파일에 저장한다. **로컬 우선 + 단일 파일 백업**으로 일생 사용 가능한 데이터 자립성을 확보한다. job-search-master의 `lib/db.ts` better-sqlite3 + WAL 모드 패턴을 그대로 포팅한다.

## 의존성

- **사용하는 자산**: 01-types
- **이걸 사용하는 자산**: 04-yfinance-client (write), 05-fx-client (write), 09-sync-scheduler (orchestrate), 10-preview-page (read), 모든 페이지의 server actions (read/write)

## Public Interface

```typescript
// src/lib/db.ts
import Database from 'better-sqlite3';
import type { Security, OHLCV, QuarterlyFinancial, MacroSnapshot, Trade, Opinion } from '@/types';

/** 단일 진입점 — 어플리케이션 전체에서 동일 인스턴스 공유 (싱글턴) */
export function getDb(): Database.Database;

/** 마이그레이션 실행 — 앱 시작 시 1회 자동 호출 */
export function runMigrations(db: Database.Database): void;

/** 트랜잭션 헬퍼 — 다중 INSERT/UPDATE 원자성 */
export function withTx<T>(db: Database.Database, fn: () => T): T;

// === Repository 함수 (자산별 별도 파일에 분산) ===

// src/lib/db/securities.ts
export function upsertSecurity(s: Security): void;
export function getSecurity(ticker: string): Security | undefined;
export function listSecurities(market?: Market): Security[];

// src/lib/db/prices.ts
export function insertPricesDaily(rows: OHLCV[], ticker: string): void;
export function getPricesDaily(ticker: string, fromDate: string, toDate: string): OHLCV[];
export function getLatestPrice(ticker: string): OHLCV | undefined;

// src/lib/db/financials.ts
export function insertFinancials(rows: QuarterlyFinancial[]): void;
export function getFinancials(ticker: string, quarters: number): QuarterlyFinancial[];

// src/lib/db/trades.ts
export function insertTrade(t: Omit<Trade, 'id'>): Trade;
export function listTrades(ticker?: string): Trade[];

// src/lib/db/opinions.ts
export function insertOpinion(o: Omit<Opinion, 'id'>): Opinion;
export function getLatestOpinion(ticker: string): Opinion | undefined;

// src/lib/db/macro.ts
export function upsertMacroSnapshot(s: MacroSnapshot): void;
export function getMacroSnapshot(market: Market, date: string): MacroSnapshot | undefined;
export function getMacroRange(market: Market, fromDate: string, toDate: string): MacroSnapshot[];

// src/lib/db/fx.ts
export function upsertFxRate(date: string, pair: string, rate: number): void;
export function getFxRate(date: string, pair: string): number | undefined;
```

## SQL Schema

```sql
-- 01_initial.sql
CREATE TABLE securities (
  ticker      TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  name_kr     TEXT,
  market      TEXT NOT NULL CHECK (market IN ('KR','US')),
  currency    TEXT NOT NULL CHECK (currency IN ('KRW','USD')),
  sector      TEXT,
  industry    TEXT,
  exchange    TEXT,
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE prices_daily (
  ticker     TEXT NOT NULL,
  date       TEXT NOT NULL,         -- ISO date
  open       REAL NOT NULL,
  high       REAL NOT NULL,
  low        REAL NOT NULL,
  close      REAL NOT NULL,
  volume     INTEGER NOT NULL,
  adj_close  REAL,
  PRIMARY KEY (ticker, date),
  FOREIGN KEY (ticker) REFERENCES securities(ticker)
);
CREATE INDEX idx_prices_date ON prices_daily(date);
CREATE TABLE financials_quarterly (
  ticker          TEXT NOT NULL,
  fiscal_quarter  TEXT NOT NULL,    -- "2025Q3"
  report_date     TEXT NOT NULL,
  revenue         REAL NOT NULL,
  net_income      REAL NOT NULL,
  eps             REAL NOT NULL,
  fcf             REAL,
  total_assets    REAL,
  total_debt      REAL,
  roic            REAL,
  currency        TEXT NOT NULL,
  PRIMARY KEY (ticker, fiscal_quarter)
);
CREATE TABLE holdings (
  ticker          TEXT PRIMARY KEY,
  quantity        REAL NOT NULL,
  avg_price       REAL NOT NULL,
  entry_lots_json TEXT NOT NULL DEFAULT '[]',  -- 분할 매수 차수
  updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE trades (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  ticker    TEXT NOT NULL,
  side      TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
  quantity  REAL NOT NULL,
  price     REAL NOT NULL,
  reason    TEXT NOT NULL DEFAULT '',
  ts        TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_trades_ticker_ts ON trades(ticker, ts DESC);
CREATE TABLE opinions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  ticker     TEXT NOT NULL,
  rating     TEXT NOT NULL,
  thesis_md  TEXT NOT NULL DEFAULT '',
  ts         TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_opinions_ticker_ts ON opinions(ticker, ts DESC);
CREATE TABLE triggers (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  scope         TEXT NOT NULL,           -- "macro", "ticker:NVDA"
  condition_json TEXT NOT NULL,          -- JSON으로 조건식
  fired_at      TEXT,                    -- NULL이면 미발동
  muted         INTEGER NOT NULL DEFAULT 0,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE macro_snapshots (
  date            TEXT NOT NULL,
  market          TEXT NOT NULL CHECK (market IN ('KR','US')),
  index_value     REAL NOT NULL,
  pe_12m_forward  REAL,
  eps_growth_1y   REAL,
  term_spread     REAL,
  daily_return_pct REAL,
  vix             REAL,
  foreign_net_buy_krw REAL,
  PRIMARY KEY (date, market)
);
CREATE TABLE fx_rates_daily (
  date  TEXT NOT NULL,
  pair  TEXT NOT NULL,                   -- "KRW/USD"
  rate  REAL NOT NULL,
  PRIMARY KEY (date, pair)
);

-- 마이그레이션 추적
CREATE TABLE schema_migrations (
  version  TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## Implementation Notes

- WAL 모드 (`pragma journal_mode = WAL`) + FK 활성 (`pragma foreign_keys = ON`)
- Prepared statement 재사용: 모듈 레벨에서 `db.prepare(...)` 1회
- 마이그레이션 순서: `migrations/01_initial.sql`, `02_xxx.sql` 알파벳 순 자동 실행, `schema_migrations` 테이블로 멱등성 보장
- DB 경로: `data/endurance.db` (`.gitignore`)
- 백업: 단일 파일이라 `cp`로 가능, 자동 백업 cron은 추후

## Test Strategy

- 마이그레이션 멱등성: in-memory DB(`:memory:`) 2회 실행 시 에러 없음
- CRUD 라운드트립: 각 테이블 insert → get → 동등성 (5개 sample)
- 트랜잭션 롤백: `withTx` 안에서 throw 시 모든 변경 사라짐
- 외래키·CHECK 위반: 잘못된 ticker·enum 값 거부

## Verification

- [ ] `npm install better-sqlite3 @types/better-sqlite3` 완료
- [ ] `.gitignore`에 `data/*.db`, `data/*.db-journal`, `data/*.db-wal` 추가
- [ ] `src/lib/db.ts` + `src/lib/db-schema.ts` + repository 모듈 작성
- [ ] `migrations/01_initial.sql` 작성, 첫 실행 시 자동 적용
- [ ] 단위 테스트 4건 통과, 앱 첫 실행 시 DB 자동 생성 확인

## Open Questions

1. 마이그레이션 라이브러리: 직접 작성 vs `better-sqlite3-helper` — 직접 작성 시작 (의존성 최소)
2. `holdings.entry_lots_json`: SQLite JSON1 확장. 분할 매수 차수 추적 필요 시 사용, Phase 0 미사용
3. Time zone: 모든 timestamp `datetime('now')` UTC, 표시는 UI 레이어에서 KST 변환
