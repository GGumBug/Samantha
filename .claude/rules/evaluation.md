# Glob: **/*.{ts,tsx,js,jsx,py,go,rs,java,cs}

## 평가 주도 검증 (Evaluation-Driven Verification)

코드를 작성한 후 반드시 검증 단계를 거친다:

1. **테스트 실행**: 관련 테스트가 있으면 반드시 실행하고 결과를 보고한다
2. **UI 변경 시**: 브라우저에서 직접 확인한다. 타입 체크와 테스트는 기능 정확성을 보장하지 않는다
3. **자기 평가 금지**: 코드를 작성한 직후 "잘 되었다"고 선언하지 않는다. 실행 결과로 증명한다
4. **교차 검증 권장**: 복잡한 변경은 `/simplify`나 별도 서브에이전트로 독립 리뷰한다

## 검증 루프 — 안쪽은 CLI, 바깥쪽은 배치 (2026-09-14)

Unity 프로젝트의 검증은 **두 겹**이다. 안쪽을 건너뛰면 느리고, **바깥쪽을 건너뛰면 총계를 잃는다**.

| 겹 | 도구 | 언제 | 무엇을 준다 |
|---|---|---|---|
| **안쪽** | `unity command recompile` → `recompile_status` → `run_tests --filter <픽스처>` | 편집할 때마다 | 초 단위. Unity **진짜** 컴파일러의 오류 배열. 좁혀 실행 |
| **바깥쪽** | `bash tools/ddtest.sh` (+ PlayMode) | **커밋 직전** · 뮤테이션 검증 | 전량 총계. 에디터 없이도 돈다 |

```bash
unity status                                   # 없으면 안쪽은 건너뛰고 그 사실을 말한다
unity command set_autotick --enable true       # 필수 — 포커스 잃은 에디터는 recompile을 멎춘다
# (.cs 편집)
unity command recompile && unity command recompile_status   # failed=true 면 errors 배열을 읽는다
unity command run_tests --mode editor --filter DoubleDown.Application.Tests.ShopBonusPackTests
unity command run_tests --mode playmode --async_tests   # PlayMode는 이 길뿐. test_status로 폴링
bash tools/ddtest.sh                           # 커밋 전 전량 — 총계 비교는 여기서만
```

**왜 바깥쪽을 못 버리는가** — 셋이다. ⓐ 우리 규율이 **총계 비교**(예: 1302 → 1303)인데 `--filter`는
총계를 못 낸다. ⓑ `run_tests`는 실패 시 **결과가 불투명할 수 있다**(패키지 스킬의 명시 경고) — 좁은
필터로 재실행하거나 Test Runner를 봐야 한다(그 불투명이 어떤 모습인지는 아래 「두 겹의 success」).
ⓒ 에디터가 Safe Mode·부재일 때 안쪽이 통째로 없다.

**`dotnet build`는 이제 2순위다.** 그쪽은 Unity 밖 **대리** 컴파일이라 asmdef·define을 근사할 뿐이고,
`recompile`은 에디터가 실제로 쓰는 컴파일러다. 에디터가 없을 때만 `dotnet build`로 내려간다.

**뮤테이션 검증은 바깥쪽에서** — 주입·원복이 파일 단위이고 판정 근거가 "총계 중 몇 건이 빨간불인가"라
필터 실행으로는 그 판별력이 나오지 않는다.

### 도구가 초록이라고 말할 때 — 두 겹의 success (2026-09-14)

응답에는 **success가 둘** 있다. 바깥은 *명령이 전달됐는가*이고, `data.result.success`가 *일이
됐는가*다. 두 겹을 구별하지 않으면 도구가 정직하게 말한 실패가 초록으로 보인다.

- **`data.result.success` / `data.result.error`를 `Summary`보다 먼저 읽는다.** 결과 파서를 직접
  쓸 때 `Summary`만 올리면 안쪽 실패 사유를 통째로 건너뛴다
- **`Total == 0`은 통과가 아니라 실패다.** 아무것도 안 돌았다는 뜻이고, 필터 오타의 유일한 증상이다
- **`--filter`에는 네임스페이스를 전부 적는다** — 픽스처 이름만 적으면 매칭이 0건이다

실측 2건(같은 계급의 거짓 초록): ⓐ `--filter "ShopBonusOfferDisplayTests"`(네임스페이스 누락) →
`{"Summary":{"Total":0,...},"success":true}` — 아무것도 안 돌았는데 통과로 읽힌다. ⓑ `run_tests
--mode play` → 바깥 `success: true`, `Summary.Total: 0`, 진짜 사유는 `data.result.error`에 숨어
있었다: *"PlayMode tests cannot run synchronously over HTTP: entering play mode triggers a domain
reload that drops the request."*

**PlayMode는 비동기로만 돈다.** `--mode playmode --async_tests` 후 `test_status` 폴링이 유일한
경로다. 장시간 실행용 선택지가 아니다. `test_status`의 `data.result`는 객체가 아니라 **JSON
문자열**(`"{\"status\":\"running\"}"`)이라 이스케이프된 따옴표 때문에 `grep '"running"'` 류 폴링이
1회 만에 빠져나간다. 파싱한 뒤 판정한다.

**폴링 술어는 긍정형으로 쓴다.** "compiling이 아니면 끝" 같은 부정형은 **응답 자체가 없는
구간**(도메인 리로드 중 서버 단절)을 완료로 통과시킨다. 완료 상태를 명시로 확인하고, 무응답은
완료가 아니라 재시도다.

## 테스트 작성자 / 구현자 분리 (기본값)

테스트 작성은 **구현자와 다른 에이전트에 위임**한다. 메커니즘: 테스트 작성자는 소비자 시점으로 코드를 역추적하므로 구현자의 사각지대를 구조적으로 통과한다.

(2026-07-08 GameCore PoolService 실증: 구현 Jarvis, 테스트 작성 Sonny로 분리했다. Sonny가 "Dispose 후 체크아웃된 인스턴스는 누가 치우나?" 시나리오를 역추적하다 실결함을 찾았다. Dispose가 풀 대기 인스턴스만 파괴하고 체크아웃 인스턴스는 entry만 폐기해, Release가 ObjectDisposedException을 내고 회수 경로가 사라진다. 루트 수명에선 잠복, 씬-스코프 컨테이너에선 실누수)

### 검증자는 기대 시나리오도 의심한다 (코디네이터 명세 오류 검출)

코디네이터가 위임 프롬프트에 제시한 **기대 시나리오 자체가 틀릴 수 있다**. 검증자는 실동작이 기대와 다를 때 맹종해 고치지 않는다. ① 실동작을 동결 케이스로 확보 ② 룰·스펙 원문 대조 ③ 코디네이터·사용자에게 스펙 확인 요청 ④ 원래 의도 검증용 깨끗한 케이스 별도 구성. [unity-delegation.md](unity-delegation.md) "범위 보존 ≠ 맹종"의 검증자 측 확장.

(2026-07-20 실증: 코디네이터 기대 "홍단+청단+피10 → 3라인"이 룰상 틀림 — 띠 6장이라 hand_tti 동시 성립 → 4라인. Sonny가 실동작 동결 + 스펙 확인 요청 + 깨끗한 3라인 케이스 별도 구성)

## 실행 불가 산출물은 참조 실재를 grep으로 확인 (타입 환각 방지)

**실행되지 않은 테스트는 존재하지 않는 타입을 지어낸다.** 컴파일·실행 피드백이 없으면 "그럴듯한 이름"이 아무 저항 없이 통과한다. 산출물이 green도 red도 아닌 채 저장소에 들어간다.

**위임 프롬프트 의무 문구** (실행 불가가 예상되는 산출물):

- "참조하는 모든 타입·메서드·필드는 **grep으로 실재를 확인**하고, 확인된 정확한 이름만 사용하라"
- "실행하지 못했다면 보고 첫 줄에 **`미실행`** 을 명시하고, 실재 확인한 심볼 목록을 함께 보고하라"

**수령 측 게이트**: 미실행 산출물은 "작성 완료"가 아니라 **"컴파일 미검증"** 으로 취급 — 실제 컴파일·실행 통과 전까지 완료 처리 금지.

(2026-07-28 Slice A 카드 28 실증: HUD 테스트가 scratchpad 실행 불가 상태로 작성만 되어 `DeterministicRandomFactory`를 참조했다. 실재하지 않는 타입이고 실제 구현은 `Pcg32RandomFactory`다)

**미실재 참조에는 두 종류가 있다**. 남의 심볼은 위 grep으로 잡힌다. **자기가 나중에 정의할 예정이던 심볼**은 작성 시점에 grep 해도 없는 것이 정상이라 위 룰이 발화하지 않는다. 후자는 위임 절단 시 "본문은 있는데 헬퍼가 없는" 컴파일 불가 상태로 남는다. 처방은 grep이 아니라 **작성 순서 역전** — 헬퍼·상수·픽스처를 먼저 정의하고 사용부를 나중에 쓰면 어디서 끊겨도 컴파일된다. 상세: [best-practice/delegation-truncation-triage.md](../../best-practice/delegation-truncation-triage.md) §6

## 뮤테이션 검증 절차 게이트 (주입 전 커밋 상태 확인)

테스트 신뢰성 검증(기대 행 제거·버그 한 줄 주입 → 빨간불 확인)은 **주입 전에** 대상 파일의 커밋 상태를 확인한다. 룰 문구("넣은 방식 그대로 되돌린다")만으로는 재발했다. 확인이 선행되면 실수가 구조적으로 불가능해진다.

1. **주입 전 게이트**: `git diff --stat <file>`이 **비어 있는지** 확인. 비어 있지 않으면 먼저 커밋하거나 그 파일을 뮤테이션 대상에서 제외
2. **원복은 주입한 메커니즘 그대로**: 문자열 치환으로 넣었으면 문자열 치환으로 되돌린다. `git checkout -- <file>` 원복은 1의 게이트를 통과한(워킹트리 clean) 파일에만 허용 — 아니면 미커밋 작업이 함께 날아간다
   - **Windows 체크아웃(CRLF) 예외**: `sed -i`·python으로 치환하면 파일이 **LF로 다시 쓰인다**
   - 증상: 원복까지 마쳐 내용이 HEAD와 **바이트 동일**한데도 `git status`에는 `M`이 남고, `git diff`는 **완전히 빈 출력**(경고 줄 제외)이다
   - 판정: `git diff <file>`이 완전히 비었으면 내용 차이가 아니라 **체크아웃 형태(줄바꿈) 차이**이므로 잃을 내용이 없다. `git checkout -- <file>`이 안전하다. 비어 있지 않으면 위 문장 그대로 문자열 치환으로 되돌린다
   - 이 갈래를 모르면 손이 멈춘다. 남은 `M`을 미커밋 작업으로 오판하거나, 반대로 무시하고 커밋에 섞는다 (2026-09-09 2회)
3. **위임 시**: 프롬프트에 "남은 턴이 빠듯하면 뮤테이션을 시작하지 마라" + `// MUTATION` 마커 의무 명시, 절단 후 재개 전 구현 파일 `MUTATION` grep 게이트
4. **라이브 에디터가 붙어 있으면 주입 직후 재임포트**: 에디터는 밖에서 고친 파일을 다시 읽지 않는다.
   그래서 주입한 뮤테이션이 초록으로 통과한다 ([unity-live-editor.md](unity-live-editor.md) 같은 제목의 절)

(2026-08-31 MatchView.cs 미커밋 R3a 작업 소실 / 2026-09-01 ShopSession.cs 미커밋 2겹 소실 — 같은 사고 2회. 앞선 원복들은 문자열 치환으로 무사했고 다음 번에 손이 checkout으로 갔다)

## 계측 실패를 넘기는 가드 금지 — 표본이 반드시 있게 만든다

연출·애니메이션·시간축을 재는 테스트에 "한 프레임에 삼켜지면 표본이 없으니 건너뛴다"는 가드(`if (Time.deltaTime < 연출시간)`)를 둔다고 하자. **그 가드 안이 계약을 무는 유일한 자리면 테스트가 통째로 거짓 통과**한다. 배치 모드에는 게임 뷰도 수직동기도 없어 프레임이 길고, 가드는 한 번도 열리지 않는다.

판단("표본이 없으면 계측 실패지 계약 위반이 아니다")은 옳다. 처방을 뒤집는다. **넘어가는 대신 표본이 반드시 있게 만든다**: 연출 시간을 프레임이 삼킬 수 없는 길이(예: 1초)로 **테스트가 지정**하고, 가드를 없애고, 단언을 무조건 실행한다. 기기·모드에 흔들리지 않는 판정이 된다.

도중 표본에는 **상한과 하한을 함께** 문다. "제자리보다 위"만 물면 값이 한 번에 꽂히는 구현도 초록이다.

**적발은 뮤테이션으로만 된다** — 초록 개수로는 보이지 않는다. 연출을 무는 테스트를 쓰면 그 연출 호출을 지워 빨간불을 확인하라.

(2026-09-03 상점 미끄럼: 7건 전부 초록인데 나가는 연출을 통째로 지워도 75/75 통과)

## 완전성 감사의 명부는 검사 대상에서 파생 (손 명부 금지)

커버리지·완전성을 주장하는 테스트가 검사 대상 목록을 리터럴 배열/if 사슬로 들면 대상이 늘어난 날 **조용히 거짓 통과**한다. 명부는 리플렉션·`Enum.GetValues`·`switch` 완전성으로 파생하고, 전환은 뮤테이션으로 검증(기대 행 제거 → 빨간불). 상세: [best-practice/hand-listed-roster-decay.md](../../best-practice/hand-listed-roster-decay.md) (2026-09-01 BgBalanceLoaderTests `Shop` 축 누락을 하드코딩 명부가 조용히 통과시킨 실측)

## 단계 게이트 종단 동결 (Golden Case)

다단계 계산 파이프라인의 단계 게이트에는 단위 테스트와 별도로 **종단값 손계산 동결 케이스**를 둔다. 커버리지 감사 표 선행·대칭성·재계산 결정론 포함. 상세: [best-practice/golden-case-gate.md](../../best-practice/golden-case-gate.md)

## Unity 테스트 모드 판정 (EditMode vs PlayMode)

"동기/POCO 여부"가 아니라 **내부에서 사용하는 Unity API**가 판정 기준 — 판정 전 `Object.Destroy` / `DontDestroyOnLoad` / 씬 API grep 선행 의무. API→모드 매핑 표: [best-practice/unity-test-mode-selection.md](../../best-practice/unity-test-mode-selection.md) (2026-07-08 PoolService EditMode→PlayMode 정정 인시던트)

## 시각 검증 단위 명세 의무

UI/시각 변경(prefab/색상/위치/scale/sprite/anchor/sorting) 보고 시, **사용자가 검증할 수 있는 단위**를 사전 명시한다. "확인 부탁" / "잘 보이는지 봐줘" 같은 모호한 위임 금지.

**필수 보고 단위**:
- **변경 대상**: prefab 경로 + 컴포넌트/필드명 (예: `EdgeView.prefab > LineRenderer.startColor`)
- **변경 전/후 값**: 수치/색상/플래그 등 비교 가능 형태
- **확인 위치**: 어느 Scene/씬 진입 경로/노드에서 보이는지
- **합격 기준**: "X가 Y 색이면 통과" 같은 명시적 pass/fail 조건
- **회귀 가능 영역**: 같은 prefab/asset을 공유하는 다른 화면 (예: prefab variant 부모 영향)

**라이브 에디터가 붙어 있으면 검증자가 직접 본다** — `unity command capture_game_view`(Play Mode의
합성 결과) · `capture_scene_view` · `screenshot`이 PNG를 낸다. 그동안 시각 회귀의 유일한 그물이
사용자의 눈이었던 자리가 이제 리뷰 가능해진다. 다만 **캡처가 명세를 대신하지 못한다** — 무엇을 보고
무엇이 합격인지는 여전히 위 단위로 적는다. 캡처는 그 합격 기준을 **누가** 확인하는지만 바꾼다.

**금기**: "Inspector에서 잘 보이는지 확인 부탁" — 사용자가 어느 필드를 어디서 보고 무엇을 통과 기준으로 삼아야 할지 불명. 시각 검증 비용은 명세 없으면 지수적으로 증가.

(2026-05-13 UIMapView 노드 아이콘 / EdgeView 라인 색상 변경 시 합격 기준 모호로 사용자 검증 부담 증가 사례)
