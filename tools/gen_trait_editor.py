"""Generate the trait editor window from the CK3 trait database.

Writes gui/ucm_trait_editor.gui (a category sidebar and one row per trait), the click dispatcher
common/scripted_effects/ucm_trait_editor_generated_effects.txt, and localization/<lang>/ucm_trait_editor_l_<lang>.yml.
The hand-written effects it calls are in common/scripted_effects/ucm_trait_editor_effects.txt.

Traits are the game's own common/traits, minus debug_ traits, plus this mod's CUSTOM traits. A trait with a
`category` goes to that category; the rest go to the categories by EXTENDED below, and anything left over to
genetic_physical (genetic = yes) or misc_other. A new trait category in a CK3 update stops the script: add it to
CATEGORIES and the translations. Adding a trait removes the others in its `group` first.

Run after a CK3 update:
    python tools/gen_trait_editor.py --game-dir <CK3>/game
or set CK3_GAME_DIR instead of passing the flag.
"""
import argparse
import os
import re
import sys

from ck3parse import effective_files, top_level_objects

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUI_REL = os.path.join("gui", "ucm_trait_editor.gui")
EFFECTS_REL = os.path.join("common", "scripted_effects", "ucm_trait_editor_generated_effects.txt")
LOC_NAME = "ucm_trait_editor_l_{0}.yml"
TRAITS = os.path.join("common", "traits")
CATEGORIES = ["childhood", "personality", "education", "commander", "winter_commander", "court_type", "lifestyle",
              "health", "fame", "genetic_physical", "appearance", "intellect", "physique", "fertility",
              "edu_martial_prowess", "edu_republic", "struggle_fp3", "misc_other", "custom"]
# Uncategorized traits: (category, [patterns in display order]); a pattern matches a key prefix.
EXTENDED = [("appearance", ["beauty_"]), ("intellect", ["intellect_", "dull$", "shrewd$"]),
            ("physique", ["physique_", "strong$", "weak$"]), ("fertility", ["fecund$", "impotent$", "infertile$"]),
            ("edu_martial_prowess", ["education_martial_prowess_"]), ("edu_republic", ["education_republican_knowledge_"]),
            ("struggle_fp3", ["fp3_struggle_"]), ("genetic_physical", ["inbred$|pure_blooded$"])]


def plain(trait):
    return f"ucm_trait_editor_toggle_cheat_effect = {{ TRAIT = {trait} }}"


def pill(trait, base):
    return (f"ucm_trait_editor_toggle_age_pill_effect = {{ TRAIT = {trait} FLAG = {base}_active "
            f"AGE_VAR = {base}_original_age }}")


# This mod's traits and what clicking one runs on the target.
CUSTOM = {
    "ucm_trait_immortal_ageless": "ucm_trait_editor_toggle_immortal_effect = yes",
    "ucm_fame_warlord_eternal": plain("ucm_fame_warlord_eternal"),
    "ucm_fame_wealth_sovereign_max": plain("ucm_fame_wealth_sovereign_max"),
    "ucm_fame_ultimate_intrigue_master": plain("ucm_fame_ultimate_intrigue_master"),
    "ucm_fame_great_builder_god": plain("ucm_fame_great_builder_god"),
    "ucm_fame_nether_conspiracy_lord": plain("ucm_fame_nether_conspiracy_lord"),
    "ucm_fame_eternal_nether_lord": plain("ucm_fame_eternal_nether_lord"),
    "ucm_trait_yannian_dan": pill("ucm_trait_yannian_dan", "ucm_yannian_dan"),
    "ucm_trait_yannian_dan_mid": pill("ucm_trait_yannian_dan_mid", "ucm_yannian_dan_mid"),
    "ucm_trait_yannian_dan_best": pill("ucm_trait_yannian_dan_best", "ucm_yannian_dan_best"),
    "ucm_trait_baidubuqin": "ucm_trait_editor_toggle_baidubuqin_effect = yes",
    "ucm_trait_xinwuguai": plain("ucm_trait_xinwuguai"),
    "ucm_trait_stats_100_locked": "ucm_trait_editor_toggle_stats_100_effect = yes",
    "ucm_trait_marriage_ban": "ucm_trait_editor_toggle_marriage_ban_effect = yes",
}

# Window title, then one name per CATEGORIES entry.
LANGS = {
    "english": ("Trait Editor", [
        "Childhood", "Personality", "Education", "Commander", "Winter Commander", "Court Traits", "Lifestyle",
        "Health", "Prestige Traits", "Congenital & Physique", "Appearance", "Intellect", "Physique", "Fertility",
        "Martial Prowess Education", "Republican Knowledge", "FP3 Struggle Traits", "Miscellaneous", "Custom Traits"]),
    "german": ("Eigenschaftseditor", [
        "Kindheitsmerkmale", "Persönlichkeit", "Bildung", "Feldherr", "Winterfeldherr", "Hofmerkmale", "Lebensstil",
        "Gesundheit", "Ruhm", "Angeboren & körperlich", "Aussehen", "Intellekt", "Körperbau", "Fruchtbarkeit",
        "Kampffertigkeitsbildung", "Republikanisches Wissen", "FP3-Konfliktmerkmale", "Sonstige Merkmale",
        "Benutzerdefinierte Merkmale"]),
    "russian": ("Редактор черт", [
        "Детство", "Личность", "Образование", "Командующий", "Зимний командир", "Тип двора", "Образ жизни",
        "Здоровье", "Слава", "Врождённые и физические", "Красота", "Интеллект", "Телосложение", "Плодородие",
        "Воинское образование", "Республиканские знания", "Борьба FP3", "Прочие", "Пользовательские черты"]),
    "simp_chinese": ("特质编辑器", [
        "童年特质", "性格特质", "教育特质", "将领特质", "冬将军", "宫廷类型特质", "生活方式特质",
        "健康特质", "名声特质", "先天与体征", "容貌", "智力", "体格", "生育力",
        "勇武教育", "共和学识", "斗争特质（FP3）", "其他", "自制特质"]),
    "turkish": ("Özellik Düzenleyici", [
        "Çocukluk", "Kişilik", "Eğitim", "Komutan", "Kış Komutanı", "Saray Özellikleri", "Yaşam Tarzı",
        "Sağlık", "Ün", "Doğuştan ve Fiziksel", "Görünüm", "Zeka", "Fizik", "Üreme",
        "Savaş Ustalığı Eğitimi", "Cumhuriyet Bilgisi", "FP3 Mücadele Özellikleri", "Diğer", "Özel Özellikler"]),
}


def load(game):
    """({category: [trait, ...]} in display order, {trait: group}) from the game's own trait files."""
    by = {c: [] for c in CATEGORIES}
    group_of = {}
    for f in effective_files(TRAITS, game):
        for k, b in top_level_objects(f):
            if k.startswith("debug_"):
                continue
            g = re.search(r"(?m)^\s*group\s*=\s*(\w+)", b)
            if g:
                group_of[k] = g.group(1)
            m = re.search(r"(?m)^\s*category\s*=\s*(\w+)", b)
            if m:
                if m.group(1) not in by:
                    sys.exit(f"trait {k}: unknown category {m.group(1)!r}; add it to CATEGORIES")
                by[m.group(1)].append((0, k))
                continue
            for cat, pats in EXTENDED:
                i = next((i for i, p in enumerate(pats) if re.match(p, k)), None)
                if i is not None:
                    by[cat].append((i, k))
                    break
            else:
                genetic = re.search(r"(?m)^\s*genetic\s*=\s*yes", b)
                by["genetic_physical" if genetic else "misc_other"].append((0, k))
    cats = {c: [k for _, k in sorted(ts)] for c, ts in by.items()}
    clash = set(CUSTOM).intersection(t for ts in cats.values() for t in ts)
    if clash:
        sys.exit(f"vanilla now defines {sorted(clash)}: rename them in CUSTOM")
    cats["custom"] = list(CUSTOM)
    return cats, group_of


def groups(group_of):
    """{group: [traits]} for groups with more than one member."""
    out = {}
    for t, g in sorted(group_of.items()):
        out.setdefault(g, []).append(t)
    return {g: ts for g, ts in out.items() if len(ts) > 1}


def build_effects(cats, group_of):
    grouped = groups(group_of)
    L = ["# AUTO-GENERATED by tools/gen_trait_editor.py from the CK3 trait database. Do not edit; rerun the script.", ""]
    for g, ts in grouped.items():
        L += [f"ucm_trait_editor_clear_{g}_effect = {{"]
        L += [f"  ucm_trait_editor_remove_effect = {{ TRAIT = {t} }}" for t in ts]
        L += ["}", ""]
    L += ["# Root = player. scope:trait_flag names the clicked trait; the toggles run on the window's target.",
          "ucm_trait_editor_dispatch_effect = {", "  save_scope_as = actor",
          "  # The shared effects read the target from this global; the rest of the menu keeps its own afterwards.",
          "  if = {", "    limit = { exists = global_var:ucm_cheat_menu_recipient }",
          "    global_var:ucm_cheat_menu_recipient = { save_scope_as = ucm_trait_editor_previous_recipient }", "  }",
          "  set_global_variable = { name = ucm_cheat_menu_recipient value = var:ucm_trait_editor_target }",
          "  ucm_cheat_menu_sync_trait_edit_target_effect = yes", "  scope:ucm_trait_edit_target = {"]
    word = "if"
    for c in CATEGORIES:
        for t in cats[c]:
            g = group_of.get(t)
            if t in CUSTOM:
                call = CUSTOM[t]
            elif g in grouped:
                call = f"ucm_trait_editor_toggle_grouped_effect = {{ TRAIT = {t} CLEAR = ucm_trait_editor_clear_{g}_effect }}"
            else:
                call = f"ucm_trait_editor_toggle_effect = {{ TRAIT = {t} }}"
            L += [f"    {word} = {{", f"      limit = {{ scope:trait_flag = flag:{t} }}", f"      {call}", "    }"]
            word = "else_if"
    L += ["  }", "  if = {", "    limit = { exists = scope:ucm_trait_editor_previous_recipient }",
          "    set_global_variable = { name = ucm_cheat_menu_recipient value = scope:ucm_trait_editor_previous_recipient }",
          "  }", "}"]
    return "\n".join(L) + "\n"


GUI_HEAD = """# AUTO-GENERATED by tools/gen_trait_editor.py from the CK3 trait database. Do not edit; rerun the script.
# Only the open category's rows are live, and they read Character.HasTrait directly: no scripted GUI runs per row.

types ucm_trait_editor_types {
  type ucm_trait_editor_row = button_standard_hover {
    layoutpolicy_horizontal = expanding
    size = { 0 38 }
    down = "[Character.HasTrait(Trait.Self)]"
    tooltipwidget = {
      using = character_trait_tooltip
    }
    hbox = {
      margin = { 8 0 }
      spacing = 8
      icon = {
        size = { 28 28 }
        texture = "[Trait.GetIcon(Character.Self)]"
      }
      text_single = {
        layoutpolicy_horizontal = expanding
        text = "[Trait.GetNameNoTooltip(Character.Self)]"
        default_format = "#clickable"
      }
      text_single = {
        text = "[SelectLocalization(Character.HasTrait(Trait.Self), 'ucm_cheat_menu_trait_minus', 'ucm_cheat_menu_trait_plus')]"
      }
    }
  }

  type ucm_trait_editor_category = button_standard {
    layoutpolicy_horizontal = expanding
    size = { 0 34 }
  }
}

window = {
  name = "ucm_trait_editor_window"
  parentanchor = center
  size = { 980 720 }
  layer = top
  filter_mouse = all
  movable = yes

  widget = {
    size = { 100% 100% }
    background = {
      using = Background_Area_Dark
    }
  }

  visible = "[GetScriptedGui('ucm_trait_editor_visible').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
  datacontext = "[GetVariableSystem]"
  datacontext = "[GetPlayer.MakeScope.Var('ucm_trait_editor_target').Char]"

  state = {
    name = ucm_trait_editor_init
    trigger_on_create = yes
    on_start = "[GetVariableSystem.Set('ucm_trait_editor_category', 'childhood')]"
  }

  vbox = {
    using = Window_Margins
    layoutpolicy_horizontal = expanding
    layoutpolicy_vertical = expanding
    spacing = 6

    header_pattern = {
      layoutpolicy_horizontal = expanding
      blockoverride "header_text" {
        text = "ucm_trait_editor_title"
      }
      blockoverride "button_close" {
        onclick = "[GetScriptedGui('ucm_trait_editor_close').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
      }
    }

    hbox = {
      layoutpolicy_horizontal = expanding
      spacing = 10
      margin = { 4 0 }

      portrait_head_small = {}

      text_single = {
        layoutpolicy_horizontal = expanding
        text = "[Character.GetShortUINameNoTooltip]"
        default_format = "#high"
        align = left|nobaseline
      }
    }

    hbox = {
      layoutpolicy_horizontal = expanding
      layoutpolicy_vertical = expanding
      spacing = 10
"""


def build_gui(cats):
    L = [GUI_HEAD.rstrip("\n"), "", "      scrollbox = {", "        minimumsize = { 220 0 }", "        maximumsize = { 240 -1 }",
         "        layoutpolicy_vertical = expanding", '        blockoverride "scrollbox_content" {', "          vbox = {",
         "            layoutpolicy_horizontal = expanding", "            spacing = 2"]
    for c in CATEGORIES:
        L += ["            ucm_trait_editor_category = {",
              f"""              onclick = "[GetVariableSystem.Set('ucm_trait_editor_category', '{c}')]\"""",
              f"""              down = "[GetVariableSystem.HasValue('ucm_trait_editor_category', '{c}')]\"""",
              f'              text = "ucm_trait_editor_cat_{c}"', "            }"]
    L += ["          }", "        }", "      }", "", "      scrollbox = {", "        layoutpolicy_horizontal = expanding",
          "        layoutpolicy_vertical = expanding", '        blockoverride "scrollbox_content" {']
    for c in CATEGORIES:
        L += ["          vbox = {", "            layoutpolicy_horizontal = expanding", "            spacing = 4",
              f"""            visible = "[GetVariableSystem.HasValue('ucm_trait_editor_category', '{c}')]\""""]
        for t in cats[c]:
            L += ["            ucm_trait_editor_row = {", f"""              datacontext = "[GetTrait('{t}')]\"""",
                  f"""              onclick = "[GetScriptedGui('ucm_trait_editor_toggle').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('trait_flag', MakeScopeFlag('{t}')).End)]\"""",
                  "            }"]
        L += ["          }"]
    L += ["        }", "      }", "    }", "  }", "}"]
    return "\n".join(L) + "\n"


def loc_file(lang, cats):
    title, names = LANGS[lang]
    L = [f"l_{lang}:", f' ucm_trait_editor_title: "{title}"']
    L += [f' ucm_trait_editor_cat_{c}: "{n} ({len(cats[c])})"' for c, n in zip(CATEGORIES, names)]
    L += [' ucm_cheat_menu_trait_minus: "#N −#!"', ' ucm_cheat_menu_trait_plus: "#P +#!"']
    return "\n".join(L) + "\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))
    print("wrote", os.path.relpath(path, MOD_DIR))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir", default=os.environ.get("CK3_GAME_DIR"), help="CK3 game/ directory (or CK3_GAME_DIR)")
    args = ap.parse_args()
    if not args.game_dir or not os.path.isdir(os.path.join(args.game_dir, TRAITS)):
        sys.exit(f"--game-dir: no {TRAITS} under {args.game_dir!r}")
    cats, group_of = load(args.game_dir)
    write(os.path.join(MOD_DIR, GUI_REL), build_gui(cats))
    write(os.path.join(MOD_DIR, EFFECTS_REL), build_effects(cats, group_of))
    for lang in LANGS:
        write(os.path.join(MOD_DIR, "localization", lang, LOC_NAME.format(lang)), loc_file(lang, cats))


if __name__ == "__main__":
    main()
