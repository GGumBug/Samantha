# Glob: **/*.cs,**/*.unity,**/*.prefab,**/*.asset,**/*.anim,**/*.controller,**/*.shader,**/*.shadergraph,**/*.mat

## 라이브 에디터 우선 (필수 — [unity-delegation.md](unity-delegation.md)에서 분리)

> unity-delegation.md 200줄 정책 준수를 위해 분리된 파일. 외부 문서의 「라이브 에디터 우선」
> 인용은 이 파일을 가리킨다. 적용 강제력은 모체와 같다(Glob 자동 주입).

프로젝트에 `com.unity.pipeline`이 있고 에디터가 떠 있으면 **CLI가 그 에디터를 직접 조종**한다.
씬·프리팹·에셋을 만지는 작업은 **파일을 쓰기 전에 반드시** 연결을 먼저 묻는다.

```bash
unity status                              # state "ready" + Port가 보이면 연결됨
unity command set_autotick --enable true  # ← 안 하면 포커스를 잃은 에디터가 recompile·test를 멎춘다
unity command                             # 이 에디터가 노출하는 명령 목록(에디터가 정한다 — 이름을 추측하지 마라)
```

**연결돼 있으면 파일 대신 명령으로 한다.** `.unity`·`.prefab`·`.asset` YAML 손편집은 ⓐ fileID·GUID를
사람이 적어 틀리기 쉽고 ⓑ 재임포트 전까지 **떠 있는 에디터에 안 보여** 조용히 실패하며 ⓒ 활성 씬이
아닌 엉뚱한 파일을 고치기 쉽다.

| 하려는 일 | 명령 |
|---|---|
| 프리팹 노드 추가·배선 | `save_prefab_contents` (격리 스테이지 — 재직렬화 없음) · `add_component` · `attach_script` · `set_serialized_field` · `set_component_properties` |
| 대량 저작 | `run_script --file AgentScripts/Build.cs --entry Build.All` (`Assets/` 밖 파일 → 인메모리 컴파일, 도메인 리로드 없음) |
| 기존 `[MenuItem]` 굽기 도구 실행 | `unity command menu` |
| 여러 편집을 한 Undo로 | `batch` (실패 시 전체 롤백) |

**"연결 안 됨"은 네 얼굴이 똑같다. 파일 편집으로 새기 전에 갈라라**:

| 증상 | 판별 | 처방 |
|---|---|---|
| 에디터가 정말 없음 | `unity editors running`이 `count: 0` | 사용자에게 에디터를 열어 달라고 하거나 `unity open <path>` |
| **Safe Mode** (컴파일 에러) | `unity pipeline list`의 `Safe Mode` 칸 | **컴파일 에러를 고치는 것이 정답이다** — 우회가 아니다 |
| 샌드박스가 가림 | 위 둘이 정상인데 `status`만 빔 | "내 샌드박스가 가릴 수 있다"를 말하고 사용자에게 확인 요청 |
| **도메인 리로드 중 일시 단절** | 위 셋이 다 정상인데 **방금 한 호출만** 실패 (2026-09-14 실측: `recompile` 직후 `run_tests`가 `No Unity Editor instances found` — 직후 `status`·`editors running`·`pipeline list` 셋 다 정상) | 재시도한다 — 파일 편집으로 새는 자리가 아니다 |

`pipeline list`와 `editors running`이 **엇갈리면** 낡은 락파일이다(`Running: true` 인데 PID 칸이 빔)
— 프로세스를 보는 `editors running` 쪽을 믿어라. (2026-09-14 실측: 에디터가 닫혔는데 락파일만 남아
`Running: true`로 보였다. 두 명령을 나란히 보지 않았으면 "포트가 왜 안 뜨지"로 헤맸다.)

**끝내 파일을 직접 편집한다면 보고에 명시해라** — *"라이브 에디터 없음(사유), 파일 직접 편집"*.
조용히 새는 것이 이 규칙이 막으려는 유일한 실패다.

**모달 다이얼로그는 멈춤이 아니다** — 명령이 길어지면 `unity command editor_status`(막혀 있어도 즉답).
`status: "blocked_by_dialog"` 면 재시도를 멈추고 **무엇이 막는지 사용자에게 말해라**(CLI로 못 누른다).

## 관련 문서

- [unity-delegation.md](unity-delegation.md) — 위임 규칙 본문(이 파일의 모체)
- [evaluation.md](evaluation.md) — 두 겹 검증 루프와 두 겹의 success
- [../../best-practice/idempotent-prefab-baker.md](../../best-practice/idempotent-prefab-baker.md) — 멱등 굽기와 `run_script`
