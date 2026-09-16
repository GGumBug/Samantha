# Glob: **/*.md

## 문서 표준

- 파일은 하나의 주제에 집중하고 간결하게 유지한다
- 절대 GitHub URL이 아닌 상대 링크를 사용한다 (예: `../best-practice/solid-unity-principles.md`)
- best-practice 및 reports 문서 상단에 뒤로 가기 링크를 포함한다 (기존 파일 패턴 참고)
- 새로운 모범 사례나 보고서를 추가할 때 README.md의 해당 표(`Best practices` 또는 `Reports`)를 업데이트한다
- 문서를 고칠 때 **같은 문서의 옛 현황 문장을 함께 본다**. "아직 그 시험이 없다", "N칸을 손으로 적어 뒀다" 같은 문장은 컴파일러도 시험도 잡지 못해 조용히 거짓이 된다
  (2026-09-14 실측: 손 명부의 부패를 경고하는 `best-practice/hand-listed-roster-decay.md`가 같은 병으로 거짓 현황 문장 둘을 들고 있었다)

## 구조 규칙

- 모범 사례 문서는 `best-practice/`에 넣는다
- 구현 문서는 `implementation/`에 넣는다
- 보고서는 `reports/`에 넣는다
- 팁은 `tips/`에 넣는다
- 변경 이력은 `changelog/<category>/`에 넣는다

## 서식

- 구조적 비교에는 표를 사용한다 (README `Best practices` 표를 참고)
- best-practice 또는 implementation 문서 연결 시 `!/tags/`의 배지 이미지를 사용하여 시각적 일관성을 유지한다
- 제목은 계층적으로 유지한다. 레벨을 건너뛰지 않는다 (예: `##`에서 `####`로 바로 이동하지 말 것)
