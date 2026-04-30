[← README로 돌아가기](../README.md)

# 자산 마이그레이션 정렬 일관성 검증 (Asset Migration Sort Consistency)

데이터/자산을 **시퀀셜 키**(예: `effect.0001`, `effect.0002` ...)로 부여하는 마이그레이션 script 작성 시, **자산 측 정렬 기준**(파일명 순서)과 **시트/카탈로그 측 정렬 기준**(Code Name 순서)의 **case sensitivity 일관성**을 사전 검증해야 한다. 불일치 시 키 매핑이 한 칸씩 또는 다수 shift되어 사용자 노출 데이터가 cross-link된다.

## 사고 사례 — Hwaseo HsEffectData (2026-04-30)

**증상**: 카드 hover 시 tooltip에 의도하지 않은 다른 effect 데이터 표시 (예: "불씨" 카드 hover → "불괴" 데이터).

**원인**:
- Phase 1 마이그레이션 script가 `Assets/Resources/HsEffectData/*.asset` 60개를 **파일명 PascalCase 알파벳 정렬**(case-sensitive — uppercase가 lowercase보다 앞)로 sequential 키 부여
- BGDB 시트는 Code Name을 **case-insensitive 알파벳 정렬**로 처리
- lowercase 파일명 4개 (`burn`, `curse`, `exorcism`, `tiredness`)가 자산 측에서는 정렬 끝(Z 이후)으로 밀려, 시트 측에서 알파벳 위치(B/C/E/T)에 있어야 할 자리를 인접 PascalCase 자산이 차지
- 후속 모든 키가 한두 칸씩 shift → **60 자산 중 54개의 `localizedNameKey`가 잘못된 시트 row와 매핑**

**복구 비용**: 자산 54건 정정 + 시트 row 검증 + cross-link 회귀 시나리오 재현.

## 사전 검증 의무

마이그레이션 script 실행 **전** 다음 단계를 수행:

### 1. 양측 정렬 결과 산출

```bash
# 자산 측 (find의 정렬 동작은 OS/locale 의존)
find Assets/Resources/<Type>/ -name "*.asset" -type f | sed 's|.*/||;s|\.asset$||' | sort > /tmp/asset-order.txt

# 시트 측 (BGDB MCP 또는 export 후 Code Name 컬럼만 추출)
# Code Name 컬럼 추출 → sort > /tmp/sheet-order.txt
```

### 2. case-insensitive 정렬과 case-sensitive 정렬 비교

```bash
sort /tmp/asset-order.txt > /tmp/asset-cs.txt
sort -f /tmp/asset-order.txt > /tmp/asset-ci.txt
diff /tmp/asset-cs.txt /tmp/asset-ci.txt
```

**diff 0건이 아니면** 자산 측 정렬을 case-insensitive로 normalization해야 시트와 일치.

### 3. 양측 head/tail 표본 검증

상위 10건, 하위 10건, 알파벳 transition 지점(B→C, C→D ...) 표본 비교. 한 칸이라도 어긋나면 **마이그레이션 중단** + 정렬 normalization 적용 후 재실행.

## 자동 검증 grep 패턴

마이그레이션 script 작성 시점에 **반드시** 본 패턴을 script 자체에 embed:

```python
# 예: Python 마이그레이션 script
asset_files = sorted(glob("Assets/Resources/<Type>/*.asset"), key=lambda x: x.lower())
sheet_codes = sorted(sheet_rows, key=lambda r: r["CodeName"].lower())
assert len(asset_files) == len(sheet_codes), f"Count mismatch: {len(asset_files)} vs {len(sheet_codes)}"
for i, (a, s) in enumerate(zip(asset_files, sheet_codes)):
    asset_name = Path(a).stem
    if asset_name.lower() != s["CodeName"].lower():
        raise ValueError(f"Row {i} mismatch: asset={asset_name} vs sheet={s['CodeName']}")
```

## 시니어 회고

본 사고는 **Phase 1 작성 시점에 표본 검증을 누락한 것이 회귀 노출 원인**. 60건 중 4건의 lowercase outlier가 정렬 결과 전체를 한 칸씩 shift시키지만, "PascalCase가 표준"이라는 묵시적 가정 + 표본 검증 부재로 발견 시점이 사용자 시각 사고로 밀림.

헌법 §0-1 Step 1 영향 분석에 추가: "자산 마이그레이션 script 작성 시 .asset 파일명 정렬과 시트/카탈로그 Code Name 정렬의 case sensitivity 일관성 사전 검증 의무".

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §0-1 Senior Default Mode
- [evidence-based-debugging.md](evidence-based-debugging.md) — 데이터 layer 격리 진단 프로토콜
