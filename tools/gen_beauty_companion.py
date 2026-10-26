"""Generate the beauty companion's classified culture picker from REGIONS below and the CK3 culture database.

Writes events/ucm_beauty_companion_classified_generated.txt (region hub 3500, region pages, paged culture
pages) and localization/<lang>/ucm_beauty_companion_classified_generated_l_<lang>.yml (region/subgroup labels
from LABELS, culture labels from the game's own culture names). The classification is hand-curated; cultures the
game no longer defines are dropped with a note. gen_ek2_compatch.py writes the EK2 stub with ek2_stub().

Run after a CK3 update, or after editing REGIONS:
    python tools/gen_beauty_companion.py --game-dir <CK3>/game
or set CK3_GAME_DIR instead of passing the flag.
"""
import argparse
import os
import sys

from ck3parse import effective_files, load_loc, top_level_objects

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_REL = os.path.join("events", "ucm_beauty_companion_classified_generated.txt")
LOC_NAME = "ucm_beauty_companion_classified_generated_l_{0}.yml"
CULTURES = os.path.join("common", "culture", "cultures")
HUB_ID, ID_LIMIT, PAGE_SIZE = 3500, 3600, 7

# (region, [(subgroup, "cultures in display order")])
REGIONS = [
    ("europe", [
        ("eu_germanic", "anglo_saxon english old_saxon frisian dutch frankish swabian bavarian saxon norse swedish norwegian danish icelandic"),
        ("eu_slavic", "russian volhynian severian polish czech pommeranian serbian croatian bulgarian"),
        ("eu_latin", "roman italian cisalpine lombard sicilian occitan french catalan castilian portuguese andalusian"),
        ("eu_celtic", "welsh cornish breton irish gaelic"),
        ("eu_baltic", "lithuanian latgalian prussian"),
        ("eu_balto_finnic", "finnish estonian karelian"),
        ("eu_balkan", "greek vlach albanian"),
    ]),
    ("west_asia", [
        ("wa_arabic", "yemeni bedouin egyptian levantine"),
        ("wa_iranian", "persian tajik khwarezmian kurdish"),
        ("wa_turkic", "turkish turkmen pecheneg khazar"),
        ("wa_berber", "baranis maghrebi butr"),
        ("wa_jewish", "ashkenazi"),
    ]),
    ("central_steppe", [
        ("cs_mongolic", "mongol kipchak"),
        ("cs_tungusic", "jurchen mohe"),
        ("cs_other", "sogdian tocharian"),
    ]),
    ("east_asia", [
        ("ea_chinese", "han hexi heshuo bashu wuyue min chu lingnan"),
        ("ea_northeast", "goryeo japanese ainu"),
        ("ea_tibet", "bodpa zhangzhung"),
    ]),
    ("south_asia", [
        ("sa_indo_aryan", "marathi hindustani rajput bengali"),
        ("sa_dravidian", "tamil telugu kannada"),
        ("sa_lanka", "sinhala"),
    ]),
    ("se_asia", [
        ("sea_mon_khmer", "khmer mon"),
        ("sea_tai", "tai khmu"),
        ("sea_malay_poly", "malay javanese bisayan tagalog"),
    ]),
    ("africa", [
        ("af_west", "soninke malinke songhai yoruba akan"),
        ("af_east", "ethiopian somali"),
        ("af_bantu", "east_bantu laktan"),
    ]),
]

LABELS = {
    "english": {
        "back_regions": "Return to Regions", "back_region": "Return to Subgroups",
        "europe": "European Cultures", "west_asia": "West Asia & North Africa", "central_steppe": "Central Asia & Steppes",
        "east_asia": "East Asia", "south_asia": "South Asia", "se_asia": "Southeast Asia", "africa": "Africa",
        "eu_germanic": "Germanic / Norse", "eu_slavic": "Slavic", "eu_latin": "Latin / Romance", "eu_celtic": "Celtic",
        "eu_baltic": "Baltic", "eu_balto_finnic": "Balto-Finnic", "eu_balkan": "Balkan / Byzantine",
        "wa_arabic": "Arabic", "wa_iranian": "Iranian", "wa_turkic": "Turkic", "wa_berber": "Berber", "wa_jewish": "Jewish",
        "cs_mongolic": "Mongolic", "cs_tungusic": "Tungusic", "cs_other": "Other Steppe Peoples",
        "ea_chinese": "Chinese", "ea_northeast": "Northeast Asia", "ea_tibet": "Tibetan Plateau",
        "sa_indo_aryan": "Indo-Aryan", "sa_dravidian": "Dravidian", "sa_lanka": "Sri Lanka",
        "sea_mon_khmer": "Mon-Khmer", "sea_tai": "Tai", "sea_malay_poly": "Malay-Austronesian",
        "af_west": "West Africa", "af_east": "East Africa", "af_bantu": "Bantu / Southern Africa",
    },
    "german": {
        "back_regions": "Zurück zu den Regionen", "back_region": "Zurück zu den Untergruppen",
        "europe": "Europäische Kulturen", "west_asia": "Westasien & Nordafrika", "central_steppe": "Zentralasien & Steppe",
        "east_asia": "Ostasien", "south_asia": "Südasien", "se_asia": "Südostasien", "africa": "Afrika",
        "eu_germanic": "Germanen / Nordgermanen", "eu_slavic": "Slawen", "eu_latin": "Lateinische / Romanische Völker",
        "eu_celtic": "Kelten", "eu_baltic": "Balten", "eu_balto_finnic": "Balto-Finnen", "eu_balkan": "Balkan / Byzantiner",
        "wa_arabic": "Araber", "wa_iranian": "Iranische Völker", "wa_turkic": "Türkvölker", "wa_berber": "Berber", "wa_jewish": "Juden",
        "cs_mongolic": "Mongolische Völker", "cs_tungusic": "Tungusen", "cs_other": "Weitere Steppenvölker",
        "ea_chinese": "Chinesen", "ea_northeast": "Nordostasiaten", "ea_tibet": "Tibeter",
        "sa_indo_aryan": "Indo-Arier", "sa_dravidian": "Draviden", "sa_lanka": "Sri-Lanker",
        "sea_mon_khmer": "Mon-Khmer-Völker", "sea_tai": "Tai-Völker", "sea_malay_poly": "Malaiisch-Austronesier",
        "af_west": "Westafrika", "af_east": "Ostafrika", "af_bantu": "Bantu / Südafrika",
    },
    "russian": {
        "back_regions": "Вернуться к регионам", "back_region": "Вернуться к подгруппам",
        "europe": "Европейские культуры", "west_asia": "Западная Азия и Северная Африка", "central_steppe": "Центральная Азия и Степь",
        "east_asia": "Восточная Азия", "south_asia": "Южная Азия", "se_asia": "Юго-Восточная Азия", "africa": "Африка",
        "eu_germanic": "Германцы / Скандинавы", "eu_slavic": "Славяне", "eu_latin": "Латиняне / Романские народы",
        "eu_celtic": "Кельты", "eu_baltic": "Балтийцы", "eu_balto_finnic": "Балто-финны", "eu_balkan": "Балканцы / Византийцы",
        "wa_arabic": "Арабы", "wa_iranian": "Иранцы", "wa_turkic": "Тюрки", "wa_berber": "Берберы", "wa_jewish": "Евреи",
        "cs_mongolic": "Монголы", "cs_tungusic": "Тунгусы", "cs_other": "Другие степные народы",
        "ea_chinese": "Китайцы", "ea_northeast": "Северо-Восточная Азия", "ea_tibet": "Тибет",
        "sa_indo_aryan": "Индоарии", "sa_dravidian": "Дравиды", "sa_lanka": "Шри-Ланка",
        "sea_mon_khmer": "Мон-кхмеры", "sea_tai": "Тайцы", "sea_malay_poly": "Малайско-австронезийцы",
        "af_west": "Западная Африка", "af_east": "Восточная Африка", "af_bantu": "Банту / Южная Африка",
    },
    "simp_chinese": {
        "back_regions": "返回七大分区", "back_region": "返回子分类",
        "europe": "欧洲文化组", "west_asia": "西亚与北非", "central_steppe": "中亚与草原",
        "east_asia": "东亚", "south_asia": "南亚", "se_asia": "东南亚", "africa": "非洲",
        "eu_germanic": "日耳曼 / 北日耳曼", "eu_slavic": "斯拉夫", "eu_latin": "拉丁/罗曼", "eu_celtic": "凯尔特",
        "eu_baltic": "波罗的", "eu_balto_finnic": "波罗的-芬兰", "eu_balkan": "巴尔干/东罗马",
        "wa_arabic": "阿拉伯", "wa_iranian": "伊朗", "wa_turkic": "突厥", "wa_berber": "柏柏尔", "wa_jewish": "犹太",
        "cs_mongolic": "蒙古", "cs_tungusic": "通古斯", "cs_other": "其他草原",
        "ea_chinese": "华夏", "ea_northeast": "东北亚", "ea_tibet": "青藏高原",
        "sa_indo_aryan": "印度-雅利安", "sa_dravidian": "达罗毗荼", "sa_lanka": "斯里兰卡",
        "sea_mon_khmer": "孟-高棉", "sea_tai": "傣-泰", "sea_malay_poly": "马来-南岛",
        "af_west": "西非", "af_east": "东非", "af_bantu": "班图/南非",
    },
}

ON = "trigger = { ucm_cheat_menu_menu_enabled_trigger = yes }"
UNFLAG = "scope:ucm_char_gen_target = { remove_character_flag = ucm_companion_picking_culture }"
TO_HUB = "scope:actor = { trigger_event = ucm_cheat_menu.0180 }"


def go(name, eid):
    return f"  option = {{ name = {name} {ON} scope:actor = {{ trigger_event = ucm_cheat_menu.{eid} }} }}"


def leave(name, on=True):
    return f"  option = {{ name = {name}{' ' + ON if on else ''} {UNFLAG} {TO_HUB} }}"


def event(eid, opts):
    return [f"ucm_cheat_menu.{eid} = {{", "  type = character_event", "  title = ucm_cheat_menu.0180.culture_picker_t",
            "  desc = ucm_ui_no_hover_tooltip", "  theme = default", "", "  immediate = {",
            "    ucm_char_gen_sync_recipient_to_scope_effect = yes", "  }", "  right_portrait = scope:ucm_char_gen_target", ""] + opts + ["}", ""]


def regions(game):
    """REGIONS with the cultures the game defines; empty subgroups and regions dropped."""
    known = {k for f in effective_files(CULTURES, game, MOD_DIR) for k, _ in top_level_objects(f)}
    out, gone = [], []
    for r, subs in REGIONS:
        kept = []
        for s, cs in subs:
            gone += [c for c in cs.split() if c not in known]
            if [c for c in cs.split() if c in known]:
                kept.append((s, [c for c in cs.split() if c in known]))
        if kept:
            out.append((r, kept))
    if gone:
        print("  note: cultures no longer in the game, dropped:", ", ".join(gone))
    return out


def build(regs):
    region_ids = {r: HUB_ID + 1 + i for i, (r, _) in enumerate(regs)}
    nxt, pages = HUB_ID + 1 + len(regs), {}
    for _, subs in regs:
        for s, cs in subs:
            chunks = [cs[i:i + PAGE_SIZE] for i in range(0, len(cs), PAGE_SIZE)]
            pages[s] = [(nxt + i, c) for i, c in enumerate(chunks)]
            nxt += len(chunks)
    if nxt > ID_LIMIT:
        sys.exit(f"beauty companion pages ran past ucm_cheat_menu.{ID_LIMIT}")
    L = ["namespace = ucm_cheat_menu", "",
         "## AUTO-GENERATED by tools/gen_beauty_companion.py (REGIONS + the CK3 culture database). Do not edit; rerun the script.", ""]
    L += event(HUB_ID, [go(f"ucm_bc_reg_{r}", region_ids[r]) for r, _ in regs]
               + [leave("ucm_cheat_menu.0180.back_to_hub"), leave("ucm_cheat_menu.00x.close")])
    for r, subs in regs:
        L += event(region_ids[r], [go(f"ucm_bc_sub_{s}", pages[s][0][0]) for s, _ in subs]
                   + [go("ucm_cheat_menu.0180.bc_back_regions", HUB_ID), leave("ucm_cheat_menu.0180.back_to_hub"),
                      leave("ucm_cheat_menu.00x.close")])
        for s, _ in subs:
            ps = pages[s]
            for i, (eid, chunk) in enumerate(ps):
                opts = [f"  option = {{ name = ucm_bc_pick_{c} {ON} scope:ucm_char_gen_target = {{ set_variable = {{ name = "
                        f"ucm_companion_stored_culture value = culture:{c} }} remove_character_flag = ucm_companion_picking_culture }} "
                        f"{TO_HUB} }}" for c in chunk]
                opts += [go("ucm_cheat_menu.page_prev", ps[i - 1][0])] if i else []
                opts += [go("ucm_cheat_menu.page_next", ps[i + 1][0])] if i + 1 < len(ps) else []
                L += event(eid, opts + [go("ucm_cheat_menu.0180.bc_back_region", region_ids[r]), leave("ucm_cheat_menu.00x.close")])
    return "\n".join(L)


def ek2_stub():
    """EK2 has none of these cultures and hides the entry option: keep only .3500, which goes back to .0180."""
    return "\n".join(["namespace = ucm_cheat_menu", "",
                      "## AUTO-GENERATED by tools/gen_ek2_compatch.py (tools/gen_beauty_companion.py). EK2 stub: the vanilla "
                      f"companion culture picker is dropped; only .{HUB_ID} is kept (its entry option is hidden under EK2).", ""]
                     + event(HUB_ID, [leave("ucm_cheat_menu.0180.back_to_hub", on=False), leave("ucm_cheat_menu.00x.close", on=False)]))


def loc_file(lang, regs, names):
    t = LABELS[lang]
    L = [f"l_{lang}:", f' ucm_cheat_menu.0180.bc_back_regions: "{t["back_regions"]}"',
         f' ucm_cheat_menu.0180.bc_back_region: "{t["back_region"]}"']
    L += [f' ucm_bc_reg_{r}: "{t[r]}"' for r, _ in regs]
    L += [f' ucm_bc_sub_{s}: "{t[s]}"' for _, subs in regs for s, _ in subs]
    for c in sorted(c for _, subs in regs for _, cs in subs for c in cs):
        if c not in names:
            sys.exit(f"{lang}: no localization for culture {c}")
        L.append(f' ucm_bc_pick_{c}: "{names[c]}"')
    return "\n".join(L) + "\n"


def write(path, text):
    with open(path, "wb") as fh:
        fh.write(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))
    print("wrote", os.path.relpath(path, MOD_DIR))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game-dir", default=os.environ.get("CK3_GAME_DIR"), help="CK3 game/ directory (or CK3_GAME_DIR)")
    args = ap.parse_args()
    if not args.game_dir or not os.path.isdir(os.path.join(args.game_dir, CULTURES)):
        sys.exit(f"--game-dir: no {CULTURES} under {args.game_dir!r}")
    regs = regions(args.game_dir)
    write(os.path.join(MOD_DIR, OUT_REL), build(regs))
    for lang in LABELS:
        write(os.path.join(MOD_DIR, "localization", lang, LOC_NAME.format(lang)), loc_file(lang, regs, load_loc(lang, args.game_dir)))


if __name__ == "__main__":
    main()
