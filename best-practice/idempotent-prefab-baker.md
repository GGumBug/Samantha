[← README로 돌아가기](../README.md)

# 멱등 프리팹 베이커 — 대량 저작은 YAML 손편집 대신 에디터 굽기 도구로

프리팹에 오브젝트를 다수 추가·배선해야 할 때 YAML 직접 편집 대신 **에디터 굽기 도구**(`[MenuItem]` 정적 메서드)를 작성한다. 근거는 저장소 선례(`UIAddressableRegistrar` 헤더)의 원칙 — "자산과 `.meta` 를 사람이 적으면 GUID 가 첫 import 에서 재발급되어 참조가 끊긴다. 생성은 전부 공식 API 경유 — **GUID 를 사람이 적는 자리가 0**". Double Down 상점 프리팹(오브젝트 ~15개 추가, `ShopViewPrefabBaker`, 2026-09-01) 실측.

## 1. 왜 YAML 손편집이 아닌가

| | YAML 손편집 | 굽기 도구 (공식 API) |
|---|---|---|
| GUID | 사람이 적음 → 첫 import 재발급 위험 | `AssetDatabase`/`PrefabUtility` 가 발급 — 사람 개입 0 |
| fileID 배선 | 손 계산 — 오배선이 침묵 | 객체 참조 대입 — 타입·null 검사 |
| 재실행 | diff 재작성 | 멱등이면 무해 |
| 검증 | 육안 | 도구가 null 0건 단언 가능 |

## 2. 도구 필수 3속성

1. **멱등성** — 이름으로 기존 자식을 찾아 재사용, 없을 때만 생성. 두 번 돌려도 한 벌. 멱등이 아니면 재실행마다 중복 오브젝트가 쌓여 도구가 곧 사고 원인이 된다. 단, **"없으면 만든다"를 쓸 자리인지 먼저 가른다** (§2-1)
2. **사람이 손본 값 보존** — 치수·색·문구 등 디자이너 조정값은 덮지 않는다. 도구가 강제하는 것은 **구조(계층)·배선(참조)·초기 활성 상태**만. 값까지 덮으면 도구 실행이 곧 저작 롤백이 된다
3. **자가 치유** — 참조가 **비었을 때만** 채운다. 스프라이트 import 전에 구웠어도 다음 실행이 빈 칸을 복구 — 실행 순서 의존이 사라진다

### 2-1. "없으면 만든다"의 경계 — 그 칸을 누가 소유하는가 (2026-09-14)

`EnsureChild`(이름으로 찾고 없으면 만든다)는 도구의 기본 관용구지만, **사람이 그린 프리팹 안의 칸**에 쓰면 이름이 바뀐 날 도구가 같은 이름을 **하나 더 만들어** 글자 두 벌이 경고 없이 겹쳐 선다. 멱등성이 사고를 만드는 유일한 자리다 — 도구는 자기가 만든 것을 재사용했다고 믿는다.

판별 질문은 하나. 그 칸의 모양(치수·색·자리)을 **누가 소유하는가**.

| 소유자 | 관용구 | 못 찾으면 |
|---|---|---|
| **도구** (구조·컨테이너·그림자) | `EnsureChild` | 만든다 |
| **사람** — 그 칸 없이는 배선이 무의미 | `RequireChild` + `LogError` | **굽기를 접는다** (좌표가 틀렸다는 뜻) |
| **사람** — 그 칸은 연출·선택 | 찾기만 한다 | 그 칸만 건너뛰고 **구조는 계속 굽는다** |

셋째 갈래를 빠뜨리기 쉽다. 선택 칸 하나 때문에 굽기 전체가 접히면 도구를 못 쓰게 되므로, **구조가 먼저고 값 칸은 나중**이다.

## 3. 결과 검증

- 구운 프리팹의 스프라이트 GUID 가 대상 자산 `.meta` 의 GUID 와 **정확히 일치**하는지 grep 대조
- 배선 대상 필드 전수 null 검사 — 본 사례 13칸 null 0건
- `git diff <prefab>` 로 의도 외 변경 확인 ([.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) 워킹트리 인지 의무)

## 4. 적용 경계

- **오브젝트 1~2개·기존 필드 값 수정**은 손 배선(또는 사용자 Inspector 작업)이 싸다 — 도구 작성 비용이 역전
- 기준은 **반복성과 참조 밀도**: 오브젝트 5개 이상 + 상호 배선이 있으면 도구, 그 이하면 손
- 도구는 에디터 전용(`Editor/` 폴더) — 런타임 어셈블리에 넣지 않는다

## 종료 게이트

- [ ] GUID·fileID 를 사람이 적는 자리가 0인가
- [ ] 2회 연속 실행 시 diff 0건인가 (멱등)
- [ ] 디자이너 조정값(치수·색·문구)을 덮지 않는가
- [ ] 빈 참조만 채우는가 (자가 치유)
- [ ] 결과 GUID 대조 + null 전수 검사를 보고에 포함했는가
- [ ] 새 `[SerializeField]` 를 추가한 커밋에서 **굽기 도구의 배선 목록도 함께 봤는가** — 런타임 배선 경고 명부에만 올리면 다시 구워도 그 칸은 빈다 (2026-09-09 실측, [hand-listed-roster-decay.md](hand-listed-roster-decay.md) §5)
- [ ] 사람이 소유한 칸에 `EnsureChild` 를 쓰지 않았는가 (§2-1)
- [ ] 중첩 프리팹의 배선을 **자산**에 얹어 상위 프리팹의 오버라이드가 0인가, 자산을 **먼저** 굽는가 (§6)

## 5. 라이브 에디터가 붙어 있으면 — `run_script` (2026-09-14)

`unity` CLI 가 에디터에 연결돼 있으면 **같은 멱등성을 더 싸게** 얻는다. 굽기 로직을 `Assets/` **밖**
파일에 두고 정적 진입점을 부른다:

```bash
unity command run_script --file AgentScripts/BakeShopView.cs --entry BakeShopView.All
unity command run_script --file AgentScripts/BakeShopView.cs --dry_run true   # 컴파일만
```

| | `[MenuItem]` 굽기 도구 | `run_script` |
|---|---|---|
| 실행 | 사람이 메뉴 클릭 (또는 헤드리스 왕복) | 에이전트가 직접 |
| 비용 | 도메인 리로드 15~20초 | 인메모리 컴파일 < 2초 |
| 자산 임포트 | `Assets/` 안이라 매 저장마다 | `Assets/` 밖이라 없음 |
| 버전 관리 | 프로젝트에 커밋 | 같음(`AgentScripts/`) |

**§2 의 세 속성(멱등·손본 값 보존·자가 치유)은 그대로 요구된다** — 실행 경로만 싸졌지, 두 번 돌려도
같아야 한다는 계약은 변하지 않는다. 노드 서넛짜리 작은 배선은 스크립트도 필요 없다:
`save_prefab_contents` 가 격리 스테이지에서 선언적으로 고쳐 **재직렬화 없이** 저장한다.

**기존 베이커를 서둘러 옮기지 마라** — `unity command menu` 로 그대로 부를 수 있다. 손댈 일이 생긴
도구부터 옮기는 것이 싸다.

## 6. 중첩 프리팹 — 배선은 **자산**에, 인스턴스에 하지 마라 (2026-09-14)

사람이 저작한 프리팹(`Item_BonusCard.prefab`)을 다른 프리팹에 중첩할 때, `Button`·스크립트·배선을 **중첩 자산 자체**에 얹는다. 인스턴스에 얹으면 그 배선이 상위 프리팹 안의 **오버라이드**로 저장돼 "카드가 카드인 이유"가 카드가 아니라 상점에 산다 — 두 번째 소비자가 생기는 날 갈린다. 자산에 얹으면 오버라이드 **0**이다.

**대가로 순서가 계약이 된다.** 굽기 도구가 프리팹 둘을 여는데 중첩 인스턴스는 **디스크의 자산**을 읽는다. 그러므로 **자산을 먼저 배선하고 소비자를 나중에 연다** — 뒤집으면 배선 안 된 카드가 상점에 선다. 이 순서는 주석이 아니라 **호출 순서로** 박제한다.

```csharp
// 부모를 넘겨야 LoadPrefabContents 의 미리보기 씬 안으로 들어간다
var card = (GameObject)PrefabUtility.InstantiatePrefab(cardAsset, shelf);
```

판별: 그 컴포넌트·참조가 **"이 물건이 이 물건인 이유"** 면 자산에, **"이 화면에서만 그렇다"** 면 인스턴스에.

## 7. 공유 asset 추가가 남의 프리팹을 바꾼다 (2026-09-16 이관)

> [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md)에서 옮겨 왔다.

새 폰트·머터리얼·스프라이트·Shader 같은 **공유 asset을 Assets/에 추가**할 때가 있다.
그러면 Unity가 import 시점에 기존 prefab의 reference GUID를 자동 교체할 수 있다. 그러면 작업 범위 밖 prefab이 `Modified` 상태로 working tree에 나타난다.

**증상**:
- `git status`에 위임 작업과 무관한 `.prefab` 다수 등장
- prefab modifications 블록에 `m_FontAsset` / `m_Material` / `m_Sprite` 등 GUID만 변경된 entry
- Inspector에서 "보이는 폰트는 같은데 GUID가 다른 asset 가리킴"

**처방** (헌법 §unity-delegation "워킹트리 인지 의무"와 cross-link):

- 공유 asset (`*.ttf` / `*.asset` TMP_FontAsset / `*.mat` / `*.png` 등) 추가가 포함된 위임 종료 직후 **`git status` 전체 점검 의무**
- 의도한 prefab(UIMapView, UITutorialGuidePanel 등) 밖에서 mutation을 발견하면 사용자에게 보고한다.
  (A) 의도 적용 (B) `git restore` 두 옵션을 함께 제시한다.
- 사전 예방: 공유 asset 추가 위임 prompt에 "**asset import 후 `git status`로 의도 외 prefab mutation 확인 + 사용자 보고**" 의무 명시

(2026-05-14 RIDIBatang 폰트 추가 인시던트: `1e51495b` 커밋에서 UIMapView의 TMP_Text fontAsset GUID가 자동 교체됐다. 의도한 폰트 마이그레이션과 함께 의도 외 prefab modification도 생겼고, 사용자가 직접 발견하기 전까지 격리되지 않았다)

## 관련 문서

- [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) — `.meta` GUID 수동 지정 리스크 (본 문서는 그 처방의 구체화)
- [ui-transition-prefab-convention.md](ui-transition-prefab-convention.md) — prefab 상태 컨벤션
