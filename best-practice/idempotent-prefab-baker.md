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

1. **멱등성** — 이름으로 기존 자식을 찾아 재사용, 없을 때만 생성. 두 번 돌려도 한 벌. 멱등이 아니면 재실행마다 중복 오브젝트가 쌓여 도구가 곧 사고 원인이 된다
2. **사람이 손본 값 보존** — 치수·색·문구 등 디자이너 조정값은 덮지 않는다. 도구가 강제하는 것은 **구조(계층)·배선(참조)·초기 활성 상태**만. 값까지 덮으면 도구 실행이 곧 저작 롤백이 된다
3. **자가 치유** — 참조가 **비었을 때만** 채운다. 스프라이트 import 전에 구웠어도 다음 실행이 빈 칸을 복구 — 실행 순서 의존이 사라진다

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

## 관련 문서

- [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) — `.meta` GUID 수동 지정 리스크 (본 문서는 그 처방의 구체화)
- [ui-transition-prefab-convention.md](ui-transition-prefab-convention.md) — prefab 상태 컨벤션
