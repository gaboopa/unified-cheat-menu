"""Static checks that need no game files, for CI: balanced braces, localization format, language parity, every ucm_
name used being defined somewhere in the mod, and valid DDS files and icon references.

    python tools/check_mod.py               # list every problem, exit 1 if any
    python tools/check_mod.py --self-check

Names are matched with regexes. A name built with $PARAM$ is only checked by its literal prefix, and writing a
variable or flag counts as defining it, so a typo made the same way at every use isn't caught.
"""
import argparse
import os
import re
import struct
import sys
import tempfile

from check_refs import MOD_DIR, read
from ck3parse import LOC_LINE, STRING, load_loc, strip_comments, top_level_objects_text

SKIP_DIRS = {".git", ".claude", ".github", "docs", "tools", "release"}
LOC_COMMENT = re.compile(r"^\s*(#.*)?$")
NAME = r"\bucm_\w+"
USED_NAME = re.compile(NAME + r"(?:\.\d\w*(?:\.\w+)*)?")  # also takes dotted event ids and loc keys: ucm_x.1, ucm_x.00x.close
FILE_PATH = re.compile(r"[\w/.-]+\.(?:gui|dds|png|tga|txt|ogg)\b")
# Where a name comes into being at runtime or in a GUI file, rather than as a top-level block or loc key.
RUNTIME_DEF = re.compile(
    rf"\b(?:set_\w*variable|change_\w*variable)\s*=\s*\{{\s*name\s*=\s*({NAME}\$?)"
    rf"|\b(?:set_\w*variable|add_\w*_flag|set_\w*_flag|save_\w*scope_as|save_\w*scope_value_as)\s*=\s*({NAME}\$?)"
    rf"|\badd_to_\w*list\s*=\s*\{{\s*name\s*=\s*({NAME}\$?)"
    rf"|\badd_to_\w*list\s*=\s*({NAME}\$?)"
    rf"|\bcopy_localized_text\s*=\s*\{{\s*key\s*=\s*({NAME})"
    rf"|\b(?:flag|namespace|LIST|FLAG)\s*=\s*({NAME}\$?)"  # LIST and FLAG are effect params that get written inside
    rf"|\b(?:type|types|template|block)\s+\"?({NAME})"
    rf"|({NAME})\s*=\s*\{{\s*type\s*="  # character_sets in succession_election
    rf"|GetVariableSystem\.(?:Set|Toggle)\(\s*'({NAME})'"
)
GUI_NAME = re.compile(rf"\bname\s*=\s*\"?({NAME})")
# Read or cleared, but nothing sets them any more. Harmless; remove the reads, then these, once tested in game.
KNOWN_UNSET = {"ucm_cheat_menu_cheat_menu", "ucm_chenzhi_force_feudal_conversion", "ucm_no_marry_vow"}


TRANSLATIONS = ("german", "russian", "simp_chinese", "turkish")
ENGLISH_ONLY_FILES = {"ucm_ek2_l_english.yml"}  # the EK2 tab's labels stay English
ICON_PATH = re.compile(r"gfx/[\w/.-]+\.(?:dds|tga|png)\b")
# `icon = x` in these folders means <folder>/x.dds.
ICON_DIRS = {
    "casus_belli_types": "casus_bellis", "character_interactions": "character_interactions", "modifiers": "modifiers",
    "men_at_arms_types": "regimenttypes", "religion": "faith", "traits": "traits",
}
ICON_USE = re.compile(r"\b(?:reformed_)?icon\s*=\s*\"?([\w.-]+)(?![\w$.-])")
# Checked against the 1.20.1.2 install. check_refs.py doesn't cover these, so recheck after a game update.
VANILLA_ICONS = {
    "gfx/interface/illustrations/decisions/decision_misc.dds",
    "gfx/interface/icons/character_interactions/debug_chars.dds",
    "gfx/interface/icons/character_interactions/debug_take_title.dds",
    "gfx/interface/icons/character_interactions/icon_contract_modification_single.dds",
    "gfx/interface/icons/faith/christianity_messalian.dds",
    "gfx/interface/icons/traits/whole_of_body.dds",
    *(f"gfx/interface/icons/modifiers/{n}.dds" for n in (
        "county_modifier_development_positive", "economy_positive", "martial_positive", "piety_positive",
        "prowess_positive", "social_negative", "social_positive", "stewardship_positive")),
}
# Used by gen_ucm_crozier.py, but neither the mod nor vanilla has it. Remove once the generator picks a real icon.
KNOWN_MISSING_ICONS = {"gfx/interface/icons/modifiers/positive.dds"}


def walk(root, exts):
    for d, subs, names in os.walk(root):
        subs[:] = [s for s in subs if s not in SKIP_DIRS]
        for n in sorted(names):
            if n.endswith(exts):
                yield os.path.join(d, n)


def brace_problems(root):
    out = []
    for f in walk(root, (".txt", ".gui")):
        open_lines, stray = [], None
        text = re.sub(STRING, '""', strip_comments(read(f)))
        for n, line in enumerate(text.splitlines(), 1):
            for c in re.findall(r"[{}]", line):
                if c == "{":
                    open_lines.append(n)
                elif open_lines:
                    open_lines.pop()
                elif stray is None:
                    stray = n
        rel = os.path.relpath(f, root)
        if stray is not None:
            out.append(f"{rel}:{stray}: stray }}")
        if open_lines:
            out.append(f"{rel}:{open_lines[-1]}: {len(open_lines)} unclosed {{")
    return out


def loc_problems(root):
    out = []
    for f in walk(os.path.join(root, "localization"), (".yml",)):
        rel = os.path.relpath(f, root)
        lang = os.path.relpath(f, os.path.join(root, "localization")).split(os.sep)[0]
        with open(f, "rb") as fh:
            raw = fh.read()
        if not raw.startswith(b"\xef\xbb\xbf"):
            out.append(f"{rel}: no UTF-8 BOM")
        try:
            lines = raw.decode("utf-8-sig").splitlines()
        except UnicodeDecodeError as e:
            out.append(f"{rel}: not UTF-8: {e}")
            continue
        header = False
        for n, line in enumerate(lines, 1):
            if LOC_COMMENT.match(line):
                continue
            if not header:
                header = True
                if line.rstrip() != f"l_{lang}:":
                    out.append(f"{rel}:{n}: header should be l_{lang}:")
            elif not LOC_LINE.fullmatch(line):
                out.append(f"{rel}:{n}: bad key line: {line.strip()[:60]}")
        if not header:
            out.append(f"{rel}: no l_{lang}: header")
    return out


def ucm_name_problems(root):
    script = {}
    for f in walk(root, (".txt", ".gui")):
        script[f] = strip_comments(read(f))
    defined = set(load_loc("english", root)) | KNOWN_UNSET
    prefixes = set()
    for f, text in script.items():
        defined.update(k for k, _ in top_level_objects_text(text))
        defined.update(re.findall(r"(?m)^\s*(?:scripted_effect|scripted_trigger)\s+(\w+)\s*=", text))
        defined.update(re.findall(r"(?m)^\s*(ucm_\w+\.\d\w*)\s*=\s*\{", text))
        for block in re.findall(r"\bsaved_scopes\s*=\s*\{([^}]*)\}", text):
            defined.update(re.findall(NAME, block))
        if f.endswith(".gui"):
            defined.update(GUI_NAME.findall(text))
        for groups in RUNTIME_DEF.findall(text):
            name = next(g for g in groups if g)
            if name.endswith("$"):
                prefixes.add(name[:-1])
            else:
                defined.add(name)
    prefixes = tuple(prefixes)
    used = {}
    for f, text in script.items():
        text = FILE_PATH.sub("", text)
        for m in USED_NAME.finditer(text):
            name = m.group()
            if name in defined or name.startswith(prefixes) or text[m.end():m.end() + 1] == "$":
                continue
            used.setdefault(name, f"{os.path.relpath(f, root)}:{text.count(chr(10), 0, m.start()) + 1}")
    return [f"{where}: {name} is not defined" for name, where in sorted(used.items())]


def parity_problems(root):
    english = set()
    for f in walk(os.path.join(root, "localization", "english"), (".yml",)):
        if os.path.basename(f) not in ENGLISH_ONLY_FILES:
            english.update(k for k, _ in LOC_LINE.findall(read(f)))
    return [f"{lang}: {key} is missing" for lang in TRANSLATIONS for key in sorted(english - set(load_loc(lang, root)))]


def icon_problems(root):
    out = []
    for f in walk(root, (".dds",)):
        with open(f, "rb") as fh:
            head = fh.read(128)
        if len(head) < 128 or head[:4] != b"DDS " or head[4:8] != struct.pack("<I", 124) or head[76:80] != struct.pack("<I", 32):
            out.append(f"{os.path.relpath(f, root)}: invalid DDS header")
    used = {}
    for f in walk(root, (".txt", ".gui", ".yml")):
        rel = os.path.relpath(f, root)
        text = strip_comments(read(f))
        for path in ICON_PATH.findall(text):
            used.setdefault(path, rel)
        parts = rel.split(os.sep)
        folder = parts[parts.index("common") + 1] if "common" in parts[:-1] else None
        if folder in ICON_DIRS:
            for name in ICON_USE.findall(text):
                file_name = name if name.endswith(".dds") else f"{name}.dds"
                used.setdefault(f"gfx/interface/icons/{ICON_DIRS[folder]}/{file_name}", rel)
    for path, rel in sorted(used.items()):
        if path not in VANILLA_ICONS | KNOWN_MISSING_ICONS and not os.path.exists(os.path.join(root, path)):
            out.append(f"{rel}: {path} doesn't exist")
    return out


def write(root, rel, data):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def self_check():
    with tempfile.TemporaryDirectory() as d:
        write(d, "common/a.txt", b'a = { b = "}" # }\n}\nc = { {\n}\n')
        write(d, "common/b.txt", b"x = 1\n}\n")
        assert brace_problems(d) == [f"common{os.sep}a.txt:3: 1 unclosed {{", f"common{os.sep}b.txt:2: stray }}"], brace_problems(d)
    with tempfile.TemporaryDirectory() as d:
        bom = b"\xef\xbb\xbf"
        write(d, "localization/german/ok_l_german.yml", bom + b'# c\nl_german:\n # c\n a:0 "x"\n\n b: "y" # z\n')
        write(d, "localization/german/nobom_l_german.yml", b'l_german:\n')
        write(d, "localization/german/wrong_l_german.yml", bom + b'l_english:\n a:0 "x\n')
        got = [p.replace(os.sep, "/") for p in loc_problems(d)]
        assert got == ["localization/german/nobom_l_german.yml: no UTF-8 BOM",
                       "localization/german/wrong_l_german.yml:1: header should be l_german:",
                       'localization/german/wrong_l_german.yml:2: bad key line: a:0 "x'], got
    with tempfile.TemporaryDirectory() as d:
        write(d, "localization/english/a_l_english.yml", b'l_english:\n ucm_loc:0 "x"\n')
        write(d, "common/a.txt", b"""ucm_def_effect = {
  ucm_gone_effect = yes
  add_character_flag = ucm_flag
  set_global_variable = { name = ucm_on_$KEY$ value = yes }
  has_global_variable = ucm_on_thing
  has_character_flag = ucm_flag
  has_character_flag = ucm_never_set
  custom_tooltip = ucm_loc
  ucm_built_$KEY$ = yes
  ucm_def_effect = yes
  trigger_event = ucm_ns.1
  trigger_event = ucm_ns.2
  tradition_ucm_other = yes
  scope:ucm_sg = { }
  x = gui/ucm_some_file.gui
}
ucm_ns.1 = { }
namespace = ucm_ns
ucm_sgui = { saved_scopes = { ucm_sg } }
""")
        got = [p.split(": ")[1] for p in ucm_name_problems(d)]
        assert got == ["ucm_gone_effect is not defined", "ucm_never_set is not defined", "ucm_ns.2 is not defined"], got
    with tempfile.TemporaryDirectory() as d:
        write(d, "localization/english/a_l_english.yml", b'l_english:\n a:0 "x"\n b:0 "y"\n')
        write(d, "localization/english/ucm_ek2_l_english.yml", b'l_english:\n tab:0 "EK2"\n')
        for lang in TRANSLATIONS:
            write(d, f"localization/{lang}/a_l_{lang}.yml", f'l_{lang}:\n a:0 "x"\n'.encode() + (b' b:0 "y"\n' if lang != "turkish" else b""))
        assert parity_problems(d) == ["turkish: b is missing"], parity_problems(d)
    with tempfile.TemporaryDirectory() as d:
        good = b"DDS " + struct.pack("<I", 124) + bytes(68) + struct.pack("<I", 32) + bytes(48)
        write(d, "gfx/interface/icons/traits/a.dds", good)
        write(d, "gfx/interface/icons/traits/bad.dds", b"DDS ")
        write(d, "common/traits/t.txt", b'a = { icon = "a.dds" }\nb = { icon = gone }\nc = { icon = $P$ }\nd = { icon = x_$P$ }\n# icon = no\n')
        write(d, "common/decisions/d.txt", b'a = { reference = "gfx/interface/illustrations/decisions/decision_misc.dds" }\nb = { icon = not_a_path }\nc = { reference = "gfx/nope.dds" }\n')
        got = [p.replace(os.sep, "/") for p in icon_problems(d)]
        assert got == ["gfx/interface/icons/traits/bad.dds: invalid DDS header",
                       "common/traits/t.txt: gfx/interface/icons/traits/gone.dds doesn't exist",
                       "common/decisions/d.txt: gfx/nope.dds doesn't exist"], got
    print("check_mod self-check OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-check", action="store_true")
    if ap.parse_args().self_check:
        return self_check()
    sys.stdout.reconfigure(encoding="utf-8")  # problem lines quote Cyrillic and Chinese text
    found = 0
    for title, check in (("braces", brace_problems), ("localization", loc_problems), ("language parity", parity_problems),
                         ("ucm names", ucm_name_problems), ("icons", icon_problems)):
        problems = check(MOD_DIR)
        for p in problems:
            print(p)
        print(f"{title}: {len(problems)} problem(s)")
        found += len(problems)
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
