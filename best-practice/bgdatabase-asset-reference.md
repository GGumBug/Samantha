[← README로 돌아가기](../README.md)

# BGDatabase 자산 참조 trade-off 가이드 — HybridFK string vs BG SO 바인딩

BGDatabase 시트에서 ScriptableObject/Sprite/Prefab 같은 Unity asset 을 참조하는 방식은 두 가지: **HybridFK string codeName** (Resources.LoadAll 캐시 + LINQ 매칭) vs **BG asset field 직접 바인딩** (`BGFieldUnityScriptableObject` 등). 같은 시트 안에서도 컬럼별로 다른 패턴이 가능하기 때문에 trade-off 명시적 선택이 필요하다.

## 8 차원 비교 표

| 차원 | HybridFK string codeName | BG asset field (BGFieldUnityScriptableObject) |
|------|--------------------------|-----------------------------------------------|
| Type-safe | ✗ (string typo 런타임 에러) | ✓ (Inspector drag-and-drop) |
| 자산 rename 안전 | ✗ (코드 식별자/파일명 동시 변경) | ✓ (GUID 기반 — rename 무영향) |
| 오타 방지 | ✗ (Editor 외 cross-check 없음) | ✓ (필드 자체가 NULL 가시) |
| Resources 의존 | ✓ 필수 (`Resources.LoadAll` 캐시) | ✗ 불필요 (BG 직접 참조) |
| Addressables 통합 | ✗ (별도 마이그 필요) | ✓ (BG asset → Addressable 키 변환 자연) |
| 디자이너 편집 | ✓ (시트 string 입력) | ✓ (시트 GUID 셀 — BG Editor) |
| 시트 가독성 | ✓ (codeName 직접 가독) | ✗ (GUID hex 가독 어려움) |
| 충돌 검출 | ✗ (런타임 LogWarning 누적) | ✓ (BG OnValidate 자동 검출) |

## 권장 판단 기준

**시트의 다른 컬럼이 BG asset field 를 이미 사용 중**이면 패턴 일관성이 HybridFK string 보다 SSOT 우월. 같은 시트에서 두 패턴 혼재 시 신규 합류자가 어느 컬럼이 어느 패턴인지 추적 비용이 폭발.

- ✓ Sprite/Prefab 컬럼이 BG asset field 라면 SO 참조도 BG asset field 가 일관
- ✓ Resources 폴더 의존이 작업 의도와 무관하면 BG asset field 가 자연
- ✗ Resources 폴더 의존이 의도된 분리(자동 export 등)라면 HybridFK string 유지

## 본 사이클 사례 (2026-05-11 Stage 3 마이그)

**Stage 1** (HybridFK string 채택):
- `HsPotionData_*.cs` 의 `effectAssetCodeName` 컬럼 → string 매칭
- `HsEffectDataResolver` 가 `Resources.LoadAll<HsEffectData>` 캐시 + LINQ 매칭 + 충돌 LogWarning + double-checked locking
- 시트의 Sprite 컬럼은 별개로 `BGFieldUnityScriptableObject` 사용 → 패턴 혼재

**Stage 3** (BG asset field 마이그 — 패턴 일관성 선택):
- 시트 컬럼 `effectAssetCodeName` (string) → `f_EffectAsset` (BGFieldUnityScriptableObject) 마이그
- `HsEffectDataResolver` dead code 폐기:
  - `Resources.LoadAll<HsEffectData>` 캐시 제거
  - double-checked locking 제거
  - 충돌 LogWarning 제거
- caller 는 `entry.f_EffectAsset` 직접 참조 (typed reference)

**결과**:
- 전체 LoC ~80 줄 감소 (resolver dead code 폐기)
- 자산 rename 무영향 (이전: 코드 식별자/파일명/시트 string 3 곳 동시 변경)
- 시트의 Sprite + SO 두 컬럼이 같은 BG asset field 패턴 — 신규 합류자 학습 비용 -50%

## 마이그 위임 체크리스트

HybridFK string → BG asset field 마이그 위임 시 프롬프트에 명시:

- [ ] 시트 컬럼 추가 (`f_EffectAsset` 같이 `f_` 접두로 BG field 식별) 후 BG Editor 에서 자산 drag-and-drop
- [ ] caller 영향: `*CodeName` string 참조 → `f_<Asset>` 직접 참조 grep sweep
- [ ] Resolver dead code 폐기: `Resources.LoadAll<T>` + 캐시 dictionary + 충돌 LogWarning + double-checked locking 모두 제거
- [ ] 시트 string 컬럼 제거 (BGDatabase Editor — auto-gen 재실행)
- [ ] 시트 read-back 검증 ([sheet-batch-readback.md](sheet-batch-readback.md))

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §2 SSOT / §5 YAGNI
- [sentinel-anti-pattern.md](sentinel-anti-pattern.md) — caller hardcode + 영속화 양립 race
- [sheet-batch-readback.md](sheet-batch-readback.md) — Google Sheets read-back 검증
- [asset-migration-sort-consistency.md](asset-migration-sort-consistency.md) — 자산 마이그 정렬 일관성
