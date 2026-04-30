[← README로 돌아가기](../README.md)

# Sheet Batch Update Read-Back 검증 (Sort Trigger 방지)

Google Sheets MCP `batch_update_cells` 호출 시, 시트의 **자동 sort filter**가 batch 결과에 트리거되어 입력한 row 순서가 ASC sort로 재배치될 수 있다. 결과: row N의 column A에는 row N+k의 데이터가 들어가는 **layer-shift misalignment**.

## 사고 사례 — Hwaseo LocalizedText_Skill (2026-04-30)

**작업**: 286 row × 3 lang(EN/JA/CN) = 858 cell 일괄 재번역 batch update.

**증상**:
- 1차 `batch_update_cells` 호출 후 row 14(`skill.0017` = "괴력") 의 EN name 컬럼에 `"For every 4 Power..."` (description text) 표시
- 검증 단계에서 row 전체 한 칸씩 swap 발견 → 시트의 sort filter가 자동 트리거되어 desc-then-name 원순서가 Key ASC 정렬로 변경됨
- 286 row 전체 misalign → batch 재작성 1회 추가 발생 (총 855 cell × 3회 = 2574 cell write, 실제 필요 853 cell)

## 검증 의무

### 옵션 A — Sort Filter 사전 비활성화 (권장)

batch update 시작 전 시트의 sort filter / `Data > Filter views`를 비활성화 후 작업 → 완료 후 재활성화. 사용자에게 사전 확인 필요 (협업 시트라면 다른 작업자에 영향).

### 옵션 B — Read-Back 즉시 검증

첫 batch 호출 직후, 동일 range를 다시 read해서 **input array와 row 순서 매칭** 확인:

```python
# 의사 코드
batch_update_cells(spreadsheet_id, sheet_name, range, values)
verify = read_range(spreadsheet_id, sheet_name, range)
for i, (sent, got) in enumerate(zip(values, verify)):
    if sent[0] != got[0]:  # Key column or first key column compare
        raise ValueError(f"Row {i} sort drift: sent {sent[0]} but read {got[0]}")
```

**필수 체크**: row index 0, 중간 (n/2), 마지막. 전수 검사가 비싸다면 표본 3개라도 하라.

### 옵션 C — Key 컬럼 함께 작성

데이터 컬럼만 update하지 말고 **Key 컬럼도 함께 batch에 포함**시켜, row 매칭이 Key 일치로 검증되게 한다. sort 트리거가 발생해도 데이터-키 정합은 유지된다.

## 안티패턴

- ❌ batch update 후 "성공" 응답만 보고 read-back 생략
- ❌ 시트 sort filter 활성 여부 사전 확인 없이 작업 시작
- ❌ Key 컬럼 제외하고 데이터 컬럼만 update (sort 발생 시 key-data 매칭 끊김)

## 시니어 회고

`batch_update_cells`의 응답 success는 **cell write 성공만 보장**하지 sort 정합을 보장하지 않는다. MCP 응답을 신뢰 boundary로 삼지 말고 read-back으로 시각적 정합 확인까지 진행해야 한다.

본 사고는 사용자 직접 시트 inspect로 발견 — Read-back 검증 단계가 자동화되어 있었다면 1차 batch 직후 발견 가능.

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — 헌법 §0-1 Step 3 표준 검증 시나리오
- [asset-migration-sort-consistency.md](asset-migration-sort-consistency.md) — 자산-시트 정렬 일관성
