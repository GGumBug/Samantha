# Glob: **/*.md

## 문서 표준

- 파일은 하나의 주제에 집중하고 간결하게 유지합니다
- 절대 GitHub URL이 아닌 상대 링크를 사용합니다 (예: `../best-practice/solid-unity-principles.md`)
- best-practice 및 reports 문서 상단에 뒤로 가기 링크를 포함합니다 (기존 파일 패턴 참고)
- 새로운 개념이나 보고서를 추가할 때 README.md의 해당 표(CONCEPTS 또는 REPORTS)를 업데이트합니다

## 구조 규칙

- 모범 사례 문서는 `best-practice/`에 넣습니다
- 구현 문서는 `implementation/`에 넣습니다
- 보고서는 `reports/`에 넣습니다
- 팁은 `tips/`에 넣습니다
- 변경 이력은 `changelog/<category>/`에 넣습니다

## 서식

- 구조적 비교에는 표를 사용합니다 (README CONCEPTS 표를 참고)
- best-practice 또는 implementation 문서 연결 시 `!/tags/`의 배지 이미지를 사용하여 시각적 일관성을 유지합니다
- 제목은 계층적으로 유지합니다 — 레벨을 건너뛰지 마세요 (예: `##`에서 `####`로 바로 이동하지 말 것)
