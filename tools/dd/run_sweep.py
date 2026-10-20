"""배치 사본에서 사다리 스윕을 한 번 돈다. [Explicit] 줄을 사본에서만 떼고, 끝나면 바이트로 되돌린다.

사용: python run_sweep.py [치환.json] [--filter 이름] [--timeout-ms 값] [--ref 리비전]
  --ref는 스윕 파일만 그 리비전(git show)으로 바꿔 돈다. 옛 기준선을 다시 만들 때 쓴다
  먼저 ddtest.sh로 사본을 맞춘다. 로그의 [SWEEP] 블록을 sweep_out.txt로 뽑는다.
  치환.json은 [[원문, 바꿀 문], ...] 목록이다. 사본의 스윕 파일에만 넣고 끝나면 되돌린다(각 원문 정확히 1회).
(2026-10-08 재작성: %TEMP% 정리로 원본이 지워졌다)
"""
import io
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = "C:/Unity_Projects/Double-Down"
SP = "C:/AI_Projects/Samantha/tools/dd/out"
DST = "C:/Unity_Projects/dd-batch"
UNITY = "C:/Program Files/Unity/Hub/Editor/6000.3.19f1/Editor/Unity.exe"
REL = "Assets/Tests/Sweep/RunLadderSweepScratch.cs"
RESULTS = f"{DST}/results-sweep.xml"
LOG = f"{DST}/batch-sweep.log"
OUT = f"{SP}/sweep_out.txt"
OLD = "    [Test]\n    [Explicit]\n    [Timeout(7200000)]"
NEW = "    [Test]\n    [Timeout(7200000)]"


def read(path):
    with open(path, "rb") as f:
        return f.read()


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def to_eol(s, crlf):
    return s.replace("\r\n", "\n").replace("\n", "\r\n") if crlf else s.replace("\r\n", "\n")


extra = []
ref = None
test_filter = "RunLadderSweepScratch"
args = sys.argv[1:]
while args:
    head = args.pop(0)
    if head == "--filter":
        test_filter = args.pop(0)
    elif head == "--ref":
        ref = args.pop(0)
    elif head == "--timeout-ms":
        # 진입점마다 Timeout 값이 달라 [Explicit] 묶음을 그 값으로 찾는다.
        value = args.pop(0)
        OLD = "    [Test]\n    [Explicit]\n    [Timeout(" + value + ")]"
        NEW = "    [Test]\n    [Timeout(" + value + ")]"
    else:
        with open(head, encoding="utf-8") as f:
            extra = json.load(f)

src_bytes = read(f"{SRC}/{REL}")
dst_path = f"{DST}/{REL}"
if read(dst_path) != src_bytes:
    raise SystemExit("사본이 원본과 다르다. 먼저 동기화하라")
restore_bytes = src_bytes
if ref is not None:
    # 옛 리비전의 스윕 파일로 바꿔 돈다. 끝나면 지금 원본 바이트로 되돌린다.
    src_bytes = subprocess.run(["git", "-C", SRC, "show", f"{ref}:{REL}"], capture_output=True, check=True).stdout
    print("ref", ref, "bytes", len(src_bytes))
text = src_bytes.decode("utf-8")
crlf = "\r\n" in text

for old, new in [(OLD, NEW)] + [tuple(pair) for pair in extra]:
    probe = to_eol(old, crlf)
    count = text.count(probe)
    print("치환 건수:", count, "|", old.strip().splitlines()[0][:60])
    if count != 1:
        raise SystemExit("원문이 정확히 1회여야 한다")
    text = text.replace(probe, to_eol(new, crlf))

write(dst_path, text.encode("utf-8"))
started = time.time()
try:
    if os.path.exists(RESULTS):
        os.remove(RESULTS)
    subprocess.run([UNITY, "-batchmode", "-nographics", "-projectPath", DST, "-runTests",
                    "-testPlatform", "EditMode", "-testFilter", test_filter,
                    "-testResults", RESULTS, "-logFile", LOG], capture_output=True, timeout=14000)
finally:
    write(dst_path, restore_bytes)
    assert read(dst_path) == restore_bytes, "사본 원복 실패"

print("경과 %d초" % (time.time() - started))
try:
    root = ET.parse(RESULTS).getroot()
    print("총 {} / 통과 {} / 실패 {} / 건너뜀 {}".format(
        root.get("total"), root.get("passed"), root.get("failed"), root.get("skipped")))
except Exception as error:
    print("결과 없음:", error)

lines = []
capturing = False
with open(LOG, encoding="utf-8", errors="replace") as f:
    for raw in f:
        line = raw.rstrip("\r\n")
        if line.startswith("[SWEEP]"):
            capturing = True
            lines.append(line)
            continue
        # 예전 추출과 같은 규칙: [SWEEP] 줄 뒤로 표 줄(|를 담은 줄)이 이어지는 동안만 담는다.
        if capturing and "|" in line:
            lines.append(line)
            continue
        capturing = False

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("[SWEEP] 줄:", len(lines))
