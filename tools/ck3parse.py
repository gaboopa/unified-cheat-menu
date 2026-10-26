"""Tiny shared helpers for the generator scripts: top-level object parsing of CK3 script files
and the vanilla/DLC/mod file overlay. Run this file directly for a self-check."""
import glob
import os
import re

STRING = r'"(?:[^"\\\n]|\\.)*"'


def strip_comments(text):
    """Remove `# ...` comments, leaving quoted strings (which may contain # or braces) untouched."""
    return re.sub(r"(%s)|#[^\n]*" % STRING, lambda m: m.group(1) or "", text)


def _match_brace(text, i):
    """Index of the `}` closing the `{` at text[i], skipping quoted strings; len(text) if unbalanced."""
    depth = 0
    for m in re.finditer(r"%s|[{}]" % STRING, text[i:]):
        if m.group() == "{":
            depth += 1
        elif m.group() == "}":
            depth -= 1
            if depth == 0:
                return i + m.start()
    return len(text)


def top_level_objects_text(text):
    """Yield (key, body) for each top-level `key = { ... }` block in script text."""
    text = strip_comments(text)
    start = re.compile(r"(?m)^([A-Za-z_]\w*)\s*=\s*\{")
    pos = 0
    while True:
        m = start.search(text, pos)
        if not m:
            return
        end = _match_brace(text, m.end() - 1)
        yield m.group(1), text[m.end():end]
        pos = end + 1


def child_objects_text(body):
    """Yield (key, body) for each `key = { ... }` block directly inside an already-extracted body
    (comments must already be stripped)."""
    start = re.compile(r"([A-Za-z_]\w*)\s*=\s*\{")
    pos = 0
    while True:
        m = start.search(body, pos)
        if not m:
            return
        end = _match_brace(body, m.end() - 1)
        yield m.group(1), body[m.end():end]
        pos = end + 1


def entries(body):
    """Depth-0 entry names in order: `brave = { weight = 30 }` and bare `brave` both give brave."""
    out, depth, after_eq = [], 0, False
    for tok in re.findall(r'[{}=]|"[^"]*"|[^\s{}=]+', body):
        if tok in "{}":
            depth += 1 if tok == "{" else -1
            after_eq = False
        elif depth:
            continue
        elif tok == "=":
            after_eq = True
        elif after_eq:
            after_eq = False  # value of a depth-0 key = value
        else:
            out.append(tok)
    return out


def top_level_objects(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        yield from top_level_objects_text(fh.read())


def effective_files(sub, *dirs):
    """Files as the game loads <dir>/<sub>/*.txt: a later dir's file replaces an earlier one with the
    same name. Returned sorted by file name."""
    by_name = {}
    for d in dirs:
        for f in glob.glob(os.path.join(d, sub, "*.txt")):
            by_name[os.path.basename(f)] = f
    return [by_name[n] for n in sorted(by_name)]


if __name__ == "__main__":
    sample = """# comment { not a block
a = {
  name = "x } # not a comment {"
  inner = { y = 1 } # trailing }
}
b = { c = { d = 2 } }
"""
    got = [(k, " ".join(b.split())) for k, b in top_level_objects_text(sample)]
    assert [k for k, _ in got] == ["a", "b"], got
    assert 'name = "x } # not a comment {"' in got[0][1] and "inner = { y = 1 }" in got[0][1], got
    assert got[1][1] == "c = { d = 2 }", got
    assert list(top_level_objects_text("x = { unbalanced")) == [("x", " unbalanced")]
    kids = [k for k, _ in child_objects_text(" p = 1 q = { r = { s = 2 } } t = { } ")]
    assert kids == ["q", "t"], kids
    assert entries(" brave = { weight = 30 } zealous = 1 deviant ") == ["brave", "zealous", "deviant"]
    print("ck3parse self-check OK")
