#!/usr/bin/env python3
"""주석·커밋 산문 감사 — 협업 가독성 지표를 재고 임계 초과를 빨간불로 낸다.

사용:
    python tools/prose-audit.py                      # 기본 저장소 감사
    python tools/prose-audit.py --repo <경로>
    python tools/prose-audit.py --commits 50 --gate  # 임계 초과 시 exit 1

지표는 reports/agent-prose-readability.md 의 처방과 1:1 대응한다.
"""
import argparse
import os
import re
import statistics
import subprocess
import sys

DEFAULT_REPO = "C:/Unity_Projects/Double-Down"
CODE_ROOTS = ["Assets/Scripts", "Assets/Tests", "Packages/com.ggumbug.gamecore"]
SKIP_DIRS = {"Plugins", "BansheeGz", "Generated", "ThirdParty"}

# 임계 — 처방과 동일한 숫자를 여기에 둔다 (SSOT)
LIMIT_CLASS_DOC = 6        # 타입 선언 위 /// 줄
LIMIT_MEMBER_DOC = 3       # 멤버 /// 줄
LIMIT_COMMENT_RATIO = 20   # 추가된 .cs 줄 중 주석 %
LIMIT_SUBJECT = 50         # 커밋 제목 글자
LIMIT_BODY_LINES = 6       # 커밋 본문 빈 줄 제외 줄
LIMIT_TOOLTIP = 80         # Tooltip 문자열 글자

TYPE_DECL = re.compile(
    r"^\s*(?:\[[^\]]*\]\s*)*(?:public|internal|private|protected|sealed|abstract|static|partial|readonly)"
    r"[\w\s]*\b(class|struct|interface|enum|record)\b"
)
TYPE_PREFIX = re.compile(r"^[가-힣]+(?:\([^)]*\))?:")
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")


def git(repo, *args):
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                         text=True, encoding="utf-8", errors="ignore")
    return out.stdout


def source_files(repo):
    for root in CODE_ROOTS:
        base = os.path.join(repo, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                if name.endswith(".cs") and not name.endswith(".Generated.cs"):
                    yield os.path.join(dirpath, name)


def is_comment(line):
    s = line.strip()
    return s.startswith("//") or s.startswith("/*") or s.startswith("*")


def audit_comments(repo):
    total = comment = 0
    class_docs = []          # (doc 줄 수, 파일)
    member_docs = []         # (doc 줄 수, 파일)
    bold = 0
    tooltips = []            # (글자 수, 태그 포함 여부, 파일)
    for path in source_files(repo):
        lines = open(path, encoding="utf-8", errors="ignore").read().splitlines()
        total += len(lines)
        comment += sum(1 for l in lines if is_comment(l))
        rel = os.path.relpath(path, repo).replace("\\", "/")
        seen_type = False
        for i, line in enumerate(lines):
            if line.strip().startswith("///"):
                continue
            declares_type = bool(TYPE_DECL.match(line))
            declares_member = (not declares_type) and bool(
                re.match(r"\s*(public|internal|protected|private)\s", line))
            if not (declares_type or declares_member):
                continue
            depth = 0
            j = i - 1
            while j >= 0:
                s = lines[j].strip()
                if s.startswith("///"):
                    depth += 1
                    j -= 1
                elif s.startswith("["):
                    j -= 1
                else:
                    break
            if declares_type and not seen_type:
                class_docs.append((depth, rel))
                seen_type = True
            elif declares_member and depth:
                member_docs.append((depth, rel))
        text = "\n".join(l for l in lines if is_comment(l) or l.strip().startswith("///"))
        bold += text.count("<b>")
        body = "\n".join(lines)
        idx = 0
        while True:
            idx = body.find("Tooltip(", idx)
            if idx < 0:
                break
            end = body.find(")]", idx)
            end = end if end > 0 else idx + 400
            chunk = body[idx:end].split('"')
            literal = "".join(chunk[1::2])
            tooltips.append((len(literal), "<" in literal, rel))
            idx = end
    return dict(total=total, comment=comment, class_docs=class_docs,
                member_docs=member_docs, bold=bold, tooltips=tooltips)


def audit_commits(repo, count):
    raw = git(repo, "log", f"-{count}", "--format=%H\x1f%s\x1f%b\x1e")
    records = [r for r in raw.split("\x1e") if r.strip()]
    rows = []
    for rec in records:
        parts = rec.strip().split("\x1f")
        if len(parts) < 2:
            continue
        sha, subject = parts[0], parts[1]
        body = parts[2] if len(parts) > 2 else ""
        files = git(repo, "show", "--name-only", "--format=", "-1", sha).split()
        # 확장자를 Unity 자산으로 좁히면 문서·스크립트 저장소에서 늘 0건이 나온다.
        stems = {os.path.basename(f).rsplit(".", 1)[0] for f in files}
        stems |= {os.path.basename(f) for f in files}
        stems = {s for s in stems if len(s) > 3}
        names_file = any(s and s.lower() in subject.lower() for s in stems)
        body_lines = [l for l in body.splitlines() if l.strip()]
        paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
        rows.append(dict(sha=sha[:7], subject=subject, len=len(subject),
                         typed=bool(TYPE_PREFIX.match(subject)),
                         names_file=names_file, has_ident=bool(IDENTIFIER.search(subject)),
                         body_lines=len(body_lines), paragraphs=len(paragraphs)))
    return rows


def added_comment_ratio(repo, count):
    shas = git(repo, "log", f"-{count}", "--format=%H").split()
    added = commented = 0
    for sha in shas:
        diff = git(repo, "show", sha, "--unified=0", "--", *CODE_ROOTS)
        for line in diff.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                s = line[1:].strip()
                if not s:
                    continue
                added += 1
                if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
                    commented += 1
    return added, commented


def pct(part, whole):
    return 100.0 * part / whole if whole else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--commits", type=int, default=150)
    ap.add_argument("--gate", action="store_true", help="임계 초과 시 exit 1")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    repo = args.repo
    c = audit_comments(repo)
    commits = audit_commits(repo, args.commits)
    added, commented = added_comment_ratio(repo, args.commits)

    fails = []
    print(f"# 산문 감사 — {repo}  (최근 {args.commits} 커밋)\n")

    print("## 주석")
    ratio = pct(c["comment"], c["total"])
    print(f"  전체 주석 비율        {c['comment']:>6,} / {c['total']:>7,} 줄   {ratio:5.1f}%")
    ar = pct(commented, added)
    flag = "  ← 초과" if ar > LIMIT_COMMENT_RATIO else ""
    print(f"  신규 추가분 주석 비율 {commented:>6,} / {added:>7,} 줄   {ar:5.1f}%  (임계 {LIMIT_COMMENT_RATIO}%){flag}")
    if ar > LIMIT_COMMENT_RATIO:
        fails.append(f"신규 주석 비율 {ar:.1f}% > {LIMIT_COMMENT_RATIO}%")

    cd = [d for d, _ in c["class_docs"]]
    if cd:
        over = [(d, f) for d, f in c["class_docs"] if d > LIMIT_CLASS_DOC]
        print(f"  타입 doc 줄           평균 {statistics.mean(cd):4.1f}  중앙 {statistics.median(cd):4.0f}  최대 {max(cd)}")
        print(f"  임계({LIMIT_CLASS_DOC}줄) 초과 타입   {len(over)} / {len(cd)}  ({pct(len(over), len(cd)):.0f}%)")
        for d, f in sorted(over, reverse=True)[:5]:
            print(f"      {d:3d}줄  {f}")
        if over:
            fails.append(f"타입 doc 초과 {len(over)}건")
    md = [d for d, _ in c["member_docs"]]
    if md:
        over_m = [(d, f) for d, f in c["member_docs"] if d > LIMIT_MEMBER_DOC]
        print(f"  멤버 doc 줄           평균 {statistics.mean(md):4.1f}  임계({LIMIT_MEMBER_DOC}줄) 초과 {len(over_m)} / {len(md)}")
        if over_m:
            fails.append(f"멤버 doc 초과 {len(over_m)}건")

    print(f"  주석 내 <b> 태그      {c['bold']:,}개  (임계 0)")
    if c["bold"]:
        fails.append(f"<b> 태그 {c['bold']}개")

    tips = c["tooltips"]
    if tips:
        long_tips = [t for t in tips if t[0] > LIMIT_TOOLTIP]
        tagged = [t for t in tips if t[1]]
        print(f"  Tooltip               {len(tips)}개 중 {LIMIT_TOOLTIP}자 초과 {len(long_tips)}  태그 포함 {len(tagged)}")
        if tagged:
            fails.append(f"Tooltip 태그 {len(tagged)}건")

    print("\n## 커밋")
    if commits:
        n = len(commits)
        slen = [x["len"] for x in commits]
        blines = [x["body_lines"] for x in commits]
        paras = [x["paragraphs"] for x in commits]
        named = sum(1 for x in commits if x["names_file"])
        typed = sum(1 for x in commits if x["typed"])
        long_body = [x for x in commits if x["body_lines"] > LIMIT_BODY_LINES]
        print(f"  제목 글자             평균 {statistics.mean(slen):4.0f}  최대 {max(slen)}  {LIMIT_SUBJECT}자 초과 {sum(1 for s in slen if s > LIMIT_SUBJECT)}")
        print(f"  제목이 바뀐 파일 언급 {named} / {n}  ({pct(named, n):.0f}%)   ← 100% 가 목표")
        print(f"  유형 접두 사용        {typed} / {n}  ({pct(typed, n):.0f}%)")
        print(f"  본문 줄               평균 {statistics.mean(blines):4.1f}  최대 {max(blines)}  문단 평균 {statistics.mean(paras):3.1f}")
        print(f"  본문 {LIMIT_BODY_LINES}줄 초과         {len(long_body)} / {n}  ({pct(len(long_body), n):.0f}%)")
        for x in long_body[:5]:
            print(f"      {x['sha']}  {x['body_lines']:2d}줄  {x['subject'][:46]}")
        if named < n:
            fails.append(f"제목에 파일 미언급 {n - named}건")
        if long_body:
            fails.append(f"본문 초과 {len(long_body)}건")

    print("\n## 판정")
    if fails:
        print("  빨간불 — " + " / ".join(fails))
    else:
        print("  초록 — 모든 임계 통과")
    if args.gate and fails:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
