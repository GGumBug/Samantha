"""S3·S4가 한 파일에 섞인 두 파일을 S3 상태로 줄였다가 되돌린다. 커밋을 hunk 단위로 가르는 데 쓴다.
사용: python split_s3.py reduce | restore | dryrun
"""
import io, os, shutil, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SRC = "C:/Unity_Projects/Double-Down/"
OUT = "C:/AI_Projects/Samantha/tools/dd/out/"
F = "Assets/Scripts/Boot/MatchSessionFactory.cs"
T = "Assets/Tests/Integration/ShopFactoryWiringTests.cs"

def reduce_factory(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        line = lines[i]
        if "// 도장 제시도 표지를 갈라 문맥부터 다시 판다" in line:
            # 7줄(주석 1, 문맥 2, 빈 줄, 스트림 2, 빈 줄)을 뺀다.
            i += 7; removed += 7; continue
        if line.strip() == "drawStream, cardDrawStream, bonusDrawStream," and i + 1 < len(lines) and "_stamps, stampPrice:" in lines[i + 1]:
            out.append(line[:-1] + ");"); i += 2; removed += 2; continue
        out.append(line); i += 1
    assert removed == 9, removed
    return nl.join(out)

def reduce_tests(text):
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    start = next(i for i, l in enumerate(lines) if "StampRunStartingGold = 100_000" in l) - 1
    assert lines[start].lstrip().startswith("///"), lines[start]
    fail = next(i for i, l in enumerate(lines) if "홍단 제시와 7월 띠 획득이" in l)
    end = fail + 1
    assert lines[end].strip() == "}", lines[end]
    end += 1
    if lines[end].strip() == "": end += 1
    return nl.join(lines[:start] + lines[end:])

mode = sys.argv[1]
if mode == "restore":
    for rel in (F, T):
        shutil.copyfile(OUT + os.path.basename(rel) + ".full", SRC + rel)
    print("restored")
    sys.exit()
for rel, fn in ((F, reduce_factory), (T, reduce_tests)):
    text = open(SRC + rel, encoding="utf-8").read()
    reduced = fn(text)
    print(rel, len(text.splitlines()), "->", len(reduced.splitlines()))
    if mode == "reduce":
        shutil.copyfile(SRC + rel, OUT + os.path.basename(rel) + ".full")
        open(SRC + rel, "w", encoding="utf-8", newline="").write(reduced)
    else:
        open(OUT + os.path.basename(rel) + ".reduced", "w", encoding="utf-8", newline="").write(reduced)
print(mode, "done")
