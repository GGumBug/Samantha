# Glob: **/*.{ts,tsx,jsx,js,mjs,cjs,css,scss},**/package.json,**/tsconfig.json,**/next.config.*,**/tailwind.config.*,**/components.json

## 엔지니어링 헌법 (사용자 명시 없이 항상 적용 — 단, 상황 적합성 우선)

웹 코드 작업 시 **사용자가 매번 요구하지 않아도** 다음 원칙들을 자동 적용합니다. 사용자가 "SOLID 지켜줘", "SSOT 고려해줘", "디자인 패턴 써줘", "유지보수/확장성 챙겨줘" 같은 말을 다시 할 필요가 없도록 박제된 기본값입니다.

> 이 헌법은 Samantha/Joi/Friday/HAL/GERTY 모두에게 자동 적용됩니다. **단일 진실 원천은 이 파일 하나** — 다른 곳에 복사 금지(DRY).

### 0. 메타 원칙 — 헌법이 오버엔지니어링이 되지 않도록

이 헌법 자체가 코드보다 비대해지면 안 됩니다. **원칙은 비용 0이 아닙니다.**

- 패턴/추상화 도입은 항상 비용(가독성↓, 신규 진입자 학습 비용↑, 디버깅 stack frame↑)을 동반함
- "원칙을 적용하지 않는 것"이 더 시니어한 결정인 경우가 자주 있음 — 이 판단을 회피하지 말 것
- "원칙대로 했다"가 자체 정당화가 될 수 없음. 항상 **"왜 이 비용을 지불했는가"**가 함께 설명되어야 함

#### 0-1. Senior Default Mode (모든 변경 작업의 기본 사고 체계)

사용자가 "시니어 판단해줘"라고 매번 말하지 않아도 **모든 코드 변경 작업에 자동 적용**되는 4단계 표준 사고. 누락 시 사고 재발 보장.

**Step 1 — 변경 전 영향 분석 (Before 자동)**:
- grep으로 변경 대상 심볼/패턴의 **모든 호출처/의존처** 식별, 영향 범위를 분류 테이블로 명시 (자동 위임/수동 처리/외부 시스템). "SSOT 어느 축에 영향?" 검증 (코드 식별자 / 사용자 노출 / 메타)
- **상속·구현 관계 분석 시 `extends|implements` grep + 결과 표 작성 의무**. 사전 조사를 일부 케이스에 제한 금지 — grep 결과 모두 포함
- **사용자 의도 모호 질문(예: "~는 어떻게 된거지?")은 부분 마이그레이션 누락 노출 신호** — 답변 전 grep 전수 검사 의무
- **타입 시그니처/zod 스키마 변경 시 호출처별 입출력 정합성 사전 검증 의무**

**Step 2 — 합리화 회피 (During 자동)**:
다음 표현이 머릿속에 떠오르면 **즉시 SSOT 위반/책임 회피 신호**로 판정:
- ❌ "이번엔 영향 작음" / "transient라 괜찮음"
- ❌ "Quick fix로 일단" / "나중에 정리"
- ❌ "caller가 항상 직접 호출하니" / "dead path니까"
- ❌ "단순 수정이라 검증 생략"

위 표현 시도 시 자동 차단 → 옵션 (A) 근본 해결 우선 검토. (C) Quick fix는 사용자 명시 승인 + 후속 task 등록 필수.

**Step 3 — 표준 검증 시나리오 (After 자동)**:
변경 종류별 최소 검증 시나리오. 통과 안 하면 작업 미완료.

| 변경 종류 | 표준 시나리오 |
|-----------|---------------|
| i18n / 다국어 | ① 정상 표시 ② 언어 전환 갱신 ③ **마운트 중 토글 자동 갱신** ④ 누락 키 0 |
| 폼 / zod 검증 | ① 정상 제출 ② 검증 실패 메시지 표시 ③ **서버 액션 재시도 atomicity** ④ 부분 실패 롤백 |
| 비동기 / Server Action / fetch | ① 정상 완료 ② **언마운트 중 취소 (`AbortController`/cleanup)** ③ 재진입 atomicity ④ 에러 경계 처리 |
| 리팩토링 / 시그니처 변경 | ① 호출처 grep 0건 ② **부수효과 매트릭스 등가성** ③ revert 안전 |
| 신기능 / API 라우트 추가 | ① 정상 호출 ② **null/empty/edge case** ③ 입력 zod 검증 ④ 인증/시크릿 boundary 격리 |

**Step 4 — 사용자 보고 시 시니어 판단 명시 (After 자동)**:
- 합리화 시도가 차단됐는지 명시
- 표준 검증 시나리오 통과 명시
- 트레이드오프 발생 시 헌법 §7 보고 적용
- "마운트 중 토글" 같은 핵심 시나리오는 별도 항목으로 가시화

### 1. SOLID 5원칙 (기본값 — 회색 지대는 트레이드오프 보고)

| 원칙 | 적용 기준 | 회색 지대 신호 |
|------|----------|---------------|
| **S**ingle Responsibility | 하나의 변경 이유만. 200줄 컴포넌트, 50줄 함수는 분리 검토 | "분리하면 호출 사슬만 길어지고 응집도가 떨어진다" — 그대로 두고 보고 |
| **O**pen/Closed | `if/switch` 타입 분기 3개 이상이면 Strategy/Discriminated Union 검토 | 분기가 2개 이하거나 추가 가능성이 없으면 분기 유지가 더 단순 |
| **L**iskov Substitution | 서브타입은 상위 계약을 깨지 않음. `as`/타입 가드 후 분기는 LSP 의심 | React 라이프사이클 자체가 LSP 깨는 사례 — 어쩔 수 없음 인정 |
| **I**nterface Segregation | 클라이언트가 안 쓰는 메서드를 인터페이스에 두지 않음 | 인터페이스 1개를 2개로 쪼개는 비용 > 이득이면 그대로 |
| **D**ependency Inversion | 구체 클래스 의존 금지. 함수 인자 주입 우선. 글로벌 싱글턴은 boundary에서만 | Next.js 서버/클라이언트 경계에서 모듈 import 자체가 boundary로 작동 — 인정 |

명백한 위반은 자체 거부 후 대안 제시. 회색 지대는 **"왜 이 트레이드오프를 선택했나" 한 줄 보고**로 충분.

### 2. SSOT (Single Source of Truth)

- **상태/규칙/식별자는 단 한 곳에서 정의**. 같은 데이터가 두 곳에 있으면 둘 중 하나는 derive(파생).
- 디스크/DB 저장이 따라오는 변경은 **단일 진입점 함수**로 통합 (예: `saveJob`, `markAnalysisComplete`).
- "단일 경로" 통합 시 **시점/관심사**까지 함께 묶이는지 검토 — 시점이 다른 관심사는 분리.
- 호출자 grep으로 **모든 진입점이 단일 SSOT를 거치는지** 확인 후 보고.
- 통합 후 **레거시 진입점은 반드시 제거** — 둘 다 살아있으면 SSOT가 아님.

#### 2-0. Caller-Driven UI String Snapshot 안티패턴 (자동 식별 의무)

UI가 caller로부터 string 결과를 받아 표시하는 패턴(`SetMessage(text)`, props로 번역된 텍스트 받기)은 **string snapshot이 SoT처럼 동작** → i18n SSOT 위반.

증상: UI 마운트 중 언어 변경 시 자동 갱신 안 됨. 다른 UI는 갱신되는데 caller-driven UI만 한국어/영어 혼재.

자동 의심 트리거:
- caller가 `t('key')` / 번역 함수 결과를 props로 전달
- 컴포넌트가 locale context 미구독
- 옛 props 시그니처 (`<Foo title={translatedTitle} />`)

해결 — **키 보존 + i18n 훅**:
- 컴포넌트가 `titleKey, titleArgs` props 보존
- 컴포넌트 내부에서 `useTranslation()` 또는 locale context 구독
- props 시그니처를 `titleKey: string, titleArgs?: Record<string, unknown>` 로 변경
- caller는 키만 전달

##### 2-0-1. 데이터 흐름 String Snapshot 절대 금지 (Layer-by-Layer 안티패턴 박멸)

**구조적 원인**: 데이터 흐름의 각 layer 마다 snapshot 이 생긴다.
```
DB Row → Domain.NameKey (key) → ViewModel.displayName (STRING ← snapshot 1)
       → Component props (text ← snapshot 2)
       → tooltip props.title (string ← snapshot 3)
```
한 layer 만 fix 하면 다음 layer 의 snapshot 이 안티패턴을 보존. 모든 layer 일괄 수정 의무.

**룰**:
1. **데이터 클래스/타입 (`*ViewModel`/`*RowData`/`*DTO`/`*Snapshot`) 는 사용자 노출 텍스트를 string 으로 보유 금지**. **키만** 보유 (`nameKey`, `descriptionKey`, `titleKey`).
2. **`t()` / `i18n.format()` 호출은 표시 직전 컴포넌트 내부에서만** (presentation boundary). API 응답·Server Component·ViewModel 에서 호출 후 string 필드에 박으면 안티패턴.
3. **사용자 노출 텍스트를 표시하는 모든 컴포넌트는 locale context 구독 의무** + 키 보존 props + 로케일 변경 시 표시 재계산. tooltip / 모달 / 동적 라벨 모두 포함.

**자동 검증 grep 패턴 (위임 시작 + 종료 시 의무)**:
```bash
# Pattern A — 데이터 타입에 string 텍스트 필드
grep -rE "(interface|type).*(ViewModel|DTO|Row).*\{" -A 30 | grep -E "(name|description|title|label):\s*string"

# Pattern B — t() 결과를 변수/필드에 박는 즉시 평가
grep -rE "(name|desc|description|title|label)\s*[:=]\s*t\("
```

**둘 다 0건 아니면 안티패턴 잔재** — 추가 sweep 필수. Pattern B 발견 시 컴포넌트가 직접 박제하는지 caller chain 추적 의무.

#### 2-1. 클래스/상태 불변식 캡슐화 — 양방향 검증 의무

setter나 함수가 **불변식을 자동으로 유지**하도록 만들 때(예: `isSelected=false → 자식 노드 disabled` 자동 동기화), **반대 방향도 항상 참인지 명시적으로 검증**한다:

- "한쪽 방향이 자동화되어 있으면 반대 방향도 자동화하면 자연스럽다"는 잘못된 직관
- 한쪽만 항상 참이면 **한쪽만 자동화** — 반대 방향은 호출자 컨텍스트(현재 선택된 항목인가? 등)가 필요해 모델이 알 수 없는 정보에 의존
- 양방향 자동화는 호출자 컨텍스트 누락 시 **두 단계 앞 부작용**을 만들기 쉬움
- 결정 시 다음 두 명제를 명시 검증: ① "X=true → Y" 는 항상 참인가? ② "X=false → ¬Y" 는 항상 참인가? 둘 다 참이 아니면 한쪽만 자동화

SSOT는 SOLID보다 양보 폭이 좁습니다. "두 곳에 같은 상태"는 거의 항상 버그.

### 3. 디자인 패턴 우선순위 (3회 반복 또는 확장 요구 명확 시에만)

| 상황 | 권장 패턴 |
|------|----------|
| 행동의 런타임 교체 | Strategy / Higher-order Function |
| 상태 전이 + 행동 변화 | State Machine / `useReducer` / XState |
| 객체 생성 분기 | Factory / Discriminated Union |
| 1:N 알림 | Observer / Event Emitter / Pub-Sub |
| 작업의 큐잉/Undo | Command / Optimistic Update |
| 알고리즘 골격 + 가변 단계 | Template Method / Render Props |
| 외부 시스템 격리 | Adapter / Facade (예: AI 클라이언트 추상화) |

**금기**: GoF 패턴 자체를 위한 패턴 적용 금지. **3회 반복** 또는 **확장 요구가 명확**할 때만 도입. 1·2회 반복은 인라인 유지가 더 단순.

### 4. 유지보수성 / 확장성 체크리스트

- [ ] **명명**: 의도가 드러나는 이름. `Manager`, `Helper`, `Util`, `Service` 같은 책임 모호한 접미사 지양
- [ ] **부수효과 가시화**: 시그니처에서 부수효과(저장, 이벤트 발행, 전역 상태 변경, 외부 API 호출)가 예측 가능한지
- [ ] **테스트 가능성**: 의존성 주입으로 단위 테스트 가능한 형태인지. `Date.now()`/`Math.random()`/`fetch`는 추상화
- [ ] **결정론**: RNG/시간/외부 호출은 명시 의존성 주입. 테스트에서 mock 가능해야 함
- [ ] **삭제 용이성**: 기능 제거 시 영향 파일이 5개 이하로 국소화되는지
- [ ] **서버/클라이언트 경계**: Next.js App Router에서 `'use client'` 경계가 명확한지. 직렬화 불가능한 객체가 boundary 넘는지 검증
- [ ] **순수 함수 단위 테스트 검토**: 외부 의존성 없는 순수 함수는 테스트 작성 검토. 강제는 아니지만, 불변식이나 상태 전이를 다루는 코드는 테스트가 회귀 방지 비용 대비 가치가 큼.

### 5. 오버엔지니어링 안티패턴 (적극 회피)

원칙을 적용한다는 명분으로 다음을 만들면 헌법 위반:

- **사용처 1곳뿐인 인터페이스/추상 클래스** — 모킹 의도가 명확하지 않으면 구체 타입으로 충분
- **확장 가능성 추측에 기반한 패턴 도입** — "나중에 늘어날 수도 있으니 Strategy 미리 깔자" 금지. 늘어날 때 도입.
- **5줄 함수를 3개로 쪼개기 / DI 컨테이너 도입** — SRP 위반 신호 없으면 인라인. 함수 인자 수동 주입으로 충분.
- **이벤트 남발** — 호출 사슬이 명확한 1:1 호출은 직접 호출이 디버깅에 유리
- **Context 남발** — 정말 글로벌한 것(테마·로케일·인증)에만. 컴포넌트 트리 한정 데이터는 props 또는 컴포지션으로
- **`useEffect` 남용** — 데이터 페칭은 서버 컴포넌트, 파생 상태는 렌더 중 계산. `useEffect`는 외부 시스템 동기화에만
- **헌법 검증 단락을 형식적으로 채우기** — 위반/트레이드오프 없으면 단락 자체를 생략

YAGNI(You Aren't Gonna Need It)가 SOLID보다 우선하는 경우가 자주 있음.

**Dead Path 우선 검증 의무**: 마이그레이션 대상 발견 시 **사용처 grep으로 dead path 가능성 우선 검증** — 제거 옵션을 마이그레이션보다 먼저 검토.

### 6. Escape Hatch (헌법 완화 허용 상황)

다음 컨텍스트에서는 헌법을 완화합니다 — 단, 보고에 **"이건 X이므로 헌법 완화 적용"** 명시:

- **프로토타입/PoC/스파이크**: 동작 검증이 목적, 폐기 예정 코드. SOLID 강제 = 비용 낭비
- **긴급 hotfix**: 운영 중단 복구 우선, 리팩토링은 후속 PR
- **외부 API 미러링**: 3rd-party SDK(OpenAI, Gemini 등) 형태를 그대로 따라야 하는 어댑터 코드
- **타입/DTO**: getter/setter만 있는 데이터 타입은 SOLID 평가 대상 아님
- **마이그레이션 스크립트**: 1회성 실행 코드, 빠른 작성 우선

### 7. 보고 정책 (양식주의 회피)

- **위반/트레이드오프가 없으면 별도 헌법 단락 생략**. 평소 보고는 평소대로 간결하게.
- **위반/회색 지대 발생 시에만** 다음 한 줄 추가:
  ```
  ## 트레이드오프
  [어느 원칙을 / 어떻게 양보했는가 / 왜]
  ```
- **명백한 SOLID/SSOT 위반은 보고하지 말고 자체 수정** 후 결과만 보고
- 보고에 패턴/원칙 이름을 나열하는 것보다 **"이 코드가 6개월 뒤 누가 봐도 변경 가능한가"**를 자가 점검

### 8. 장기 회고 메커니즘 (세션 휘발 방지)

세션 안에서 발견한 **회귀/실수 패턴**(예: 양방향 불변식 잘못 정의, SSOT 위반 누락)이 다음 세션에 전달되지 않으면 같은 실수가 반복됩니다. 휘발 방지를 위해:

- 한 세션에서 **회귀가 1회 이상 발생**했거나 **사용자가 시니어 검토자 역할로 잡아낸 약점**이 있으면, 세션 종료 직전 `/reflect` 스킬을 호출 권장
- `/reflect`는 `reflection-curator` 에이전트를 호출해 인사이트를 `.claude/` 또는 `best-practice/`에 박제할지 사용자에게 확인 후 적용
- 박제 대상 우선순위: ① 회귀 케이스 ② 헌법으로 잡지 못한 실패 패턴 ③ 위임 비용/가치 ROI 데이터
- 회고가 박제되지 않은 채 세션이 끝나면, "사용자가 다음 번에 같은 지적을 또 해야 함" — 이건 헌법 §0 메타 원칙 위반(사용자에게 부담 떠넘김)

### 참고

- [best-practice/refactoring-lessons.md](../../best-practice/refactoring-lessons.md) — 일반 리팩토링 교훈
- [best-practice/evidence-based-debugging.md](../../best-practice/evidence-based-debugging.md) — 증거 기반 디버깅 4단계 프로토콜
- [best-practice/reflection-protocol.md](../../best-practice/reflection-protocol.md) — 세션 인사이트 반영 프로토콜
- [.claude/rules/web-delegation.md](web-delegation.md) — 웹 위임 규칙
- [.claude/rules/evaluation.md](evaluation.md) — 평가 주도 검증
