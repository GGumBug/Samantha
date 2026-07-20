# Glob: **/*.{ts,tsx,js,jsx,py,go,rs,java,cs}

## 평가 주도 검증 (Evaluation-Driven Verification)

코드를 작성한 후 반드시 검증 단계를 거칩니다:

1. **테스트 실행**: 관련 테스트가 있으면 반드시 실행하고 결과를 보고합니다
2. **UI 변경 시**: 브라우저에서 직접 확인합니다 — 타입 체크와 테스트는 기능 정확성을 보장하지 않습니다
3. **자기 평가 금지**: 코드를 작성한 직후 "잘 되었다"고 선언하지 않습니다 — 실행 결과로 증명합니다
4. **교차 검증 권장**: 복잡한 변경은 `/simplify`나 별도 서브에이전트로 독립 리뷰합니다

## 테스트 작성자 / 구현자 분리 (기본값)

테스트 작성은 **구현자와 다른 에이전트에 위임**한다. 메커니즘: 테스트 작성자는 소비자 시점으로 코드를 역추적하므로 구현자의 사각지대를 구조적으로 통과한다.

(2026-07-08 GameCore PoolService 실증: 구현 Jarvis / 테스트 작성 Sonny 분리 → Sonny가 "Dispose 후 체크아웃된 인스턴스는 누가 치우나?" 시나리오 역추적 중 실결함 발견 — Dispose가 풀 대기 인스턴스만 파괴하고 체크아웃 인스턴스는 entry만 폐기, Release는 ObjectDisposedException → 회수 경로 소멸. 루트 수명에선 잠복, 씬-스코프 컨테이너에선 실누수)

## Unity 테스트 모드 판정 (EditMode vs PlayMode)

"동기/POCO 여부"가 아니라 **내부에서 사용하는 Unity API**가 판정 기준 — 판정 전 `Object.Destroy` / `DontDestroyOnLoad` / 씬 API grep 선행 의무. API→모드 매핑 표: [best-practice/unity-test-mode-selection.md](../../best-practice/unity-test-mode-selection.md) (2026-07-08 PoolService EditMode→PlayMode 정정 인시던트)

## 시각 검증 단위 명세 의무

UI/시각 변경(prefab/색상/위치/scale/sprite/anchor/sorting) 보고 시, **사용자가 검증할 수 있는 단위**를 사전 명시한다. "확인 부탁" / "잘 보이는지 봐줘" 같은 모호한 위임 금지.

**필수 보고 단위**:
- **변경 대상**: prefab 경로 + 컴포넌트/필드명 (예: `EdgeView.prefab > LineRenderer.startColor`)
- **변경 전/후 값**: 수치/색상/플래그 등 비교 가능 형태
- **확인 위치**: 어느 Scene/씬 진입 경로/노드에서 보이는지
- **합격 기준**: "X 가 Y 색이면 통과" 같은 명시적 pass/fail 조건
- **회귀 가능 영역**: 같은 prefab/asset 을 공유하는 다른 화면 (예: prefab variant 부모 영향)

**금기**: "Inspector 에서 잘 보이는지 확인 부탁" — 사용자가 어느 필드를 어디서 보고 무엇을 통과 기준으로 삼아야 할지 불명. 시각 검증 비용은 명세 없으면 지수적으로 증가.

(2026-05-13 UIMapView 노드 아이콘 / EdgeView 라인 색상 변경 시 합격 기준 모호로 사용자 검증 부담 증가 사례)
