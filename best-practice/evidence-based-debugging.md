[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 증거 기반 디버깅 프로토콜 (Evidence-Based Debugging)

정적 분석만으로 원인 특정이 불가능할 때, **런타임 증거를 수집·분석해서 단일 원인을 지목하고 최소 수정**하는 4단계 프로토콜. 반복된 방어적 수정으로 사용자 시간을 낭비하지 않기 위한 규약.

## 배경 (도출 경위)

Hwaseo 2026-04-17 Encounter resume 버그 해결 과정에서 확립. 초기 몇 번의 "방어적" 수정이 모두 실패했고, 사용자 요청으로 로그 기반 접근으로 전환한 뒤 **1줄 제거**로 단번에 해결. 증거 없이 가설에 의존한 수정이 얼마나 비효율적인지 입증한 사례.

## 4단계 프로토콜

### 1단계 — 진단 로그 삽입

정적 분석으로 원인을 좁히지 못한 경우 **임시 Debug.Log**로 런타임 데이터 관찰:

- 공통 prefix 사용 (예: `[XXX-DIAG]`) — 콘솔 필터링 용이
- **실제 데이터 값 출력** — "호출됐다" 수준이 아니라 `snapshot.EncounterId`, `phase`, 플래그 값 등을 직접 출력
- 5~10개 key 분기점만 삽입, 과용 금지
- 저장·로드·상태 전환 전/후 각각 찍기 (체인 추적)

### 2단계 — 사용자 재현 + 로그 수집

- 재현 절차를 **명확한 단계**로 제시 (1~6 step 형식)
- 사용자가 Unity 콘솔에서 prefix 필터링 후 **전체 복사**해 공유
- AI는 여기서 대기 — 가설에 따른 추가 수정 금지

### 3단계 — 원인 매트릭스 사전 정의 + 단일 원인 지목

로그 **받기 전에** 예상 패턴별 대응을 매트릭스로 문서화:

| 관찰 로그 | 해석 | 수정 방향 |
|---------|------|---------|
| A 값 NULL | X 경로 누수 | Y 지점 수정 |
| B 불일치 | Z timing | W 재설계 |
| ... | ... | ... |

사용자 로그 수신 후 매트릭스에서 정확한 행을 지목 → **단일 원인 확정**.

### 4단계 — 최소 수정 + 로그 전수 제거

- 특정된 원인에 대한 **최소 범위** 수정 (1~5줄 선호)
- 방어적 확장 금지 (관련 없는 코드 안 건드림)
- 진단 로그 **전수 제거** (grep 결과 0 확인)
- 임시 변수(`_diag*` 등)도 함께 정리

## 안티패턴 경고

### "해결됐다" 성급한 선언
정적 분석 후 수정하고 곧장 "해결됐다"고 결론내기. **증거 없이 선언하는 순간 사용자 신뢰 손상**. 대안:
- 에디터 테스트 결과 공유 요청 후에만 성공 확정
- "예상 동작"과 "검증된 동작"을 명확히 구분

### 방어적 확장 수정
"혹시 모르니 여기도 고치자" 식으로 범위 넓히기. 위험:
- 다른 기능에 회귀 유발 (Hwaseo에서 `TryResumePendingEncounter`에 IsEnded 조건 추가 → r-3 회귀)
- 원인이 다른 곳에 숨어있으면 계속 못 잡음

대안: **증거 기반 단일 수정**. 로그에 보이지 않은 것은 건드리지 않음.

### 같은 가설 2회 이상 실패
같은 가설로 두 번 수정했는데 증상 남으면 **즉시 가설 폐기**. 로그 수집으로 전환.

### 영구 로깅 방치
진단 로그를 제거하지 않고 방치 → 프로덕션 로그 스팸. SRP 위반.
- 수정 완료 직후 `grep` 전수 확인
- 임시 변수도 함께 정리

## 사례 — Hwaseo Encounter Resume (2026-04-17)

**증상**: 진행 중 encounter 강제 종료 → 재접속 → 다른 encounter 표시

**실패한 추측 수정 (2회)**:
1. `TryResumePendingEncounter`에 `IsEnded=true` 방어 분기 → r-3(같은 노드 재클릭) 회귀 유발
2. "Encounter 시작 시 bookmark save" 추가로 "해결됐다" 선언 → 실제 재현 테스트에서 여전히 다른 encounter

**증거 기반 재접근**:
- `[SnapshotChain-DIAG]` 13개 지점 로그 삽입
- 사용자 콘솔 공유 → `AFTER SaveCurrentData: EncId=encounter_07` 있음 but `TryResume ENTER: EncId=NULL` → **저장과 로드 사이 clear 발생 증명**
- 원인 매트릭스에서 "LOAD 성공 but TryResume NULL" = 로드 후 `ClearPendingEncounter` 호출자 존재
- 단일 수정: `GameScene.StartEncounter` 가드의 `&& snapshot.IsEnded` **1줄 제거**
- 로그 12건 전수 제거 (grep 0 확인)

## 사례 — Hwaseo btnMap SSOT race fix + AudioManager NRE (2026-05-12)

race / lazy-init / Singleton 라이프사이클 의심 시 4단계 프로토콜 완주 사례.

**observe**:
- 사용자 보고 #1: Battle/Boss/Elite 노드 진입 시 btnMap 활성화 안 됨
- 사용자 보고 #2: btnMap 클릭 시 AudioManager.PlayEffect NRE

**hypothesize**:
- H1a (btnMap): UIGame.OnEnable 시점에 `BattleManager.HasInstance=false` → 가드 통과 실패 → 구독 영구 누락
- H1b (AudioManager): Singleton 인스턴스 교체 race — Setup 호출 인스턴스 ≠ PlayEffect 호출 인스턴스

**verify (진단 로그)**:
- `[BTNMAP-DIAG] OnEnable enter | HasInstance(before)=?` 로 race 시점 상태 캡쳐
- `[AUDIO-DIAG] Init/Setup/PlayEffect | InstanceID=?` 로 인스턴스 교체 검증
- Editor.log 시퀀스를 사용자 → Claude 전달

**result**:
- H1a 확정: `HasInstance(before)=False` 로그 출력 → 실제 race 발생 evidence
- H1b 폐기: `InstanceID=-120158` 단일 일관 → Singleton 교체 없음, 일회성 race 추정

**fix**:
- btnMap: `Instance` getter 직접 호출 (lazy init 트리거) → race 해소
- AudioManager: Phase A defensive 가드 (Database null 체크) → NRE 차단

**cleanup**:
- 진단 로그 14개 라인 제거 (병렬 위임 Sonny+Jarvis)
- Phase A 가드는 안전망으로 보존

### race / lazy-init / Singleton 라이프사이클 의심 시 표준 패턴

1. `[XXX-DIAG]` prefix 진단 로그
2. `GetInstanceID()` + `HasInstance(before)=?` 형태로 **race 발생 시점 상태** 직접 캡쳐
3. Editor.log 시퀀스를 사용자 → Claude 로 전달해 evidence 확정
4. fix 후 재진단으로 정상 시퀀스 확인 + 진단 로그 제거

## 시각 표시 사고 시 데이터 Layer 격리 우선

UI에 **잘못된 텍스트/이미지가 swap 표시**되는 사고(예: 상단/하단 라벨 swap, 다른 entity의 데이터 표시)는 **prefab/SerializeField/RectTransform 정합 검증보다 데이터 origin 격리 진단 로그가 빠르다**. 정적 분석은 시각 layer 가설(GameObject 명명, fileID, 위치 swap)에 시간을 낭비시킨다.

**진단 우선순위 역전 규칙**: prefab YAML 분석 + RectTransform 위치 + SerializeField fileID 검증을 시도하기 전에, **데이터 흐름 layer마다 Debug.Log를 찍어 잘못된 데이터가 어느 layer에서 진입했는지 격리**하라.

### 4-Layer 진단 로그 템플릿

```csharp
// Layer 1 — Source (시트/자산 → 도메인)
Debug.Log($"[X-DIAG][L1] id={id} name={data.Name} desc={data.Description}");

// Layer 2 — Carrier (도메인 → UI 전달 boundary)
Debug.Log($"[X-DIAG][L2] hover boundary id={target.Id} key={target.Key}");

// Layer 3 — Display (View 내부 set 시점)
Debug.Log($"[X-DIAG][L3] set name={nameKey} desc={descKey}");

// Layer 4 — Final (TextMeshPro에 박힌 최종 string)
Debug.Log($"[X-DIAG][L4] final txtName={_txtName.text} txtDesc={_txtDesc.text}");
```

L1에서 이미 swap 발견 → 시트/자산 마이그레이션 버그 (코드 무죄). L3에서 swap 발견 → UI set 코드 버그. L4까지 정합인데 시각 swap → 그제서야 prefab 정합 의심.

### 사용자 시니어 검토자 신호 패턴

사용자가 다음 형태로 개입하면 **prefab/코드 의심 차단 + 데이터 origin 격리 지시 신호**:

- "프리팹은 문제없으니 X 의심말고 Y 디버그 찍어"
- "관련없는 Z 데이터가 W에 뜨는데 버그 이유 추적"
- "데이터 임포트 검증 완료, 다음 layer 확인"

이 신호 수신 시 즉시 정적 분석 중단 + 4-layer 진단 로그 모드로 전환. 사용자가 시각 layer 정합을 이미 confirm한 상태이므로 **데이터 흐름만 의심**.

(2026-04-30 카드 swap 사고: 본 세션이 prefab YAML / RectTransform / fileID 검증에 시간 소비 → 사용자가 "디버그 찍어" 명시 → 즉시 시트 데이터 layer (skill.0201 name 위치에 desc 텍스트) origin 확정. 본 세션 시니어 검토자 개입 4건 누적 — Encounter L10n + 카드 swap + Effect tooltip 외)

## 실패 메시지 오독 — 기대값 위치의 이상값은 "수집 범위 오류" 신호

단언 실패의 **기대값/실제값 위치에 관측 대상이 아닌 값**이 등장하면, 로직 오류보다 **관측 코드의 수집 범위 오류**를 먼저 의심한다.

- **감별 신호**: 여러 케이스가 **전부 같은 방향으로 같은 크기만큼** 어긋나면 수집 범위 오류. 로직 버그는 케이스마다 다르게 깨지지만, 수집 범위 오류는 전 케이스에 균일하게 상수로 얹힌다
- **실측**: 행 필터가 `name.StartsWith("Line")` 인데 헤더 오브젝트 이름이 `LinesHeader` — 접두사 근사가 헤더까지 수집해 4개 케이스가 전부 "기대 3행 vs 실제 4행"으로 실패. 실패 메시지만 보고 "정렬 오류"로 오독해 정렬 로직을 먼저 뒤졌다
- **처방**: 이름 규약에 의존하는 관측은 **접두사 근사 금지** — 정확 일치 집합, 전용 태그/마커 컴포넌트, 또는 컨테이너 자식 범위로 한정한다. 이름 규약은 사람을 위한 것이고 관측 필터의 계약이 아니다

(2026-07-28 Double Down HUD 라인 테스트)

## 노출 창 마스킹 — 버그가 버그를 가린다

버그 A 가 버그 B 의 **노출 창을 좁혀** B 를 잠복시키는 경우가 있다. A 를 고치면 B 가 발현한다 — 이때 B 를 "A 수정이 만든 신규 회귀"로 단정하고 A 를 롤백하면 증상만 다시 숨고 구조는 그대로 남는다. ([refactoring-lessons.md](refactoring-lessons.md) §7 "두 버그가 서로를 가리는 경우"의 반대 방향 — §7 은 *수정 효과가 안 보이는* 쪽, 여기는 *결함이 안 보이는* 쪽)

### 판별 1 — fix 직후 새 증상은 롤백 전에 코드 경로를 대조한다

1. 이번 fix 의 **변경 파일 목록** 확보 (`git diff --stat`)
2. 새 증상을 만드는 **판정식·대입 지점**을 grep 으로 특정 (예: 정렬 순서가 틀렸다면 해당 값을 대입하는 지점 전수)
3. 두 집합의 **교집합이 0건이면 잠복 해제** — B 를 독립 결함으로 등록하고 A 의 fix 는 유지

**경계 케이스(중요)**: fix 가 값이 아니라 **체류 시간·순서·빈도**만 바꿨다면(홀드 추가, 대기 삽입, 순서 교체) 교집합이 있어도 잠복 해제 쪽이다 — 관측 창을 넓힌 변경이기 때문. 이 경우 fix 를 되돌리면 증상이 사라지지만 **그것은 무죄 증거가 아니다**. 되돌림으로 증상이 사라졌다는 사실만으로 원인을 확정하지 말 것.

### 판별 2 — 사용자의 "간혹"을 확률로 읽지 않는다

"간혹" / "가끔 그럼"은 확률적 버그 신호이기도 하지만, **다른 버그가 노출 창을 조절 중**일 가능성을 먼저 배제한다.

배제 방법 — **창을 인위적으로 넓혀본다**: 대기 삽입, 재생 속도 감소, 홀드 추가. 창을 넓혔을 때 **재현율이 100% 로 붙으면 확률이 아니라 창 문제** — 구조적으로 상시 존재하는 결함이다. 재현율이 그대로 낮게 유지되면 그때 확률·경합을 의심한다([measurement-driven-debug.md](measurement-driven-debug.md) 샘플 N≥100).

(2026-08-04 Double Down 카드 연출: 레이어 역전(뜸 중 카드가 더미 뒤로 숨음)은 상시 존재했으나 **다른 버그가 카드를 먼저 치워** 창이 짧아 "간혹"으로 보고됨. 앞 버그를 고쳐 체류 시간이 늘자 상시 재현)

## 프로토콜 체크리스트

- [ ] 진단 로그 prefix 통일 (`[XXX-DIAG]`)
- [ ] 실제 데이터 값 출력 (not "호출됨")
- [ ] 5~10개 key 분기점만
- [ ] 재현 절차 명시 (1~6 step)
- [ ] 원인 매트릭스 **로그 받기 전** 사전 정의
- [ ] 단일 원인 지목 후 최소 수정
- [ ] 진단 로그 전수 제거 (grep 0)
- [ ] 임시 변수 정리
- [ ] **시각 swap 사고 — prefab 의심 전 데이터 layer 4단 로그 우선**
- [ ] **사용자 "X 의심말고 Y 보라" 신호 시 정적 분석 즉시 중단**
- [ ] **전 케이스가 균일하게 어긋나면 로직 아닌 관측 수집 범위 먼저 의심**
- [ ] **fix 직후 새 증상은 롤백 전에 코드 경로 교집합 대조** (잠복 해제 vs 신규 회귀)
