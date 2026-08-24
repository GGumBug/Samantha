#!/usr/bin/env bash
# Double Down EditMode 테스트를 Unity 배치 모드로 돌린다.
#
# 왜 사본에서 도는가: Editor 가 원본 프로젝트를 Temp/UnityLockfile 로 잠그므로 같은 폴더를
# 배치 모드가 열 수 없다. 사본은 Library 캐시를 보존해 재임포트를 건너뛴다(첫 회만 느리다).
#
# 사용법:
#   ./ddtest.sh                     Assets/Packages/ProjectSettings 증분 동기화 후 전량 실행
#   ./ddtest.sh --filter <패턴>     특정 테스트만 (예: --filter DoubleDown.Presentation.Tests)
#   ./ddtest.sh --full-sync         사본을 지우고 처음부터 (Library 캐시도 버림 — 최후 수단)
set -uo pipefail

SRC="C:/Unity_Projects/Double-Down"
DST="C:/Users/alsrl/AppData/Local/Temp/claude/C--AI-Projects-Samantha/d514da04-ede3-4dc1-a445-44595fca6b59/scratchpad/dd-batch"
UNITY="/c/Program Files/Unity/Hub/Editor/6000.3.19f1/Editor/Unity.exe"
RESULTS="$DST/results-editmode.xml"
LOG="$DST/batch.log"

FILTER=""
FULL_SYNC=0
while [ $# -gt 0 ]; do
  case "$1" in
    --filter) FILTER="$2"; shift 2 ;;
    --full-sync) FULL_SYNC=1; shift ;;
    *) echo "알 수 없는 인자: $1"; exit 2 ;;
  esac
done

[ -x "$UNITY" ] || { echo "Unity 에디터 없음: $UNITY"; exit 1; }

if [ "$FULL_SYNC" = "1" ]; then
  echo "▸ 전체 재생성 (Library 캐시 버림 — 첫 실행은 수 분 걸린다)"
  rm -rf "$DST"
fi

mkdir -p "$DST"

# 증분 동기화 — robocopy /MIR 로 Assets·Packages·ProjectSettings 만 맞춘다.
# Library 는 건드리지 않는다: 사본이 쌓아 둔 임포트 캐시가 재임포트를 건너뛰게 하는 자산이다.
echo "▸ 동기화"
for d in Assets Packages ProjectSettings; do
  # robocopy 는 변경 없으면 0, 복사 있으면 1 을 낸다 — 8 이상만 실제 오류다.
  # MSYS_NO_PATHCONV: Git Bash 가 /MIR 같은 스위치를 경로로 오인해 C:/Program Files/Git/MIR 로
  # 바꿔 버린다(robocopy 16). 슬래시 인자를 쓰는 네이티브 명령에는 항상 이 가드가 필요하다.
  MSYS_NO_PATHCONV=1 robocopy "$(cygpath -w "$SRC/$d")" "$(cygpath -w "$DST/$d")" \
    /MIR /NFL /NDL /NJH /NJS /NP /R:1 /W:1 >/dev/null
  rc=$?
  [ "$rc" -ge 8 ] && { echo "  동기화 실패: $d (robocopy $rc)"; exit 1; }
done
echo "  완료"

# -quit 을 주지 않는다: -runTests 는 끝나면 스스로 종료하는데, -quit 을 함께 주면
# 임포트 직후 종료해 테스트에 도달하지 못하고 그때도 종료 코드 0 을 낸다(성공으로 오인).
ARGS=(-batchmode -nographics -projectPath "$DST"
      -runTests -testPlatform EditMode
      -testResults "$RESULTS" -logFile "$LOG")
[ -n "$FILTER" ] && ARGS+=(-testFilter "$FILTER")

rm -f "$RESULTS"
echo "▸ 실행${FILTER:+ (필터: $FILTER)}"
"$UNITY" "${ARGS[@]}"
UNITY_RC=$?

if [ ! -f "$RESULTS" ]; then
  echo "▸ 결과 없음 (종료 코드 $UNITY_RC) — 라이선스·컴파일 실패를 의심한다"
  grep -aiE "error CS|Licensing.*[Ee]rror|Failed to (get|resolve)" "$LOG" 2>/dev/null | sort -u | head -8
  exit 1
fi

PYTHONIOENCODING=utf-8 python - "$RESULTS" <<'PY'
import sys, xml.etree.ElementTree as ET
# 콘솔 기본 코드페이지가 cp949 라 한글·em dash 가 UnicodeEncodeError 를 낸다 — 출력을 UTF-8 로 고정한다.
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
r = ET.parse(sys.argv[1]).getroot()
total, passed, failed = r.get('total'), r.get('passed'), r.get('failed')
print()
print(f"결과 — 총 {total} / 통과 {passed} / 실패 {failed} / 건너뜀 {r.get('skipped')}")
print()
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
