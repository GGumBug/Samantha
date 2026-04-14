# 코드 리뷰 & 테스트 시간 컴퓨트 — Boris Cherny의 팁

Claude Code 창시자 Boris Cherny([@bcherny](https://x.com/bcherny))가 2026년 3월 10일에 공유한 인사이트 요약.

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## 1/ 코드 리뷰 도입

Claude Code의 새 기능: **코드 리뷰**. 에이전트 팀이 모든 PR에 대해 심층 리뷰를 실행합니다.

- Anthropic 자체 팀을 위해 먼저 구축 — 엔지니어당 코드 출력이 **올해 200% 증가**했으며, 리뷰가 병목이었습니다
- Boris는 몇 주 동안 사용했으며 그렇지 않으면 발견하지 못했을 많은 실제 버그를 잡아냅니다
- PR이 열릴 때 Claude가 버그를 찾기 위한 에이전트 팀을 디스패치합니다

<a href="https://x.com/bcherny/status/2031089411820228645"><img src="assets/boris-10-mar-26/0.png" alt="Boris Cherny의 코드 리뷰 발표" width="50%" /></a>

---

## 2/ 테스트 시간 컴퓨트 & 다중 컨텍스트 창

대략적으로, 코딩 문제에 던지는 토큰이 많을수록 결과가 더 좋습니다. Boris는 이것을 **테스트 시간 컴퓨트**라고 부릅니다.

- **별도의 컨텍스트 창**을 사용하면 결과가 더욱 좋아집니다 — 이것이 서브에이전트가 작동하는 이유이며, 한 에이전트는 버그를 유발하고 다른 에이전트(동일한 정확히 같은 모델 사용)는 그것을 찾을 수 있는 이유입니다
- 엔지니어링 팀과 유사: Boris가 버그를 유발하면, 코드를 검토하는 동료가 그보다 더 안정적으로 찾을 수 있습니다
- 결국, 에이전트는 완벽하고 버그 없는 코드를 작성하게 될 것입니다 — 그때까지 **여러 비상관 컨텍스트 창**이 좋은 접근법입니다

<a href="https://x.com/bcherny/status/2031151689219321886"><img src="assets/boris-10-mar-26/1.png" alt="Boris Cherny의 테스트 시간 컴퓨트에 대하여" width="50%" /></a>

---

## 출처

- [Boris Cherny (@bcherny) X에서 — 2026년 3월 10일](https://x.com/bcherny)
