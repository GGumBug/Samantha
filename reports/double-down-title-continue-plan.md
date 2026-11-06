[← 목록](../README.md)

# 타이틀 씬 제작 + 계속하기(런 저장) 계획

## Context

타이틀 그림 13장이 `Assets/Arts/Sprites/Title/`에 임포트됐다(Double Down `8901b4c`). 지금 타이틀은 단색 배경과 금색 명판, 버튼 셋뿐이다.
이 그림으로 장면을 세우고, 메뉴에 **계속하기**를 더한다. 계속하기는 저장된 게임이 있을 때만 보인다.

조사 결과 **런 저장은 지금 전혀 없다**(`MatchSceneInstaller.cs:50` "저장·이어하기는 아직 없다"). 계속하기는 저장 기능을 새로 세우는 일이다.
사용자 결정(2026-11-06): 저장 방식은 슬레이 더 스파이어를 따른다. 저장이 있을 때 새 게임을 누르면 별도 확인 창을 띄운다. 추가 범위는 없다.

## 1. 슬레이 더 스파이어 저장 방식과 대응

| StS | 근거 | Double Down 대응 |
|---|---|---|
| 방에 들어갈 때 자동 저장(층 증가 → 저장) | gist(luckytyphlosion) | **판 시작 체크포인트**: `CreateNext` 직전 |
| 전투 승리 직후, 보상 화면 전에 저장(`post_combat`) → 다시 열면 같은 보상 화면 | gist, Steam 토론 | **상점 체크포인트**: `ReportMatchEnded`가 true를 낸 직후. 재개하면 요약 없이 같은 상점이 열린다 |
| 전투 도중 종료 → 그 전투를 1턴부터 다시. 패가 같다(전투 난수 = 시드 + 층) | Steam 토론, oohbleh | 판 도중 종료 → 그 판을 처음부터 같은 상대·같은 분배로. 판 난수는 (루트, 상대, 판 번호, 라운드)에서 파생된다(`MatchFlow.cs:509-524`) |
| 난수마다 카운터를 저장해 다시 굴리기를 막는다 | gist, libsts | 저장할 난수 위치는 `_nextMatchIndex` 하나다. 상점·상대 선택 스트림이 모두 이 값에서 파생된다 |
| 버그: 저장 안 한 제단 목록, 하나 어긋난 카운터 → 다시 열면 결과가 바뀜 | gist | 같은 함정: `MetOpponentLedger`(이번 막에 만난 상대)를 빼면 상대가 바뀐다. 캡처를 지수 증가 뒤에 하면 다음 판으로 밀린다. 둘 다 뮤테이션 시험으로 지킨다 |
| JSON 한 파일(base64 + XOR 난독화) | libsts `save.rs` | JSON 한 파일. 난독화는 하지 않는다(싱글 플레이 개발 단계) |
| 메인 메뉴에 계속하기, 런이 끝나면 저장 삭제 | 커뮤니티 설명(공식 문서 미확인) | 런이 끝나는 순간(`ReportMatchEnded` false) 삭제 |

**상점 도중에는 저장하지 않는다.** 매대 추첨이 장착한 보너스 카드에 의존하므로(`ShopSession.cs:284-292`), 구매 뒤 저장하고 상점을 다시 만들면 매대가 다시 뽑힌다.
상점에서 사고 끄면 구매 전으로 돌아가지만 매대는 같다.

## 2. 설계

### 2-1. 저장 소유와 계층

| 계층 | 새 것 | 내용 |
|---|---|---|
| Domain | `Run/RunSnapshot.cs`, `RunResumePoint {Match=1, Shop=2}`, `RunFlow.Restore(...)` | 스키마 판본, 시드 코드, 덱 id, `NextMatchIndex`, 재개 지점, RunFlow(Chips·Gold·Act·SlotIndex·MatchesWon·StakeRuleEnabled), 각서 횟수, 작업패 단 수, 보너스 카드(순서 = 발화 순서), 도장(칸 순서대로 카드 원형 id + 도장 stable id), 만난 상대 명부(막, id들), 진단용 판본. `Phase`는 저장하지 않고 복원 때 `AwaitingMatch`를 단언한다 |
| Boot | `MatchSessionFactory.CaptureSnapshot(point)`, `static FromSnapshot(...)`, 명부 노출 | 모르는 id는 기존 `Raise`·`Equip`·`Stamp` 검증이 던진다. 검증 지점은 여기 하나 |
| Application | `IRunSaveStore`(TryLoad·Save·Delete) | 포트가 필수인 근거는 asmdef다. `Boot.Scenes`가 Infrastructure를 참조하지 않는다 |
| Infrastructure | `Save/FileRunSaveStore.cs` | `[Serializable]` DTO + `JsonUtility`, 임시 파일에 쓰고 교체(원자적), 스키마 판본이 다르거나 손상되면 "저장 없음" + 경고. 데이터 판본(BG DB 해시) 차이는 경고만 하고 불러온다 |
| Boot | `RunCheckpoint.cs`(씬 스코프 POCO) | `CreateNext`와 `ReportMatchEnded`를 감싸 Save·Delete를 독점한다 |

체크포인트를 공장 안에 넣지 않는 이유: 공장 생성자를 부르는 곳이 시험 21곳이고, `BombDebugMode`(`BombDebugMode.cs:93-94`)가 탐침으로 공장을 반복 생성해 실제 세이브를 덮어쓴다. MainScene 호출부에 직접 두면 시험할 수 없다(MainScene은 자동 시험이 없다).

Easy Save 3는 설치돼 있지만 쓰지 않는다. asmdef가 없어 `DoubleDown.*` 어셈블리에서 참조할 수 없고, 서드파티 폴더에 asmdef를 더하는 비용이 `JsonUtility`보다 크다.

### 2-2. 재개 경로

- `PendingRunConfig.SetResume(snapshot)`이 스냅샷에서 `RunConfig`(시드·덱)를 파생한다. `Set()`·`Reset()`은 재개 표시를 지운다. 인스톨러는 `TakeResume()`으로 한 번만 꺼낸다.
- `MatchSceneInstaller`: 재개면 `FromSnapshot`, 아니면 `ForNewRun`. 재개일 때 BombDebugMode 시드 덮어쓰기(`:65-78`)를 건너뛴다. `FromSnapshot`이 던지면 LogError → 세이브 삭제 → 같은 RunConfig로 `ForNewRun`.
- 상점 재개: 첫 `CreateNext`가 로드 스텝 `PrepareMatchAsync`(`MainScene.cs:368`)에서 불리므로, 상점 재개 때는 그 `BuildRuntime`을 건너뛴다. 진입 훅에서 HUD 칩·슬롯을 한 번 밀고(`ShowRunChips`·`ShowBonusSlots`, 상점 콜백은 값이 바뀔 때만 불린다) 상점을 연 뒤 판을 세운다. `StartNewMatchAsync`는 `_runtime == null`이면 판을 새로 세운다(`:283-286`).
- 런이 끝나면 삭제한다. 패배 후 타이틀을 고르면 계속하기가 사라진다. 다시 하기와 클리어 후 자동 새 런은 그 런의 첫 `CreateNext`에서 다시 저장된다.

### 2-3. 타이틀 화면

- **배경은 월드 공간 SpriteRenderer**로 세운다(판 화면과 같은 방식). 카메라는 직교 크기 1.8, 중심 (3.2, −1.8)이라 1080p에서 정확히 ×3이다. 임포터의 모델 프리팹은 쓰지 않는다. 여러 프레임 파일에 Animator와 반복 클립이 자동으로 붙어, 도장 1회·램프 느린 깜빡임과 맞지 않는다. 피벗이 캔버스 하단 가운데라 임포터가 여백을 잘라도 자리는 그대로다.
- 층 순서: 방 → 테이블 → 뒷면 더미 → 칩 3 → 화투 부채 5 → 빛무리 → 전구 → 연기 → 비네트 → 로고 → 도장. 자리는 `Guides~/_generator/bake.py` `PLACE`와 승인된 합성(`Title_Screen_preview_x3.png`)을 따른다. 부제("화투 로그라이크 · 하우스에 앉는다")도 합성대로 넣는다.
- 움직임: 연기 12프레임 0.12초 반복, 도장은 진입 때 1회, 전구는 빛무리 알파 ±3%로 숨 쉬고 가끔 어두운 프레임. 프레임 진행은 `Advance(dt)` 순수 계산으로 둬 시험한다. 반복은 기존 선례(Update + sin, `HudRejectionFeedback.cs:88`)를 따른다.
- **메뉴는 uGUI 오버레이**이고 캔버스 가운데에 앵커를 둔다. 월드와 UI가 둘 다 높이 맞춤이라 어느 화면비에서도 같이 움직인다. 글자 48px(16px × 3), 간격 58, 아래 정렬. 항목은 계속하기 · 새 게임 · 설정 · 나가기. 계속하기를 숨겨도 나머지는 움직이지 않는다. 마지막 항목 아래 끝(y 794)이 칩 위 끝(804)보다 위다.
- 커서(`Title_Cursor`)는 선택된 항목 왼쪽. 첫 선택은 계속하기가 보이면 계속하기, 아니면 새 게임. 호버·선택 1.03배, 누름 0.97배(LitMotion, `MotionHandle` 보관·`TryCancel`).
- 옛 `Image_Backdrop`·`Panel_TitlePlaque`(`Text_Title` 포함)는 지운다. 씬 굽기 도구는 `AgentScripts/BakeTitleScreen.cs` 하나로 유지한다(두 도구가 한 씬을 다투지 않게).
- 확인 창 `TitleConfirmView`: "새 게임을 시작하면 진행 중인 게임이 지워집니다." [계속][취소], 기본 포커스는 취소. 확인하면 런 설정 창이 열리고, **세이브는 시작을 누를 때 지운다**. 런 설정에서 취소하면 세이브가 남는다.

## 3. 구현 카드 (카드마다 커밋 1)

카드마다 재컴파일 → 라이브 픽스처 → 배치 전량(`ddtest.sh` + PlayMode) → 뮤테이션 ≥ 1 → 커밋. 구현과 시험은 다른 에이전트다.

| 카드 | 구현/시험 | 편집 | 시험 | 뮤테이션 → 빨간불 | 게이트 |
|---|---|---|---|---|---|
| **C1** 스냅샷 | Jarvis / Sonny | `Domain/Run/RunSnapshot.cs`, `RunFlow.cs`(`Restore`) | EditMode: 범위 검증(막·슬롯·칩·골드), 왕복 | 슬롯 범위 검증 제거 | `RunFlow.Restore(` 생산자 표 |
| **C2** 공장 캡처·복원 | Jarvis / Sonny | `Boot/MatchSessionFactory.cs`(`CaptureSnapshot`·`FromSnapshot`·명부) | 통합: ① 판 재개 = 같은 상대 + 같은 첫 분배 ② 승리 뒤 상점 재개 = 같은 매대 ③ 2슬롯 뒤 재개해도 상대 비중복 | 명부 복원 생략 → ③, 지수 증가 뒤 캡처 → ① | `StartNewRun`이 갈아 끼우는 필드가 Capture·From 양쪽에 모두 있다 |
| **C3** 저장소 | Jarvis / Sonny | `Application/IRunSaveStore.cs`, `Infrastructure/Save/FileRunSaveStore.cs`, `Boot/ProjectInstaller.cs` | Infrastructure EditMode(임시 폴더): 왕복, 손상, 스키마 불일치, 보너스 순서, 없는 파일 | 보너스 정렬 저장 | `persistentDataPath`가 ProjectInstaller에만 |
| **C4** 체크포인트·재개 통로 | Jarvis / Sonny | `Boot/RunCheckpoint.cs`, `Boot/RunConfig.cs`(Resume), `Boot/MatchSceneInstaller.cs` | 통합(가짜 저장소): 판 시작 저장 지수 N, 상점 저장, 패배·클리어 삭제, 복원 실패 폴백 | 저장을 `CreateNext` 뒤로 | `IRunSaveStore` 사용처 표 |
| **C5** MainScene 배선 | Jarvis / Sonny | `Boot/Scenes/MainScene.cs`(호출부 2곳, 로드 스텝 건너뛰기, 상점 먼저, HUD 밀기) | 라이브 탐침 캡처(MainScene은 자동 시험 없음) | 건너뛰기 제거 → 탐침이 매대 불일치를 잡는다 | `_sessionFactory.(CreateNext\|ReportMatchEnded)` Boot/Scenes 0건 |
| **C6** 타이틀 장면 | Ava / Sonny | `AgentScripts/BakeTitleScreen.cs`(그림 층·카메라·옛 객체 제거·부제), `Presentation/Title/TitleSpriteFlipbook.cs`, `TitleLampFlicker.cs` | EditMode: `Advance(dt)` 반복·1회·깜빡임 | 1회 모드가 순환 | TitleScene.unity `Animator` 0건, 굽기 2회째 변경 0 |
| **C7** 메뉴 | Ava / Sonny | `Presentation/Title/TitleView.cs`(`_continueButton`·`SetContinueVisible`·`SelectInitial`·커서·반응), `TitleMenuItem.cs`, 굽기 도구 메뉴부 | PlayMode: 첫 선택, 숨김 때 선택 이동, 핸들 `OnDestroy` 취소 | 가시성 무시 | 버튼 필드 4개가 `Button` |
| **C8** 계속하기·확인 창 | Jarvis(씬)·Ava(뷰) / Sonny | `Boot/Scenes/TitleScene.cs`(Start에서 TryLoad, 계속하기, 확인 창), `Presentation/Title/TitleConfirmView.cs` + 씬 굽기 | `TitleSceneSeedTests` 확장 6건(가짜 저장소): 없음 → 숨김, 있음 → 보임·첫 선택, 계속하기 → 재개 통로, 확인 취소 → 유지, 설정 취소 → 유지, 시작 → 삭제 | 확인 시점 삭제 | TitleScene의 `.Delete(`가 시작 처리 1곳 |
| **C9** 문서 | 코디네이터 | 연구 문서 §8·§12(구현 결과), 이 계획 이전, 메모리 | — | — | 산문 게이트 초록 |

- 순서: C1 → (C2 ∥ C3) → C4 → C5, 별도 트랙 C6 → C7, 두 트랙 뒤 C8 → C9.
- 라이브 에디터가 하나라 병렬은 코드 작성까지다. 컴파일·시험·굽기는 차례로 돌린다. 허브 파일(`MatchSessionFactory`·`MainScene`·`TitleScene`·`TitleView`)은 카드 하나만 만진다.
- C8: 시험이 `AddComponent` 뒤 리플렉션으로 주입하므로 저장소는 Awake가 아니라 Start에서 읽는다. 저장소가 null이면 숨김 + LogWarning(LogError면 기존 LogAssert 시험이 깨진다).
- 낡은 주석 셋은 그 파일을 만지는 카드가 고친다: `RunConfig.cs:55-57`(타이틀에 스코프 없음), `MainScene.cs:1053`·`MatchSessionFactory.cs:277`(Boot.Scenes가 Domain 미참조).

## 4. 검증 (종단, 라이브 에디터)

1. 세이브 없이 Boot부터: 항목 3개, 커서가 새 게임, 계속하기 없음.
2. 새 게임 시작 → 파일 생김(판 시작, 지수 0). 상대 id와 첫 분배를 적어 둔다.
3. 판 도중 플레이 중지 → 다시 시작: 항목 4개, 커서가 계속하기. 메뉴와 칩이 겹치지 않는지 1920×1080·1920×1200·2560×1080 캡처로 확인.
4. 계속하기 → 2와 같은 상대·분배.
5. 승리 뒤 요약 화면에서 중지 → 재개: 요약 없이 상점, 같은 매대, HUD 칩·슬롯 일치.
6. 상점에서 산 뒤 중지 → 재개: 구매 전 상태·골드, 같은 매대.
7. 다음 판까지 간 뒤 재개: 같은 막에서 상대 중복 없음.
8. 패배 → 타이틀: 계속하기 없음, 파일 없음. 다시 하기 → 파일 생김.
9. 세이브가 있을 때 새 게임: 확인 창 취소 → 유지, 확인 → 런 설정 취소 → 유지, 시작 → 새 런으로 교체.
10. 손상 파일: 계속하기 숨김 + 경고. 콘솔 오류 0, EditMode·PlayMode 전량 통과.

화면 합격 기준(Ava 보고 단위): 1080p 캡처에서 그림이 합성 미리보기와 같은 자리(±0px), 연기 영역만 프레임 사이에 바뀐다, 계속하기가 숨으면 다른 픽셀 0.

## 5. 위험과 남는 것

| 항목 | 처리 |
|---|---|
| 판 도중 종료로 패를 미리 아는 것 | StS와 같이 받아들인다(다시 굴리기는 막힌다) |
| 클리어 뒤 자동 새 런이 저장되어 다음 실행의 계속하기가 1막 새 런을 연다 | 지금 흐름(클리어 → 같은 시드로 새 런)을 바꾸지 않는다. 타이틀 복귀 흐름은 범위 밖 |
| 에디터 플레이가 실제 `persistentDataPath`에 쓴다 | 시험은 임시 폴더만 쓴다. 개발 중 초기화는 파일 삭제 |
| L10n 기반이 없다(규칙은 요구) | 기존 선례대로 씬 TMP에 직접 적는다. 트레이드오프로 보고 |
| 배경 모션 끄기 설정 없음(연구 §2-2 권고) | 설정 화면이 범위 밖이라 남긴다 |
| 1080p 밖은 정수 배율이 아니다(1200은 ×3.33) | 정지 그림이라 받아들인다. PixelPerfectCamera는 UI와 어긋나 쓰지 않는다 |
| 소리 | 별도 트랙(자산 0건) |

## 출처

- [luckytyphlosion gist: StS unknown room re-rolling](https://gist.github.com/luckytyphlosion/e1c1fd8b445e7df406ad4bc480f9dcdd): 방 진입·전투 뒤 저장, 난수 카운터, 어긋난 카운터·제단 목록 버그
- [Steam 토론 3277925755439357420](https://steamcommunity.com/app/646570/discussions/0/3277925755439357420): 다시 열면 전투 처음부터, 같은 패
- [oohbleh, losing seed](https://oohbleh.github.io/losing-seed): 셔플 난수가 시드와 층 번호로 정해진다
- [libsts save.rs](https://docs.rs/crate/libsts/0.3.1/source/src/save.rs): 저장 필드(`post_combat`, `*_seed_count`), base64 + XOR

## 6. 진행 상태

| 카드 | 상태 | 커밋 | 검증 |
|---|---|---|---|
| C1 스냅샷 | 대기 | | |
| C2 공장 캡처·복원 | 대기 | | |
| C3 저장소 | 대기 | | |
| C4 체크포인트·재개 통로 | 대기 | | |
| C5 MainScene 배선 | 대기 | | |
| C6 타이틀 장면 | 대기 | | |
| C7 메뉴 | 대기 | | |
| C8 계속하기·확인 창 | 대기 | | |
| C9 문서 | 대기 | | |
