[← 뒤로](../README.md)

# 측정 주도 디버깅 (Measurement-Driven Debug)

같은 영역에서 추측 기반 fix 가 2회 이상 실패하면 **즉시 측정 도구를 작성**해야 한다. 코드 분석/grep/시뮬레이션은 정적 안전성만 검증할 뿐, 시간축·확률·분포가 얽힌 버그는 측정 evidence 없이 해결 불가.

## 적용 트리거

- 같은 증상으로 fix 시도 2회 이상 → 사용자 재보고
- "이론상 균등 분포여야 하는데 체감 편향" 같은 통계 의심
- 시간축 race / 부트 순서 / 비동기 타이밍 의심 (정적 안전 ≠ 시간축 안전)
- "코드는 맞아 보이는데 결과가 다름" — 가설/현실 mismatch

## 1순위 — 측정 도구 작성 의무

추측 fix 2회 실패 시점에 **반드시** 다음 중 하나를 작성:

- **로깅 harness**: 의심 지점에 `[Tag] frame=X t=Y key=Z value=W` 구조화 로그 (grep 가능 prefix)
- **카운터/히스토그램**: 분포 의심이면 N회 샘플링 후 빈도 출력
- **시간축 진단**: `Time.frameCount`, `Time.unscaledTime`, `InstanceID`, `HasInstance(before/after)` 동시 기록
- **재현 스크립트**: Editor 메뉴 / 단위 테스트로 N회 자동 반복

**출력 포맷 룰**: grep 으로 골라낼 수 있는 prefix + 시계열 정렬 가능한 timestamp + 한 줄에 충분한 컨텍스트.

## 2순위 — PRNG vs Hash Mixing 묶음

랜덤 분포 디버깅은 **두 축의 결합 효과**를 측정해야 함:

- **PRNG 시드**: `RunRngService.ForSubsystem(label)` 의 seed 가 같은 값에서 매번 같은 sequence 를 내는지
- **Hash mixing**: label/key 조합으로 sub-stream 을 파생할 때 hash 함수가 input 비트를 충분히 섞는지

한 축만 측정하면 다른 축의 편향이 가려짐. 분포 검증 시 다음 4가지 동시 기록:

| 측정 항목 | 의미 |
|-----------|------|
| seed 입력 | 결정론 검증 |
| 첫 N개 raw output | PRNG 자체 균등성 |
| label hash → sub-seed | mixing 함수 산포 |
| 최종 결과 빈도 | end-to-end 분포 |

**자주 발생하는 함정**:
- seed 가 같으면 결과 같다고 가정하지만 hash mixing 단계에서 label 간 충돌 → 같은 sub-stream 공유
- "균등 분포로 보였다" 는 체감 — 100회 샘플링 미만이면 통계적으로 의미 없음
- `GetHashCode()` 는 .NET 버전/플랫폼/string interning 에 따라 변동 — 결정론 RNG 의 mixing 함수로 사용 금지

## 금기

- ❌ "코드 분석으로 충분, 측정은 오버" — 2회 실패 시점에 자동 차단 (헌법 §0-1 Step 2 합리화 차단)
- ❌ 측정 도구 없이 3차 추측 fix 시도
- ❌ 분포 의심에 N<100 샘플로 결론

## 관련

- [evidence-based-debugging.md](evidence-based-debugging.md) — 증거 기반 디버깅 4단계 프로토콜
- [race-fix-meta-patterns.md](race-fix-meta-patterns.md) — 시간축 race 시뮬레이션
- [determinism-hooks.md](determinism-hooks.md) — RunRngService 결정론 RNG 훅
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §0-1 합리화 차단 트리거
