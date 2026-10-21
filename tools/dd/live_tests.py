"""라이브 에디터에서 픽스처를 좁혀 돌리고 두 겹의 success를 함께 요약한다.

사용: python live_tests.py editor <필터>... | python live_tests.py play <필터>
  editor는 필터마다 동기 실행한다. play는 --async_tests로 걸고 test_status를 긍정형으로 폴링한다.
  Total 0은 실패로 판정한다(필터 오타의 유일한 증상).
"""
import io, json, subprocess, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
PP = ["--project-path", "C:/Unity_Projects/Double-Down"]


def call(*args):
    out = subprocess.run(["unity", "command", *args, *PP, "--format", "json"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    try:
        return json.loads(out)
    except ValueError:
        return {"success": False, "raw": out[:300]}


def summarize(name, result):
    if isinstance(result, str):
        result = json.loads(result)
    if result.get("error"):
        print(f"{name}: 안쪽 실패 — {result['error'][:200]}")
        return False
    # 동기 응답은 Summary/Results, test_status 완료 응답은 summary/results(소문자 키)다.
    raw = result.get("Summary") or result.get("summary") or {}
    s = {k[:1].upper() + k[1:]: v for k, v in raw.items()}
    rows = result.get("Results") or result.get("results") or []
    result = {"Results": rows}
    failed = [r["FullName"] for r in rows if r.get("Status") == "Failed"]
    ok = s.get("Total", 0) > 0 and s.get("Failed", 1) == 0
    print(f"{name}: 총 {s.get('Total')} / 통과 {s.get('Passed')} / 실패 {s.get('Failed')} / 건너뜀 {s.get('Skipped')}"
          + ("" if s.get("Total") else "  ← Total 0은 실패"))
    for f in failed:
        msg = next((r.get("Message") or "" for r in result["Results"] if r["FullName"] == f), "")
        print(f"    - {f}\n      {msg.strip()[:240]}")
    return ok


mode, filters = sys.argv[1], sys.argv[2:]
all_ok = True
if mode == "editor":
    for flt in filters:
        r = call("run_tests", "--mode", "editor", "--filter", flt)
        if not r.get("success"):
            print(f"{flt}: 명령 실패 {r.get('errors') or r.get('raw')}"); all_ok = False; continue
        all_ok &= summarize(flt, r["data"]["result"])
else:
    args = ["run_tests", "--mode", "playmode", "--async_tests"]
    if filters:
        args += ["--filter", filters[0]]
    r = call(*args)
    print("시작:", json.dumps(r.get("data", {}).get("result"), ensure_ascii=False)[:200])
    for _ in range(240):
        time.sleep(10)
        st = call("test_status")
        if not st.get("success"):
            continue  # 도메인 리로드 중 무응답은 완료가 아니라 재시도
        res = st["data"]["result"]
        res = json.loads(res) if isinstance(res, str) else res
        if res.get("status") == "completed":
            all_ok &= summarize(filters[0] if filters else "playmode", res)
            break
    else:
        print("시간 초과"); all_ok = False
sys.exit(0 if all_ok else 1)
