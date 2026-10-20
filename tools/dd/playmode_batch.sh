#!/usr/bin/env bash
# Double Down PlayMode 전량을 배치 사본에서 돌린다(세션 한정 도구, tools/ddtest.sh의 짝).
# 동기화는 하지 않는다. ddtest.sh를 먼저 돌려 사본을 맞춘다.
set -uo pipefail

DST="C:/Unity_Projects/dd-batch"
# 파이썬은 PATH의 스토어 스텁(실행하면 "Python was not found")을 피해 실제로 도는 것을 고른다.
PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  for candidate in python3 python py "C:/Users/alsrl/AppData/Local/Python/pythoncore-3.14-64/python.exe"; do
    if "$candidate" -c "pass" >/dev/null 2>&1; then PYTHON="$candidate"; break; fi
  done
fi
[ -n "$PYTHON" ] || { echo "파이썬 없음: PYTHON 환경변수로 지정하라"; exit 1; }
UNITY="/c/Program Files/Unity/Hub/Editor/6000.3.19f1/Editor/Unity.exe"
STAMP=$(date +%Y%m%d-%H%M%S)
RESULTS="$DST/results-playmode-$STAMP.xml"
LOG="$DST/batch-playmode.log"

[ -x "$UNITY" ] || { echo "Unity 에디터 없음: $UNITY"; exit 1; }
[ -d "$DST/Assets" ] || { echo "사본 없음: 먼저 ddtest.sh를 돌린다"; exit 1; }

echo "▸ PlayMode 실행 (결과: $(basename "$RESULTS"))"
"$UNITY" -batchmode -projectPath "$DST" -runTests -testPlatform PlayMode \
  -testResults "$RESULTS" -logFile "$LOG"
UNITY_RC=$?

if [ ! -f "$RESULTS" ]; then
  echo "▸ 결과 없음 (종료 코드 $UNITY_RC) — 라이선스·컴파일 실패를 의심한다"
  grep -aiE "error CS|Licensing.*[Ee]rror|Failed to (get|resolve)" "$LOG" 2>/dev/null | sort -u | head -8
  exit 1
fi

PYTHONIOENCODING=utf-8 "$PYTHON" - "$RESULTS" <<'PY'
import sys, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
r = ET.parse(sys.argv[1]).getroot()
print()
print(f"결과 — 총 {r.get('total')} / 통과 {r.get('passed')} / 실패 {r.get('failed')} / 건너뜀 {r.get('skipped')} / start-time {r.get('start-time')}")
for s in r.iter('test-suite'):
    if s.get('type') == 'Assembly':
        mark = '' if s.get('failed') == '0' else '  ← 실패'
        print(f"  {s.get('name'):46s} {s.get('total'):>4}건  실패 {s.get('failed')}{mark}")
fails = [tc for tc in r.iter('test-case') if tc.get('result') == 'Failed']
if fails:
    print()
    print("── 실패 상세 ──")
    for tc in fails:
        f = tc.find('failure')
        msg = ''
        if f is not None and f.find('message') is not None:
            msg = (f.find('message').text or '').strip().split('\n')[0][:160]
        print(f"  {tc.get('fullname')}")
        print(f"      {msg}")
PY
exit "$UNITY_RC"
