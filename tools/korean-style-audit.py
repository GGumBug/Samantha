#!/usr/bin/env python3
"""한국어 문체 감사 — 번역투·맞춤법 이탈을 재고 임계 초과를 빨간불로 낸다.

사용:
    python tools/korean-style-audit.py                 # 커밋·주석·문서 전부
    python tools/korean-style-audit.py --repo <경로>
    python tools/korean-style-audit.py --gate          # 임계 초과 시 exit 1

지표는 reports/korean-prose-style.md 의 처방과 1:1 대응한다.
"""
import argparse
import os
import re
import subprocess
import sys

DEFAULT_REPO = "C:/Unity_Projects/Double-Down"
CODE_ROOT = "Assets/Scripts"

# --- 임계 (SSOT) ---
LIMIT_JOSA_SPACE = 0.0      # 조사 앞 공백 비율 % — 맞춤법 제41항, 예외 없음
LIMIT_DASH_PER_1K = 2.0     # 문장 중간 줄표 1000자당
LIMIT_SENT_AVG = 50         # 평균 문장 길이(자)
LIMIT_SENT_LONG = 100       # 이 길이를 넘는 문장은 0이어야 한다
LIMIT_REGISTER_MIX = 15.0   # 한 파일 안 한다체/합니다체 섞임 %

JOSA = ("은|는|이|가|을|를|의|에서는|에서|에게|에도|에는|에|으로서|로서|으로써|로써|으로|로|"
        "와|과|도|만|까지|부터|보다|처럼|이라도|라도|이나|나|이란|란|이며|며")
# '>'는 마크다운 인용 마커이고, 한글 뒤 '.'은 문장 끝이라 그다음 "이"는 관형사다. 둘 다 앞말에서 뺀다.
TAIL = r"[A-Za-z0-9_\)\]`\"']"
BOUND = r"(?=[\s\.,·—!?)\]\"'…:;]|$)"
# 닫는 괄호 뒤의 "이"는 조사가 아니라 관형사다. 괄호가 끼어든 절이 끝나고 새 절이
# "이 값은"으로 시작하는 자리라, 한글 뒤 마침표를 앞말에서 뺀 것과 같은 이유로 뺀다.
# 2026-09-16 실측: 이 갈래를 세지 않으면 25건 중 대부분이 고칠 수 없는 위반으로 남는다.
JOSA_NO_PAREN = "이"
JOSA_REST = "|".join(j for j in JOSA.split("|") if j != JOSA_NO_PAREN)
TAIL_NO_PAREN = r"[A-Za-z0-9_\]`\"']"
JOSA_BAD = re.compile(
    "(?:" + TAIL + r" (?:" + JOSA_REST + r")" + BOUND
    + "|" + TAIL_NO_PAREN + r" " + JOSA_NO_PAREN + BOUND + ")")
JOSA_OK = re.compile(TAIL + r"(?:" + JOSA + r")" + BOUND)
# 문장 중간 삽입만 잡는다. 주술이 끝난 뒤(종결어미) 덧붙는 줄표가 영어 em dash 용법이다.
# `**라벨** — 설명`이나 `Step 1 — 제목` 같은 부제·라벨 구분자는 규정이 드는 용법이라 제외한다.
DASH_MID = re.compile(r"(?:다|음|함|됨|까|네|라|요) — ")
HANDA = re.compile(r"[가-힣]다[\.\n]")
HAPNIDA = re.compile(r"[가-힣](?:합니다|입니다|습니다|하세요|하십시오)")

# 영어 관용구·은유의 직역 후보. 보고만 하고 게이트로 쓰지 않는다 — 판단이 필요하다.
CALQUE = [
    (r"자리\b|자리가|자리를|자리에", "place / spot"),
    (r"묻는다|문다\b|무는 |물어 ", "asks / bites"),
    (r"운다\b|울고|울린|우는 ", "fires (warning)"),
    (r"조용히", "silently"),
    (r"가른다|갈린다|가르는", "splits / diverges"),
    (r"얼굴", "face"),
    (r"말한다|말해 준다", "says / tells"),
    (r"빨간불|초록불|초록인", "red / green"),
    (r"죽는다|죽은 |죽어 ", "dies"),
    (r"산다\b|살고 있|에 산다", "lives in"),
    (r"그물", "safety net"),
    (r"손잡이", "knob"),
    (r"나른다|나르는", "carries"),
    (r"쥔다|쥐고 ", "holds"),
    (r"호소", "complains"),
    (r"샌다|새는|새어", "leaks"),
]


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, encoding="utf-8", errors="ignore").stdout


def sentences(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "…", text)
    # 링크 텍스트가 파일 경로면 길이가 산문이 아니라 경로 탓이다. 자리표로 줄인다.
    text = re.sub(r"\[[^\]]*[/][^\]]*\]\([^)]*\)", "…", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    parts = re.split(r"(?<=[.!?])\s+|\n", text)
    # 표 행은 문장이 아니라 칸의 나열이다. 길이 측정에서 뺀다.
    return [p.strip() for p in parts
            if len(p.strip()) > 10 and re.search(r"[가-힣]", p)
            and not p.strip().startswith("|")]


def measure(name, text, fails):
    ko = len(re.findall(r"[가-힣]", text))
    if ko < 200:
        return
    per = ko / 1000.0
    bad, ok = len(JOSA_BAD.findall(text)), len(JOSA_OK.findall(text))
    josa_pct = 100.0 * bad / max(1, bad + ok)
    dash = len(DASH_MID.findall(text))
    dash_rate = dash / per
    sent = sentences(text)
    lens = [len(s) for s in sent]
    avg = sum(lens) / len(lens) if lens else 0
    long_n = sum(1 for x in lens if x > LIMIT_SENT_LONG)

    print(f"\n### {name}   (한글 {ko:,}자 · 문장 {len(sent):,})")
    mark = "  ← 위반" if josa_pct > LIMIT_JOSA_SPACE else ""
    print(f"  조사 앞 공백        {bad:5d} / {bad+ok:5d}   {josa_pct:5.1f}%   (임계 0%){mark}")
    mark = "  ← 초과" if dash_rate > LIMIT_DASH_PER_1K else ""
    print(f"  문장 중간 줄표      {dash:5d}            1000자당 {dash_rate:5.1f}   (임계 {LIMIT_DASH_PER_1K}){mark}")
    mark = "  ← 초과" if avg > LIMIT_SENT_AVG else ""
    print(f"  평균 문장 길이      {avg:5.0f}자          {LIMIT_SENT_LONG}자 초과 {long_n}개{mark}")
    if josa_pct > LIMIT_JOSA_SPACE:
        fails.append(f"{name}: 조사 앞 공백 {bad}건")
    if dash_rate > LIMIT_DASH_PER_1K:
        fails.append(f"{name}: 줄표 1000자당 {dash_rate:.1f}")
    if long_n:
        fails.append(f"{name}: {LIMIT_SENT_LONG}자 초과 문장 {long_n}개")

    rows = sorted(((len(re.findall(p, text)) / per, len(re.findall(p, text)), g)
                   for p, g in CALQUE), reverse=True)
    rows = [r for r in rows if r[1]]
    if rows:
        total = sum(r[1] for r in rows)
        print(f"  영어 관용구 직역    {total:5d}            1000자당 {total/per:5.1f}   (참고 — 판단 필요)")
        print("      " + " · ".join(f"{g} {n}" for _, n, g in rows[:6]))


def register_mix(fails):
    print("\n### 문체 혼재 — 한 파일 안 한다체 / 합니다체")
    for base in [".claude/rules", ".claude/agents", "."]:
        if not os.path.isdir(base):
            continue
        names = [n for n in sorted(os.listdir(base)) if n.endswith(".md")]
        for n in names:
            path = os.path.join(base, n)
            if not os.path.isfile(path):
                continue
            t = open(path, encoding="utf-8", errors="ignore").read()
            a, b = len(HANDA.findall(t)), len(HAPNIDA.findall(t))
            if a < 5 or b < 5:
                continue
            mix = 100.0 * min(a, b) / (a + b)
            mark = "  ← 혼재" if mix > LIMIT_REGISTER_MIX else ""
            print(f"  {path:42s} 한다체 {a:4d} / 합니다체 {b:4d}   섞임 {mix:4.1f}%{mark}")
            if mix > LIMIT_REGISTER_MIX:
                fails.append(f"{path}: 문체 섞임 {mix:.0f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--commits", type=int, default=150)
    ap.add_argument("--gate", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    fails = []

    print(f"# 한국어 문체 감사   (커밋 {args.commits}개)")
    measure(f"커밋 — {os.path.basename(args.repo.rstrip('/'))}",
            git(args.repo, "log", f"-{args.commits}", "--format=%s%n%b"), fails)
    measure("커밋 — 현재 저장소",
            git(".", "log", f"-{args.commits}", "--format=%s%n%b"), fails)

    lines = []
    root = os.path.join(args.repo, CODE_ROOT)
    if os.path.isdir(root):
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if f.endswith(".cs"):
                    for l in open(os.path.join(dp, f), encoding="utf-8", errors="ignore"):
                        s = l.strip()
                        if s.startswith("//") or s.startswith("*"):
                            # 태그는 낱말 한 글자로 바꾼다. 공백도 빈 문자열도 허수를 만든다.
                            # 공백이면 `<c>Foo</c>가` 가 `Foo 가` 가 되고, 빈 문자열이면
                            # `uGUI <see/>는` 이 `uGUI 는` 이 된다. 둘 다 원문에 없는 공백이다.
                            # 태그는 그 자리에 낱말이 하나 서 있는 것이므로 한 글자가 맞다.
                            # 2026-09-16 실측: 공백 방식이 522건 중 433건을 허수로 만들었다.
                            lines.append(re.sub(r"<[^>]+>", "A", s))
        measure("C# 주석", "\n".join(lines), fails)

    if os.path.isdir(".claude/rules"):
        # 파일을 빈틈없이 이어 붙이면 경계에서 없던 매치가 생긴다. 빈 줄로 가른다.
        measure("규칙 문서", "\n\n".join(
            open(".claude/rules/" + f, encoding="utf-8", errors="ignore").read()
            for f in os.listdir(".claude/rules")), fails)

    register_mix(fails)

    print("\n## 판정")
    if fails:
        print(f"  빨간불 — {len(fails)}건")
        for f in fails[:10]:
            print(f"    · {f}")
    else:
        print("  초록 — 모든 임계 통과")
    return 1 if (args.gate and fails) else 0


if __name__ == "__main__":
    sys.exit(main())
