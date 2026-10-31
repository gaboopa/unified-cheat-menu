"""Report references to things nothing defines: effects, triggers, events, scripted GUIs, modifiers, traits,
interactions, decisions, loc keys, and entries in gen_ucm_main_menu.TABS.

    python tools/check_refs.py --game-dir <CK3>/game                 # list every problem
    python tools/check_refs.py --game-dir <CK3>/game --base <rev>    # fail only on problems <rev> didn't have

With --base, anything <rev> defined counts as a known effect or trigger name, so a deleted effect is caught
wherever it's still called, whatever it's called. gui/ucm_main_menu.gui is skipped: it's generated from TABS,
which is checked instead. compat/ is skipped: it's regenerated. Script is matched with regexes, so this has false
positives (and can miss references built from $PARAMS$); --base keeps those out of the way.
"""
import argparse
import glob
import io
import os
import re
import runpy
import subprocess
import sys
import tarfile
import tempfile

from ck3parse import load_loc, strip_comments, top_level_objects_text

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEF_DIRS = {
    "effect": "scripted_effects", "trigger": "scripted_triggers", "sgui": "scripted_guis", "modifier": "modifiers",
    "trait": "traits", "interaction": "character_interactions", "decision": "decisions",
}
END = r"(?![\w:$.])"
USES = {
    "event": rf"(?:trigger_event|\bid)\s*=\s*(\w+\.\d+){END}",
    "trait": rf"\b(?:has_trait|add_trait|add_trait_force_tooltip|remove_trait)\s*=\s*(\w+){END}",
    "modifier": rf"\b(?:add|remove|has)_(?:character|county|dynasty|house|province)_modifier\s*=\s*(?:\{{\s*modifier\s*=\s*)?(\w+){END}",
}
LOC_USE = rf"\b(?:desc|custom_tooltip|custom_description_no_bullet|title)\s*=\s*\"?([A-Za-z_]\w*){END}"
GUI_LOC_USE = r"\b(?:text|tooltip)\s*=\s*\"([A-Za-z_]\w*)\""
KEY = r"(?m)(?:^|[\s{])([A-Za-z_]\w*)\s*=(?!=)"
SKIP_LOC = {"yes", "no", "root", "this", "prev", "scope"}


def read(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        return fh.read()


def script_files(root):
    return [f for sub in ("common", "events") for f in glob.glob(os.path.join(root, sub, "**", "*.txt"), recursive=True)]


def definitions(root):
    """kind -> names defined under root (mod or game folder)."""
    defs = {k: set() for k in (*DEF_DIRS, "event")}
    for kind, sub in DEF_DIRS.items():
        for f in glob.glob(os.path.join(root, "common", sub, "**", "*.txt"), recursive=True):
            defs[kind].update(k for k, _ in top_level_objects_text(read(f)))
    for f in script_files(root):
        text = read(f)
        defs["event"].update(re.findall(r"(?m)^\s*([\w-]+\.\d+)\s*=\s*\{", text))
        defs["effect"].update(re.findall(r"(?m)^\s*scripted_effect\s+(\w+)\s*=", text))
        defs["trigger"].update(re.findall(r"(?m)^\s*scripted_trigger\s+(\w+)\s*=", text))
    return defs


def tabs_problems(root):
    """Problems from the menu's source of truth, as (kind, name) pairs to check against definitions."""
    gen = os.path.join(root, "tools", "gen_ucm_main_menu.py")
    if not os.path.exists(gen):
        return set()
    try:
        tabs = runpy.run_path(gen, run_name="check_refs")["TABS"]
    except Exception as e:
        print(f"could not load TABS from {root}: {e}", file=sys.stderr)
        return {("tabs", "load failure")}
    uses, kinds = set(), {"sg": "sgui", "ia": "interaction", "dec": "decision"}
    for _, items in tabs:
        for it in items:
            if it[0] in kinds:
                uses.add((kinds[it[0]], it[1]))
            elif it[0] in ("cz", "czrow"):
                names = it[1] if isinstance(it[1], list) else [it[1]]
                uses.update(("sgui", f"ucm_crozier_cheats_sg_{n}") for n in names)
    return uses


def references(root, known):
    """(kind, name) pairs used under root. `known` is effect and trigger names to look for besides the usual suffixes."""
    uses = tabs_problems(root)
    for f in script_files(root):
        text = strip_comments(read(f))
        for kind, pat in USES.items():
            uses.update((kind, n) for n in re.findall(pat, text))
        uses.update(("loc", n) for n in re.findall(LOC_USE, text) if n not in SKIP_LOC)
        if os.path.join("common", "on_action") in f:
            uses.update(("event", n) for n in re.findall(rf"\b([a-z_]\w*\.\d+){END}", text))
        for k in re.findall(KEY, text):
            if (k.endswith("_effect") and k != "hidden_effect") or k in known["effect"]:
                uses.add(("effect", k))
            elif k.endswith("_trigger") or k in known["trigger"]:
                uses.add(("trigger", k))
    for f in glob.glob(os.path.join(root, "gui", "**", "*.gui"), recursive=True):
        if os.path.basename(f) == "ucm_main_menu.gui":
            continue
        text = strip_comments(read(f))
        uses.update(("sgui", n) for n in re.findall(r"ScriptedGui\(\s*'(\w+)'", text))
        uses.update(("loc", n) for n in re.findall(GUI_LOC_USE, text))
    return uses


def problems(root, vanilla, vanilla_loc, known):
    defs = definitions(root)
    loc = load_loc("english", root)
    out = set()
    for kind, name in references(root, known):
        if kind == "tabs":
            out.add((kind, name))
        elif kind == "loc":
            if name not in loc and name not in vanilla_loc:
                out.add((kind, name))
        elif name not in defs[kind] and name not in vanilla[kind]:
            out.add((kind, name))
    return out


def extract(rev, dest):
    data = subprocess.run(["git", "-C", MOD_DIR, "archive", rev, "common", "events", "gui", "localization"],
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter="data")
    # tools/ is export-ignore, so archive leaves it out.
    os.makedirs(os.path.join(dest, "tools"))
    names = subprocess.run(["git", "-C", MOD_DIR, "ls-tree", "--name-only", f"{rev}:tools"],
                           capture_output=True, text=True, check=True).stdout.split()
    for name in names:
        if name.endswith((".py", ".json")):
            blob = subprocess.run(["git", "-C", MOD_DIR, "show", f"{rev}:tools/{name}"], capture_output=True, check=True).stdout
            with open(os.path.join(dest, "tools", name), "wb") as fh:
                fh.write(blob)


def self_check():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "common", "scripted_effects"))
        with open(os.path.join(d, "common", "scripted_effects", "a.txt"), "w") as fh:
            fh.write('a_effect = { b_effect = yes c_thing = yes add_trait = nope add_trait = $T$ custom_tooltip = NO_LOC }\n')
        vanilla = {k: set() for k in (*DEF_DIRS, "event")}
        got = problems(d, vanilla, {}, {"effect": {"c_thing"}, "trigger": set()})
        want = {("effect", "b_effect"), ("effect", "c_thing"), ("trait", "nope"), ("loc", "NO_LOC")}
        assert got == want, got
    print("check_refs self-check OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir", default=os.environ.get("CK3_GAME_DIR"))
    ap.add_argument("--base", help="git rev to compare against (its merge base with HEAD is used)")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        return self_check()
    if not args.game_dir:
        sys.exit("pass --game-dir <CK3>/game or set CK3_GAME_DIR")
    vanilla, vanilla_loc = definitions(args.game_dir), load_loc("english", args.game_dir)
    if not args.base:
        found, old = problems(MOD_DIR, vanilla, vanilla_loc, definitions(MOD_DIR)), set()
    else:
        base = subprocess.run(["git", "-C", MOD_DIR, "merge-base", args.base, "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
        with tempfile.TemporaryDirectory() as d:
            extract(base, d)
            known = definitions(d)
            old = problems(d, vanilla, vanilla_loc, known)
        found = problems(MOD_DIR, vanilla, vanilla_loc, known)
    new = sorted(found - old)
    for kind, name in new:
        print(f"{kind}: {name}")
    print(f"{len(new)} problem(s); {len(found & old)} already in base, {len(old - found)} fixed")
    sys.exit(1 if new else 0)


if __name__ == "__main__":
    main()
