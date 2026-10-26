"""Generate the faith editor's data effects from the CK3 1.20 religion databases.

Writes common/scripted_effects/ucm_acm_faith_editor_data_effects.txt (vanilla + this mod). gen_ek2_compatch.py
calls build() for the Elder Kings 2 version in compat/ek2/.

1.20 keeps core tenets and doctrines on Rites, so everything here reads and edits the selected faith's main
rite: rite_has_doctrine / rite_has_tenet / trait_is_virtue_rite to display it, change_rite_doctrine (which
replaces the group's current doctrine) and add_rite_tenet / remove_rite_tenet to edit it. Categories, groups
and their order come from doctrine_category_types and doctrine_group_types, so new DLC groups show up on rerun.

Run after a CK3 update:
    python tools/gen_faith_editor.py --game-dir <CK3>/game
or set CK3_GAME_DIR instead of passing the flag.
"""
import argparse
import os
import re
import sys

from ck3parse import child_objects_text, effective_files, entries, top_level_objects

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_REL = os.path.join("common", "scripted_effects", "ucm_acm_faith_editor_data_effects.txt")
REL = os.path.join("common", "religion")
# Doctrine categories the editor shows, in GUI order. GUI list name: ucm_acm_fe_display_<category>.
CATEGORIES = ["main_group", "marriage", "crimes", "clergy"]
KEY = "var:ucm_acm_pick_doctrine_key"


def objects(sub, dirs):
    """[(key, body)] in load order for common/religion/<sub>, later dirs' same-name files winning."""
    return [kb for f in effective_files(os.path.join(REL, sub), *dirs) for kb in top_level_objects(f)]


def field(body, name):
    m = re.search(r"\b%s\s*=\s*(\w+)" % name, body)
    return m and m.group(1)


def traits_of(body):
    """(sins, virtues) from a depth-1 `traits = { sins = {..} virtues = {..} }` block."""
    out = {"sins": [], "virtues": []}
    for k, b in child_objects_text(body):
        if k == "traits":
            for g, gb in child_objects_text(b):
                if g in out:
                    out[g] += entries(gb)
    return out["sins"], out["virtues"]


def load(dirs):
    """dirs: {sub: [dir, ...]} per religion database, so a replace_path can drop vanilla for one of them."""
    groups = {}  # group -> (category, has is_available_on_create), in definition order
    for k, b in objects("doctrine_group_types", dirs["doctrine_group_types"]):
        groups[k] = (field(b, "category"), "is_available_on_create" in b)
    by_group = {g: [] for g in groups}
    traits = {"sins": [], "virtues": []}

    def note(body):
        for lst, ts in zip(("sins", "virtues"), traits_of(body)):
            traits[lst] += [t for t in ts if t not in traits[lst]]

    for k, b in objects("doctrine_types", dirs["doctrine_types"]):
        g = field(b, "doctrine_group_type")
        if g not in by_group:
            sys.exit(f"doctrine {k}: unknown doctrine_group_type {g!r}")
        by_group[g].append((int(field(b, "index") or 0), k))
        note(b)
    tenets = []
    for k, b in objects("tenet_types", dirs["tenet_types"]):
        tenets.append(k)
        note(b)
    for sub in ("religion_types", "faith_types", "rite_types"):
        for _, b in objects(sub, dirs[sub]):
            note(b)
    shown = {c: [(g, [d for _, d in sorted(by_group[g])]) for g, (cat, _) in groups.items() if cat == c and by_group[g]]
             for c in CATEGORIES}
    optional = {g for g, (_, opt) in groups.items() if opt}
    return shown, optional, tenets, traits


def add(lines, ind, name, target):
    lines += [f"{ind}add_to_global_variable_list = {{", f"{ind}  name = {name}", f"{ind}  target = flag:{target}", f"{ind}}}"]


def build(dirs, header):
    shown, optional, tenets, traits = load(dirs)
    L = header + [""]

    # Doctrine library lists (ucm_acm_faith_doctrine_picker.gui).
    L.append("ucm_acm_faith_populate_doctrine_catalog_effect = {")
    for name, items in [("core_tenets", tenets)] + [(c, [d for _, ds in shown[c] for d in ds]) for c in CATEGORIES]:
        L.append(f"  clear_global_variable_list = ucm_acm_doctrine_list_{name}")
        for t in items:
            add(L, "  ", f"ucm_acm_doctrine_list_{name}", t)
    L += ["}", ""]

    # What the selected faith's main rite has now.
    L += ["ucm_acm_faith_refresh_display_lists_effect = {", "  if = {", "    limit = { has_variable = ucm_selected_faith_var }"]
    lists = ["core_tenets"] + CATEGORIES + ["sin_traits", "virtue_traits"]
    L += [f"    clear_global_variable_list = ucm_acm_fe_display_{n}" for n in lists]
    L.append("    var:ucm_selected_faith_var = { main_rite = { save_scope_as = ucm_fe_rite } }")
    for lst, trig in (("sins", "trait_is_sin_rite"), ("virtues", "trait_is_virtue_rite")):
        for t in traits[lst]:
            L += ["    if = {", f"      limit = {{ scope:ucm_fe_rite = {{ {trig} = {t} }} }}"]
            add(L, "      ", f"ucm_acm_fe_display_{lst[:-1]}_traits", t)
            L.append("    }")
    for t in tenets:
        L += ["    if = {", f"      limit = {{ scope:ucm_fe_rite = {{ rite_has_tenet = {t} }} }}"]
        add(L, "      ", "ucm_acm_fe_display_core_tenets", t)
        L.append("    }")
    for c in CATEGORIES:
        for g, ds in shown[c]:
            for i, d in enumerate(ds):
                L += [f"    {'if' if i == 0 else 'else_if'} = {{", f"      limit = {{ scope:ucm_fe_rite = {{ rite_has_doctrine = {d} }} }}"]
                add(L, "      ", f"ucm_acm_fe_display_{c}", d)
                L.append("    }")
            if g not in optional:  # every rite has one; show the first so the group can still be picked
                L.append("    else = {")
                add(L, "      ", f"ucm_acm_fe_display_{c}", ds[0])
                L.append("    }")
    L += ["  }", "}", ""]

    # Picked doctrine or tenet -> its group (flag:doctrine_core_tenets for tenets).
    picks = [("doctrine_core_tenets", tenets)] + [(g, ds) for c in CATEGORIES for g, ds in shown[c]]
    L += ["ucm_acm_faith_resolve_pick_group_effect = {", "  remove_variable = ucm_acm_pick_group_name", "  if = {",
          "    limit = { has_variable = ucm_acm_pick_doctrine_key }"]
    for i, (g, ds) in enumerate(picks):
        L += [f"    {'if' if i == 0 else 'else_if'} = {{", "      limit = {", "        OR = {"]
        L += [f"          {KEY} = flag:{d}" for d in ds]
        L += ["        }", "      }", "      set_variable = {", "        name = ucm_acm_pick_group_name",
              f"        value = flag:{g}", "      }", "    }"]
    L += ["  }", "}", ""]

    # Choices for the picked group.
    L += ["ucm_acm_faith_populate_pick_current_effect = {", "  clear_global_variable_list = ucm_acm_fe_pick_current",
          "  if = {", "    limit = { has_variable = ucm_acm_pick_group_name }"]
    for i, (g, ds) in enumerate(picks):
        L += [f"    {'if' if i == 0 else 'else_if'} = {{", f"      limit = {{ var:ucm_acm_pick_group_name = flag:{g} }}"]
        for d in ds:
            add(L, "      ", "ucm_acm_fe_pick_current", d)
        L.append("    }")
    L += ["  }", "}", ""]

    # Drop the clicked core tenet before the replacement is added.
    L += ["ucm_acm_faith_remove_pick_slot_doctrine_effect = {", "  if = {", "    limit = {",
          "      has_variable = ucm_selected_faith_var", "      has_variable = ucm_acm_pick_slot", "    }"]
    for i, t in enumerate(tenets):
        L += [f"    {'if' if i == 0 else 'else_if'} = {{", f"      limit = {{ var:ucm_acm_pick_slot = flag:{t} }}",
              f"      var:ucm_selected_faith_var = {{ main_rite = {{ remove_rite_tenet = tenet:{t} }} }}", "    }"]
    L += ["  }", "}", ""]

    # Apply the pick: a tenet is added, a doctrine replaces its group's current one.
    L += ["ucm_acm_faith_add_doctrine_to_selected_effect = {", "  if = {", "    limit = {",
          "      has_variable = ucm_selected_faith_var", "      has_variable = ucm_acm_pick_doctrine_key", "    }"]
    first = True
    for eff, ks in (("add_rite_tenet", tenets), ("change_rite_doctrine", [d for _, ds in picks[1:] for d in ds])):
        for k in ks:
            L += [f"    {'if' if first else 'else_if'} = {{", f"      limit = {{ {KEY} = flag:{k} }}",
                  f"      var:ucm_selected_faith_var = {{ main_rite = {{ {eff} = {k} }} }}", "    }"]
            first = False
    L += ["  }", "}", ""]
    return "\n".join(L)


def vanilla_dirs(game):
    subs = ["doctrine_group_types", "doctrine_types", "tenet_types", "religion_types", "faith_types", "rite_types"]
    return {s: [game, MOD_DIR] for s in subs}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))
    print("wrote", os.path.relpath(path, MOD_DIR))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir", default=os.environ.get("CK3_GAME_DIR"), help="CK3 game/ directory (or CK3_GAME_DIR)")
    args = ap.parse_args()
    if not args.game_dir or not os.path.isdir(os.path.join(args.game_dir, REL, "doctrine_group_types")):
        sys.exit(f"--game-dir: no {REL}/doctrine_group_types under {args.game_dir!r}")
    write(os.path.join(MOD_DIR, OUT_REL), build(vanilla_dirs(args.game_dir), [
        "# AUTO-GENERATED by tools/gen_faith_editor.py from the CK3 religion databases. Do not edit; rerun the script.",
        "# compat/ek2/ ships the Elder Kings 2 version of this file.",
    ]))


if __name__ == "__main__":
    main()
