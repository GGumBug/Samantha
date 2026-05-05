[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 증거 기반 디버깅 프로토콜 (Evidence-Based Debugging)

정적 분석만으로 원인 특정이 불가능할 때, **런타임 증거를 수집·분석해서 단일 원인을 지목하고 최소 수정**하는 4단계 프로토콜. 반복된 방어적 수정으로 사용자 시간을 낭비하지 않기 위한 규약.

## 배경 (도출 경위)

게임 프로젝트의 진행 중 상태 복원 버그 해결 과정에서 확립. 초기 몇 번의 "방어적" 수정이 모두 실패했고, 사용자 요청으로 로그 기반 접근으로 전환한 뒤 **1줄 제거**로 단번에 해결. 증거 없이 가설에 의존한 수정이 얼마나 비효율적인지 입증한 사례. 웹 프로젝트에도 동일한 원리가 적용됩니다.

## 4단계 프로토콜

### 1단계 — 진단 로그 삽입

정적 분석으로 원인을 좁히지 못한 경우 **임시 `console.log`/`console.error`** 로 런타임 데이터 관찰:

- 공통 prefix 사용 (예: `[XXX-DIAG]`) — 콘솔 필터링 용이
- **실제 데이터 값 출력** — "호출됐다" 수준이 아니라 `snapshot.id`, `phase`, 플래그 값 등을 직접 출력
- 5~10개 key 분기점만 삽입, 과용 금지
- 저장·로드·상태 전환 전/후 각각 찍기 (체인 추적)
- 서버 컴포넌트/API 라우트는 `console.error` (서버 로그), 클라이언트는 `console.log` (브라우저 DevTools)

### 2단계 — 사용자 재현 + 로그 수집

- 재현 절차를 **명확한 단계**로 제시 (1~6 step 형식)
- 사용자가 브라우저 DevTools Console / 서버 터미널에서 prefix 필터링 후 **전체 복사**해 공유
- 네트워크 탭의 요청/응답이 도움 되는 경우 함께 요청
- AI는 여기서 대기 — 가설에 따른 추가 수정 금지

### 3단계 — 원인 매트릭스 사전 정의 + 단일 원인 지목

로그 **받기 전에** 예상 패턴별 대응을 매트릭스로 문서화:

| 관찰 로그 | 해석 | 수정 방향 |
|---------|------|---------|
| A 값 undefined | X 경로 누수 | Y 지점 수정 |
| B 불일치 | Z timing | W 재설계 |
| ... | ... | ... |

사용자 로그 수신 후 매트릭스에서 정확한 행을 지목 → **단일 원인 확정**.

### 4단계 — 최소 수정 + 로그 전수 제거

- 특정된 원인에 대한 **최소 범위** 수정 (1~5줄 선호)
- 방어적 확장 금지 (관련 없는 코드 안 건드림)
- 진단 로그 **전수 제거** (`grep -rn "\[XXX-DIAG\]" src` 결과 0 확인)
- 임시 변수(`_diag*` 등)도 함께 정리

## 안티패턴 경고

### "해결됐다" 성급한 선언
정적 분석 후 수정하고 곧장 "해결됐다"고 결론내기. **증거 없이 선언하는 순간 사용자 신뢰 손상**. 대안:
- 브라우저 재현 결과 공유 요청 후에만 성공 확정
- "예상 동작"과 "검증된 동작"을 명확히 구분
- 타입 컴파일/lint 통과 ≠ 동작 정확성

### 방어적 확장 수정
"혹시 모르니 여기도 고치자" 식으로 범위 넓히기. 위험:
- 다른 기능에 회귀 유발 (예: 가드 분기 추가가 정상 플로우 막음)
- 원인이 다른 곳에 숨어있으면 계속 못 잡음

대안: **증거 기반 단일 수정**. 로그에 보이지 않은 것은 건드리지 않음.

### 같은 가설 2회 이상 실패
같은 가설로 두 번 수정했는데 증상 남으면 **즉시 가설 폐기**. 로그 수집으로 전환.

> 사례: GaugeMeter 시각 버그 — "viewBox 잘림" 가설로 1차/2차 fix 모두 실패. 진짜 원인은 SVG `large-arc-flag` 로직 오류였음. 같은 layer를 두 번 의심한 순간 다른 layer(path 명령 인자)로 즉시 전환했어야 함.

### 영구 로깅 방치
진단 로그를 제거하지 않고 방치 → 프로덕션 콘솔 스팸. SRP 위반.
- 수정 완료 직후 `grep` 전수 확인
- 임시 변수도 함께 정리
- TS 컴파일러는 `console.log`를 경고하지 않으므로 의식적 grep 필수

## 시각/데이터 swap 사고 시 데이터 Layer 격리 우선

UI에 **잘못된 텍스트/이미지가 swap 표시**되는 사고(예: 다른 항목의 데이터 표시, 라벨 swap)는 **컴포넌트 props/CSS 정합 검증보다 데이터 origin 격리 진단 로그가 빠르다**. 정적 분석은 시각 layer 가설(컴포넌트 명명, key prop, 위치 swap)에 시간을 낭비시킨다.

**진단 우선순위 역전 규칙**: 컴포넌트 트리 분석 + key prop 검증 + CSS 위치 검증을 시도하기 전에, **데이터 흐름 layer마다 `console.log`를 찍어 잘못된 데이터가 어느 layer에서 진입했는지 격리**하라.

### 4-Layer 진단 로그 템플릿

```typescript
// Layer 1 — Source (DB/API → 서버 응답)
console.log(`[X-DIAG][L1] id=${id} name=${data.name} desc=${data.description}`);

// Layer 2 — Carrier (서버 → 클라이언트 boundary, 직렬화)
console.log(`[X-DIAG][L2] hover boundary id=${target.id} key=${target.key}`);

// Layer 3 — Display (컴포넌트 props 시점)
console.log(`[X-DIAG][L3] set name=${nameKey} desc=${descKey}`);

// Layer 4 — Final (DOM에 박힌 최종 string)
console.log(`[X-DIAG][L4] final txtName=${nameRef.current?.textContent}`);
```

L1에서 이미 swap 발견 → DB/API 마이그레이션 버그 (코드 무죄). L3에서 swap 발견 → 컴포넌트 props 전달 버그. L4까지 정합인데 시각 swap → 그제서야 CSS/레이아웃 의심.

### 사용자 시니어 검토자 신호 패턴

사용자가 다음 형태로 개입하면 **컴포넌트/CSS 의심 차단 + 데이터 origin 격리 지시 신호**:

- "컴포넌트는 문제없으니 X 의심말고 Y 디버그 찍어"
- "관련없는 Z 데이터가 W에 뜨는데 버그 이유 추적"
- "API 응답 검증 완료, 다음 layer 확인"

이 신호 수신 시 즉시 정적 분석 중단 + 4-layer 진단 로그 모드로 전환. 사용자가 시각 layer 정합을 이미 confirm한 상태이므로 **데이터 흐름만 의심**.

## SVG 시각 버그 진단 — "잘림" 표현은 다층 원인

SVG 컴포넌트에서 사용자가 "잘림", "이상함", "찌그러짐" 으로 신고한 시각 버그는 **viewBox 단일 의심 금지**. 같은 시각 증상이 최소 4개 layer에서 발생한다.

### SVG 시각 버그 4-Layer

| Layer | 원인 | 의심 신호 |
|-------|------|----------|
| L1 — viewBox / 좌표계 | viewBox 범위 좁음, transform 잘못 | 일부만 보이고 명확한 직사각형 경계 |
| L2 — path 명령 인자 (d 속성) | `large-arc-flag`, `sweep-flag`, M/L/A 좌표 오류 | 호(arc)가 반대 방향으로 그려짐, 곡선이 끊김 |
| L3 — stroke / fill / opacity | stroke-width 0, fill='none' + stroke 누락 | 좌표 정확하지만 화면에 안 보임 |
| L4 — CSS 변환 / 부모 컨테이너 | overflow:hidden, transform:scale, 부모 width 0 | 다른 환경에선 정상, 특정 컨테이너에서만 깨짐 |

### 정공법 — path 명령 인자 전수 검증 의무

SVG path의 **모든 시그니처 인자**를 한 번에 검증한다. 좌표만 검증하면 flag 회귀를 놓친다.

```
A rx ry x-axis-rotation large-arc-flag sweep-flag x y
```

`large-arc-flag` (0|1), `sweep-flag` (0|1) 같은 boolean 인자도 **단위 테스트의 명시 케이스**가 되어야 한다. 좌표 검증만으로는 다음을 못 잡는다:
- 호의 진행 방향이 반대 (sweep-flag)
- 작은 호 vs 큰 호 swap (large-arc-flag)
- 동일 좌표 + 다른 flag → 시각만 다름

### SVG 작업 체크리스트

- [ ] viewBox 의심 전에 path d 속성 인자 전수 print → 시각 검토
- [ ] arc(A) 명령 사용 시 large-arc-flag·sweep-flag 단위 테스트 케이스 명시
- [ ] 각 layer(viewBox / path 인자 / stroke / 부모 CSS) 격리 의심
- [ ] **사용자 시각 검토 회귀 2회 이상 발생 시 layer 전환 의무** (같은 layer 3회 의심 금지)
- [ ] 우회 금지: "viewBox만 늘리면 일단 보임" 식 합리화 차단 — 진짜 원인 명시 후 수정

## 프로토콜 체크리스트

- [ ] 진단 로그 prefix 통일 (`[XXX-DIAG]`)
- [ ] 실제 데이터 값 출력 (not "호출됨")
- [ ] 5~10개 key 분기점만
- [ ] 재현 절차 명시 (1~6 step)
- [ ] 원인 매트릭스 **로그 받기 전** 사전 정의
- [ ] 단일 원인 지목 후 최소 수정
- [ ] 진단 로그 전수 제거 (grep 0)
- [ ] 임시 변수 정리
- [ ] **시각 swap 사고 — 컴포넌트 의심 전 데이터 layer 4단 로그 우선**
- [ ] **사용자 "X 의심말고 Y 보라" 신호 시 정적 분석 즉시 중단**

## 웹 환경 추가 도구

- **브라우저 DevTools**: Network 탭(요청/응답), Performance 탭(렌더 추적), React DevTools(컴포넌트 트리·state)
- **Server logs**: Next.js dev 서버 출력, Vercel 배포 환경의 functions log
- **브라우저 자동화 MCP**: Claude in Chrome / Chrome DevTools MCP로 Claude가 직접 콘솔 로그 수집 가능
- **소스맵**: 프로덕션 디버깅 시 sourcemap 활성화로 원본 줄번호 추적
