"""Report code still inherited from the mod's original baseline. Exits 0 when none is left.

    python tools/audit_baseline.py --game-dir <CK3>/game [--paths file-or-dir ...] [--top N]

Fails on: a file byte-identical to a baseline file; a run of RUN_LEN or more consecutive lines that are in the
baseline but not in vanilla (single lines coincide, since CK3 script is repetitive); an inherited identifier.
LICENSE and README.md keep their credits, so they're only exempt from the identifier check and the identical check.
"""
import argparse
import os
import re
import subprocess
import sys

BASELINE = "bfcb175"
RUN_LEN = 5
MIN_LINE = 13
MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = (".txt", ".gui", ".yml")
EXEMPT = {"LICENSE", "README.md", "tools/audit_baseline.py"}
IDENT = re.compile(r"skonester|\bskone_|\bDP_|\bdp_|daddy_?pika|\byyz_|\bpcm_|\bzhuge_|\bzhueg_|\w*_0?toc\w*|\btoc_|tocmod", re.I)


def git(*args):
    return subprocess.run(["git", "-C", MOD_DIR, *args], capture_output=True, check=True).stdout


def tree(rev):
    out = {}
    for line in git("ls-tree", "-r", "-z", rev).decode("utf8").split("\0"):
        if line:
            meta, path = line.split("\t", 1)
            out[path] = meta.split()[2]
    return out


def norm(text):
    """Comparable lines: stripped, without comments or short boilerplate like `limit = {`."""
    return [s for s in (l.strip() for l in text.splitlines()) if len(s) >= MIN_LINE and not s.startswith("#")]


def runs(lines, inherited, min_len=RUN_LEN):
    """Lengths of each run of at least min_len consecutive lines in `inherited`."""
    out, n = [], 0
    for line in [*lines, None]:
        if line in inherited:
            n += 1
        else:
            if n >= min_len:
                out.append(n)
            n = 0
    return out


def baseline_lines(old, vanilla_dir):
    """Lines the baseline has and vanilla doesn't."""
    lines = set()
    for path, blob in old.items():
        if path.endswith(TEXT):
            lines.update(norm(git("cat-file", "-p", blob).decode("utf8", "replace")))
    for root in ("common", "events", "gui", "localization"):
        for dp, _, files in os.walk(os.path.join(vanilla_dir, root)):
            for f in files:
                if f.endswith(TEXT):
                    with open(os.path.join(dp, f), encoding="utf-8-sig", errors="replace") as fh:
                        lines.difference_update(norm(fh.read()))
    return lines


def self_check():
    assert runs(["a", "b", "c", "x", "d"], {"a", "b", "c", "d"}, 3) == [3]
    assert runs(["a", "x", "b"], {"a", "b"}, 2) == []
    assert runs(["a", "b"], {"a", "b"}, 2) == [2]
    assert norm("  short\n# a comment that is long enough\n  long enough to count\n") == ["long enough to count"]
    assert IDENT.search("DP_general_page_effect") and IDENT.search("zzzzzzzz_0toc_deb") and not IDENT.search("ucm_stock_gold")
    print("audit_baseline self-check OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir", default=os.environ.get("CK3_GAME_DIR"))
    ap.add_argument("--paths", nargs="*", help="only report these files or folders")
    ap.add_argument("--top", type=int, default=40, help="how many failing files to list")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        return self_check()
    if not args.game_dir:
        sys.exit("pass --game-dir <CK3>/game or set CK3_GAME_DIR")
    old = tree(BASELINE)
    old_blobs, inherited = set(old.values()), baseline_lines(old, args.game_dir)
    prefixes = tuple(p.replace("\\", "/").rstrip("/") for p in args.paths or [])
    fails = []
    # Working-tree contents, so a worker can audit before committing.
    for path in git("ls-files", "-z", "--cached", "--others", "--exclude-standard").decode("utf8").split("\0"):
        if not path or (prefixes and not any(path == p or path.startswith(p + "/") for p in prefixes)):
            continue
        full = os.path.join(MOD_DIR, path)
        if path.startswith(".claude/") or not os.path.isfile(full):
            continue
        reasons, exempt = [], path in EXEMPT
        with open(full, "rb") as fh:
            raw = fh.read()
        # Baseline blobs are LF or CRLF depending on the file, so try both.
        blobs = {subprocess.run(["git", "-C", MOD_DIR, "hash-object", "--no-filters", "--stdin"], input=form,
                                capture_output=True, check=True).stdout.decode().strip()
                 for form in (raw, raw.replace(b"\r\n", b"\n"))}
        if blobs & old_blobs and not exempt:
            reasons.append("identical to baseline")
        text = raw.decode("utf8", "replace")
        score = 0
        if path.endswith(TEXT):
            found = runs(norm(text), inherited)
            if found:
                score = sum(found)
                reasons.append(f"{score} inherited lines in {len(found)} runs")
        if not exempt and not path.startswith("docs/menu-handoff"):
            hits = len(IDENT.findall(text if path.endswith((*TEXT, ".py", ".md", ".mod")) else "")) + len(IDENT.findall(path))
            if hits:
                reasons.append(f"{hits} inherited identifiers")
        if reasons:
            fails.append((score, path, reasons))
    fails.sort(reverse=True)
    for score, path, reasons in fails[:args.top]:
        print(f"{path}: {'; '.join(reasons)}")
    print(f"{len(fails)} file(s) fail; {sum(f[0] for f in fails)} inherited lines in runs")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
