"""Generate the classic-menu base-game trait editor from the CK3 trait database.

Writes events/ucm_cheat_menu_trait_editor_generated.txt (category hub 0100/0196/0288/0289 and the paged trait
lists from 9000) and localization/<lang>/ucm_officials_trait_editor_gen_l_<lang>.yml (hub/category text with
trait counts, page titles, and one toggle label per trait).

Traits are the game's own common/traits (not this mod's or other mods'), minus debug_ traits. A trait with a
`category` goes to that category; the rest go to the extended categories by EXTENDED below, and anything left
over to genetic_physical (genetic = yes) or misc_other. A new trait category in a CK3 update stops the script:
add it to CATEGORIES and the translations.

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
OUT_REL = os.path.join("events", "ucm_cheat_menu_trait_editor_generated.txt")
LOC_NAME = "ucm_officials_trait_editor_gen_l_{0}.yml"
TRAITS = os.path.join("common", "traits")
PAGE_SIZE, FIRST_ID, ID_LIMIT = 7, 9000, 9100
# (hub event, [categories] it opens); category pages go back to their hub. The vanilla ones (0100/0196) show a count.
HUBS = [("0100", ["childhood", "personality", "education", "commander", "winter_commander"]),
        ("0196", ["court_type", "lifestyle", "health", "fame"]),
        ("0288", ["genetic_physical", "appearance", "intellect", "physique"]),
        ("0289", ["fertility", "edu_martial_prowess", "edu_republic", "struggle_fp3", "misc_other"])]
CATEGORIES = [c for _, cs in HUBS for c in cs]
COUNTED = set(HUBS[0][1] + HUBS[1][1])
# Uncategorized traits: (extended category, [patterns in display order]); a pattern matches a key prefix.
EXTENDED = [("appearance", ["beauty_"]), ("intellect", ["intellect_", "dull$", "shrewd$"]),
            ("physique", ["physique_", "strong$", "weak$"]), ("fertility", ["fecund$", "impotent$", "infertile$"]),
            ("edu_martial_prowess", ["education_martial_prowess_"]), ("edu_republic", ["education_republican_knowledge_"]),
            ("struggle_fp3", ["fp3_struggle_"]), ("genetic_physical", ["inbred$|pure_blooded$"])]

LANGS = {
    "english": dict(
        page="{0} (Page {1}/{2})", count="{0} ({1})",
        head={
            "ucm_trait_gui_window_title": "Base Game Traits",
            "ucm_cheat_trait_gui_window_title": "Custom Traits",
            "ucm_cheat_menu.0100.t": "Base Game Traits - Categories",
            "ucm_cheat_menu.0100.desc": "(Page 1) Categories I–V. Toggle traits to add or remove them. Maximum 11 entries per page. Warning: Personality, Education and Lifestyle traits affect numerous game mechanics.",
        },
        tail={
            "ucm_cheat_menu.0196.desc": "(Page 2) Categories VI–IX. Use extended categories for congenital traits, appearance, martial prowess and more.",
            "ucm_cheat_menu.0196.more_categories": "Extended Categories (Congenital · Appearance · Prowess …)",
            "ucm_cheat_menu.0288.t": "Base Traits - Extended Categories (1/2)",
            "ucm_cheat_menu.0289.t": "Base Traits - Extended Categories (2/2)",
            "ucm_cheat_menu.0288.desc": "Extended Categories (1/2): Congenital, Appearance, Intellect, Physique. Click an entry to toggle the corresponding trait.",
            "ucm_cheat_menu.0289.desc": "Extended Categories (2/2): Fertility, Martial Prowess Education, Republican Knowledge, FP3 Struggle, Miscellaneous.",
            "ucm_cheat_menu.0101.t": "Base Game Traits",
        },
        cats=["I. Childhood", "II. Personality", "III. Education", "IV. Commander", "V. Winter Commander",
              "VI. Court Traits", "VII. Lifestyle", "VIII. Health", "IX. Prestige Traits",
              "X. Congenital & Physique Traits", "XI. Appearance", "XII. Intellect", "XIII. Physique",
              "XIV. Fertility", "XV. Martial Prowess Education", "XVI. Republican Knowledge",
              "XVII. FP3 Struggle Traits", "XVIII. Miscellaneous"],
    ),
    "german": dict(
        page="{0} (Seite {1}/{2})", count="{0} ({1})",
        head={
            "ucm_trait_gui_window_title": "Basisspiel-Merkmale",
            "ucm_cheat_trait_gui_window_title": "Benutzerdefinierte Merkmale",
            "ucm_cheat_menu.0100.t": "Basisspiel-Merkmale (Kategorien)",
            "ucm_cheat_menu.0100.desc": "(Seite 1) Kategorien I–V. Merkmale umschalten (entfernen, falls vorhanden / hinzufügen, falls nicht vorhanden). Maximal 11 Optionen pro Seite. Hinweis: Persönlichkeit, Bildung und Lebensstil beeinflussen zahlreiche Spielsysteme.",
        },
        tail={
            "ucm_cheat_menu.0196.desc": "(Seite 2) Kategorien VI–IX; Weitere Kategorien für angeborene Merkmale, Aussehen, Kampffertigkeiten und mehr.",
            "ucm_cheat_menu.0196.more_categories": "Weitere Kategorien (Angeboren · Aussehen · Kampffertigkeit ...)",
            "ucm_cheat_menu.0288.t": "Basismerkmale · Weitere Kategorien (1/2)",
            "ucm_cheat_menu.0289.t": "Basismerkmale · Weitere Kategorien (2/2)",
            "ucm_cheat_menu.0288.desc": "Weitere Kategorien (1/2): Angeborene Merkmale, Aussehen, Intellekt, Körperbau. Wähle eine Kategorie zum Bearbeiten der Merkmale.",
            "ucm_cheat_menu.0289.desc": "Weitere Kategorien (2/2): Fruchtbarkeit, Kampffertigkeitsbildung, republikanisches Wissen, FP3-Konflikt, Sonstiges.",
            "ucm_cheat_menu.0101.t": "Basisspiel-Merkmale",
        },
        cats=["I. Kindheitsmerkmale", "II. Persönlichkeit", "III. Bildung", "IV. Feldherr", "V. Winterfeldherr",
              "VI. Hofmerkmale", "VII. Lebensstil", "VIII. Gesundheit", "IX. Ruhm",
              "X. Angeborene & körperliche Merkmale", "XI. Aussehen", "XII. Intellekt", "XIII. Körperbau",
              "XIV. Fruchtbarkeit", "XV. Kampffertigkeitsbildung", "XVI. Republikanisches Wissen",
              "XVII. FP3-Konfliktmerkmale", "XVIII. Sonstige Merkmale"],
    ),
    "russian": dict(
        page="{0} (стр. {1}/{2})", count="{0} ({1})",
        head={
            "ucm_trait_gui_window_title": "Игровые особенности",
            "ucm_cheat_trait_gui_window_title": "Пользовательские черты",
            "ucm_cheat_menu.0100.t": "Игровые особенности (категории)",
            "ucm_cheat_menu.0100.desc": "(Страница 1) Категории I-V. Черты переключателей (удалить, если они присутствуют, добавить, если их нет). Макс 11 опций на странице. Предупреждение: Личность/Образование/Стиль жизни влияют на многие системы.",
        },
        tail={
            "ucm_cheat_menu.0196.desc": "(Страница 2) Категории VI-IX; используйте дополнительные категории для врожденных/красивых/военных линий мастерства и т.д.",
            "ucm_cheat_menu.0196.more_categories": "Больше категорий (врожденная · красота · доблесть ...)",
            "ucm_cheat_menu.0288.t": "Базовые черты · Больше категорий (1/2)",
            "ucm_cheat_menu.0289.t": "Базовые черты · Больше категорий (2/2)",
            "ucm_cheat_menu.0288.desc": "Больше категорий (1/2): врожденная, красота, интеллект, телосложение. Откройте ряд, чтобы переключать черты.",
            "ucm_cheat_menu.0289.desc": "Больше категорий (2/2): фертильность, военное образование, республиканские знания, борьба FP3, другие.",
            "ucm_cheat_menu.0101.t": "Игровые черты Base Game",
        },
        cats=["I. Детство", "II. Личность", "III. Образование", "IV. Командующий", "V. Зимний командир",
              "VI. Тип суда", "VII. Образ жизни", "VIII. Здоровье", "IX. Слава",
              "X. Врожденные и физические черты", "XI. Красота", "XII. Интеллект", "XIII. Физика",
              "XIV. Плодородие", "XV. Воинское мастерство в образовании", "XVI. Республиканские знания",
              "XVII. Борьба FP3", "XVIII. Прочие"],
    ),
    "simp_chinese": dict(
        page="{0}（第 {1}/{2} 页）", count="{0}（{1}）",
        head={
            "ucm_trait_gui_window_title": "本体特质",
            "ucm_cheat_trait_gui_window_title": "自制特质",
            "ucm_cheat_menu.0100.t": "本体特质（分类）",
            "ucm_cheat_menu.0100.desc": "（第 1 页）按一至五类浏览并开关本体特质（有则移除，无则授予）。每页最多 11 个选项。注意：性格/教育/生活方式等会影响大量系统，乱改可能导致 AI/事件异常。",
        },
        tail={
            "ucm_cheat_menu.0196.desc": "（第 2 页）六至九类；另有「更多分类」含先天/容貌/勇武教育等。每页最多 11 个选项。",
            "ucm_cheat_menu.0196.more_categories": "更多分类（先天·容貌·勇武教育…）",
            "ucm_cheat_menu.0288.t": "本体特质 · 更多分类（1/2）",
            "ucm_cheat_menu.0289.t": "本体特质 · 更多分类（2/2）",
            "ucm_cheat_menu.0288.desc": "更多分类第 1 页：先天与体征、容貌、智力、体格。点击选项进入对应特质列表；有则移除，无则授予。",
            "ucm_cheat_menu.0289.desc": "更多分类第 2 页：生育力、勇武教育、共和学识、斗争特质（FP3）及其他。点击选项进入列表开关特质。",
            "ucm_cheat_menu.0101.t": "本体特质",
        },
        cats=["一、童年特质", "二、性格特质", "三、教育特质", "四、将领特质", "五、冬将军",
              "六、宫廷类型特质", "七、生活方式特质", "八、健康特质", "九、名声特质",
              "十、先天与体征", "十一、容貌", "十二、智力", "十三、体格",
              "十四、生育力", "十五、勇武教育", "十六、共和学识",
              "十七、斗争特质（FP3）", "十八、其他"],
    ),
}


def load(game):
    """{category: [trait, ...]} in display order, from the game's own trait files only."""
    by = {c: [] for c in CATEGORIES}
    for f in effective_files(TRAITS, game):
        for k, b in top_level_objects(f):
            if k.startswith("debug_"):
                continue
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
    return {c: [k for _, k in sorted(ts)] for c, ts in by.items()}


def option(name, *body):
    return ["  option = {", f"    name = {name}"] + [f"    {line}" for line in body] + ["  }"]


def go(eid):
    return f"scope:actor = {{ trigger_event = ucm_cheat_menu.{eid} }}"


def event(eid, title, desc, opts):
    return [f"ucm_cheat_menu.{eid} = {{", "  type = character_event", f"  title = ucm_cheat_menu.{title}",
            f"  desc = ucm_cheat_menu.{desc}", "  theme = learning", "  right_portrait = scope:ucm_trait_edit_target", "",
            "  immediate = {", "    ucm_cheat_menu_sync_trait_edit_target_effect = yes", "  }", ""] + opts + ["}"]


def pages(items):
    return [items[i:i + PAGE_SIZE] for i in range(0, len(items), PAGE_SIZE)] or [[]]


def build(cats):
    first, nxt = {}, FIRST_ID
    for c in CATEGORIES:
        first[c], nxt = nxt, nxt + len(pages(cats[c]))
    if nxt > ID_LIMIT:
        sys.exit(f"trait pages ran past ucm_cheat_menu.{ID_LIMIT}")
    L = ["namespace = ucm_cheat_menu", "",
         "## AUTO-GENERATED by tools/gen_trait_editor.py from the CK3 trait database. Do not edit; rerun the script.",
         f"## Hub: 0100/0196 (categories I-IX), 0288/0289 (extended). Page size: {PAGE_SIZE}", ""]
    cat_opts = {c: option(f"ucm_cheat_menu.0100.cat_{c}", go(first[c])) for c in CATEGORIES}
    back = option("ucm_cheat_menu.0100.back", go("0110"))
    close = option("ucm_cheat_menu.0100.close")
    back_main = option("ucm_cheat_menu.0288.back_main", go("0196"))
    cats_of = {hub: [o for c in cs for o in cat_opts[c]] for hub, cs in HUBS}
    hubs = {"0100": cats_of["0100"] + option("ucm_cheat_menu.page_next", go("0196")) + back + close,
            "0196": cats_of["0196"] + option("ucm_cheat_menu.0196.more_categories", go("0288"))
            + option("ucm_cheat_menu.page_prev", go("0100")) + back + close,
            "0288": cats_of["0288"] + option("ucm_cheat_menu.page_next", go("0289")) + back_main + close,
            "0289": option("ucm_cheat_menu.page_prev", go("0288")) + cats_of["0289"] + back_main + close}
    for eid, opts in hubs.items():
        L += event(eid, "0100.t" if eid in ("0100", "0196") else f"{eid}.t", f"{eid}.desc", opts)
    for hub, cs in HUBS:
        for c in cs:
            ps = pages(cats[c])
            for i, chunk in enumerate(ps):
                eid = first[c] + i
                opts = [o for t in chunk for o in option(f"ucm_cheat_menu_trait_opt_{t}", "ucm_cheat_menu_sync_trait_edit_target_effect = yes",
                                                         f"ucm_cheat_menu_toggle_base_trait_effect = {{ TRAIT = {t} }}", go(eid))]
                if i:
                    opts += option("ucm_cheat_menu.page_prev", go(eid - 1))
                if i + 1 < len(ps):
                    opts += option("ucm_cheat_menu.page_next", go(eid + 1))
                opts += option("ucm_cheat_menu.0101.back", go(hub)) + option("ucm_cheat_menu.0101.close")
                L += event(eid, "0101.t", f"0101.desc_{c}_{i + 1}", opts)
    return "\n".join(L) + "\n"


def loc_file(lang, cats):
    t = LANGS[lang]
    label = {c: t["count"].format(name, len(cats[c])) if c in COUNTED else name for c, name in zip(CATEGORIES, t["cats"])}
    L = [f"l_{lang}:"] + [f' {k}: "{v}"' for k, v in t["head"].items()]
    L += [f' ucm_cheat_menu.0100.cat_{c}: "{label[c]}"' for c in CATEGORIES]
    L += [f' {k}: "{v}"' for k, v in t["tail"].items()]
    for c in CATEGORIES:
        n = len(pages(cats[c]))
        L += [f' ucm_cheat_menu.0101.desc_{c}_{i}: "{t["page"].format(label[c], i, n)}"' for i in range(1, n + 1)]
    L += [' ucm_cheat_menu_trait_minus: "#N −#!"', ' ucm_cheat_menu_trait_plus: "#P +#!"']
    for tr in sorted(tr for ts in cats.values() for tr in ts):
        g = f"GetTrait('{tr}')"
        L.append(f' ucm_cheat_menu_trait_opt_{tr}: "[{g}.GetName( ucm_trait_edit_target )][{g}.GetTextIcon][{g}.GetIcon] '
                 f"[SelectLocalization( ucm_trait_edit_target.HasTrait( {g} ), 'ucm_cheat_menu_trait_minus', 'ucm_cheat_menu_trait_plus' )]\"")
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
    cats = load(args.game_dir)
    write(os.path.join(MOD_DIR, OUT_REL), build(cats))
    for lang in LANGS:
        write(os.path.join(MOD_DIR, "localization", lang, LOC_NAME.format(lang)), loc_file(lang, cats))


if __name__ == "__main__":
    main()
