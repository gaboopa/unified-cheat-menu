"""Regenerate gui/ucm_main_menu.gui, the Unified Cheat Menu window, from TABS below.

Each tab is a list of items:
    ("h", loc_key)        section header
    ("t", loc_key)        note text
    ("sg", sgui)          button running scripted GUI `sgui` (common/scripted_guis/ucm_*.txt);
                          text is loc key `sgui`, tooltip `sgui_tt`
    ("row", [sgui, ...])  the same, as small buttons side by side
    ("ia", interaction)   button opening an existing character interaction on the target;
                          shown/enabled/named exactly as the interaction itself
    ("steps",)            step-size selector (ucm_step_*)
    ("skill", name)       skill row: value, minus and plus (ucm_skill_<name>_down/_up)

Run after editing TABS:
    python tools/gen_ucm_main_menu.py
"""
import os

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(MOD_DIR, "gui", "ucm_main_menu.gui")
R = "GuiScope.SetRoot( GetPlayer.MakeScope ).End"
C = "GetPlayer.MakeScope.Var( 'ucm_target' ).Char"
LATER = ("t", "UCM_TAB_LATER")

TABS = [
    ("quick", [("sg", "ucm_quick_gold"), ("sg", "ucm_quick_prestige"), ("sg", "ucm_quick_piety"), ("sg", "ucm_clear_stress")]),
    ("character", [
        ("h", "UCM_SEC_EDITORS"),
        ("sg", "ucm_open_trait_editor"), ("sg", "ucm_open_cheat_trait_editor"), ("sg", "ucm_open_lifestyle_editor"),
        ("ia", "daddy_pika_edit_character"),
        ("h", "UCM_SEC_IDENTITY"),
        ("ia", "skonester_change_age_interaction"),
        ("row", ["ucm_sexuality_heterosexual", "ucm_sexuality_homosexual", "ucm_sexuality_bisexual", "ucm_sexuality_asexual"]),
        ("ia", "daddy_pika_change_dynasty"), ("ia", "daddy_pika_change_character"),
        ("h", "UCM_SEC_ATTRIBUTES"),
        ("steps",),
        ("skill", "diplomacy"), ("skill", "martial"), ("skill", "stewardship"),
        ("skill", "intrigue"), ("skill", "learning"), ("skill", "prowess"),
        ("row", ["ucm_skill_all_down", "ucm_skill_all_up"]),
        ("row", ["ucm_weight_down", "ucm_weight_up"]),
        ("ia", "daddy_pika_boost_stats"),
        ("h", "UCM_SEC_TRAITS"),
        ("ia", "zhuge_yixue_02"), ("ia", "zhueg_yixue_03"), ("ia", "zhuge_yixue_04"), ("ia", "zhuge_yixue_06"),
        ("h", "UCM_SEC_HEALTH"),
        ("sg", "ucm_clear_stress"),
        ("ia", "zhuge_yixue_01"), ("ia", "zhuge_yixue_05"),
        ("ia", "set_immortal_interaction"), ("ia", "set_mortal_interaction"),
        ("ia", "toc_celibate_interaction"),
        ("h", "UCM_SEC_LIFESTYLE"),
        ("ia", "zhuge_lifexp_all_xp"),
        ("h", "UCM_SEC_PRESETS"),
        ("ia", "set_super_interaction"), ("ia", "set_unsuper_interaction"),
        ("ia", "set_super_governor_interaction"), ("ia", "set_unsuper_governor_interaction"),
        ("ia", "set_super_general_interaction"), ("ia", "set_unsuper_general_interaction"),
        ("ia", "set_all_in_one_interaction"), ("ia", "set_unall_in_one_interaction"),
        ("h", "UCM_SEC_RESOURCES"),
        ("ia", "daddy_pika_character_currency_menu"),
    ]),
    ("relationships", [
        ("h", "UCM_SEC_SECOND"),
        ("sg", "ucm_second_set_target"), ("sg", "ucm_second_clear"),
        ("t", "UCM_SECOND_NOTE"),
        ("h", "UCM_SEC_RELATIONS"),
        ("row", ["ucm_relation_friend", "ucm_relation_best_friend", "ucm_relation_rival"]),
        ("row", ["ucm_relation_nemesis", "ucm_relation_lover", "ucm_relation_soulmate"]),
        ("sg", "ucm_relation_clear"),
        ("ia", "zhuge_set_relation_interaction"),
        ("h", "UCM_SEC_MARRIAGE"),
        ("row", ["ucm_marry_second", "ucm_marry_second_matrilineal"]),
        ("row", ["ucm_betroth_second", "ucm_betroth_second_matrilineal"]),
        ("row", ["ucm_break_betrothal_second", "ucm_divorce_second"]),
        ("ia", "daddy_pika_arrange_marriage_inter"), ("ia", "divorce_character_cheat"), ("ia", "daddy_pika_concubine_cheat"),
        ("h", "UCM_SEC_FAMILY"),
        ("row", ["ucm_second_as_father", "ucm_second_as_real_father", "ucm_second_as_mother"]),
        ("sg", "ucm_join_second_house"),
        ("ia", "daddy_pika_adopt_m"), ("ia", "daddy_pika_adopt_f"), ("ia", "daddy_pika_disown"),
        ("ia", "daddy_pika_designate_heir"), ("ia", "toc_setheira_interaction"), ("ia", "toc_disinherit_interaction"),
        ("ia", "daddy_pika_extermination_process"),
        ("h", "UCM_SEC_PREGNANCY"),
        ("row", ["ucm_pregnant_by_second_1", "ucm_pregnant_by_second_2", "ucm_pregnant_by_second_3"]),
        ("sg", "ucm_end_pregnancy"),
        ("ia", "toc_pregnancy_interaction"),
        ("h", "UCM_SEC_HOOKS"),
        ("row", ["ucm_second_hook_on_target", "ucm_target_hook_on_second"]),
        ("ia", "daddy_pika_add_strong_hook"),
        ("row", ["ucm_learn_target_secrets", "ucm_expose_target_secrets"]),
    ]),
    ("titles", [LATER]),
    ("faith_culture", [("sg", "ucm_open_culture_picker"), ("sg", "ucm_open_religion_picker"), ("sg", "ucm_open_tradition_picker"), LATER]),
    ("realm", [("sg", "ucm_group_sub_realm_max_development"), ("sg", "ucm_group_sub_realm_max_control"), LATER]),
    ("military", [("sg", "ucm_open_army_spawner"), LATER]),
    ("artifacts", [("sg", "ucm_open_artifact_crafter"), ("sg", "ucm_open_artifact_repair"), LATER]),
    ("court", [("sg", "ucm_group_courtiers_clear_stress"), LATER]),
    ("dlc", [LATER]),
    ("settings", [("sg", "ucm_open_console_helper"), ("sg", "ucm_second_clear")]),
]


def tab_shown(t):
    if t == "quick":
        return "[Or( GetVariableSystem.HasValue( 'ucm_tab', 'quick' ), Not( GetVariableSystem.Exists( 'ucm_tab' ) ) )]"
    return f"[GetVariableSystem.HasValue( 'ucm_tab', '{t}' )]"


def sgui_button(name, ind, width="0", expand=True):
    return [
        f"{ind}button_standard = {{",
        *([f"{ind}  layoutpolicy_horizontal = expanding"] if expand else []),
        f"{ind}  size = {{ {width} 30 }}",
        f'{ind}  text = "{name}"',
        f'{ind}  tooltip = "{name}_tt"',
        f"{ind}  enabled = \"[GetScriptedGui( '{name}' ).IsValid( {R} )]\"",
        f"{ind}  onclick = \"[GetScriptedGui( '{name}' ).Execute( {R} )]\"",
        f"{ind}}}",
    ]


def item(it, ind):
    kind = it[0]
    if kind == "h":
        return [f'{ind}text_single = {{ layoutpolicy_horizontal = expanding text = "{it[1]}" using = Font_Size_Medium default_format = "#high" }}']
    if kind == "t":
        return [f'{ind}text_multi = {{ layoutpolicy_horizontal = expanding autoresize = yes max_width = 460 text = "{it[1]}" default_format = "#low" }}']
    if kind == "sg":
        return sgui_button(it[1], ind)
    if kind == "row":
        lines = [f"{ind}hbox = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  spacing = 4"]
        for name in it[1]:
            lines += sgui_button(name, ind + "  ")
        return lines + [f"{ind}}}"]
    if kind == "ia":
        k = it[1]
        return [
            f"{ind}button_standard = {{",
            f"{ind}  layoutpolicy_horizontal = expanding",
            f"{ind}  size = {{ 0 30 }}",
            f"{ind}  visible = \"[{C}.IsPlayerInteractionShown( '{k}' )]\"",
            f"{ind}  enabled = \"[{C}.IsPlayerInteractionValid( '{k}' )]\"",
            f"{ind}  text = \"[{C}.GetPlayerInteractionName( '{k}' )]\"",
            f"{ind}  tooltip = \"[{C}.GetPlayerInteractionTooltip( '{k}' )]\"",
            f"{ind}  onclick = \"[{C}.OpenPlayerInteraction( '{k}' )]\"",
            f"{ind}}}",
        ]
    if kind == "steps":
        lines = [f"{ind}hbox = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  spacing = 4",
                 f'{ind}  text_single = {{ text = "UCM_STEP_LABEL" }}']
        for n in (1, 5, 10, 25, 100):
            lines += sgui_button(f"ucm_step_{n}", ind + "  ", "56", expand=False)
        return lines + [f"{ind}  expand = {{}}", f"{ind}}}"]
    if kind == "skill":
        s = it[1]
        return [
            f"{ind}hbox = {{",
            f"{ind}  layoutpolicy_horizontal = expanding",
            f"{ind}  spacing = 4",
            f'{ind}  text_single = {{ size = {{ 140 30 }} text = "UCM_SKILL_{s.upper()}" }}',
            f"{ind}  text_single = {{ size = {{ 50 30 }} raw_text = \"[{C}.GetSkill( '{s}' )]\" default_format = \"#high\" }}",
            *sgui_button(f"ucm_skill_{s}_down", ind + "  ", "56", expand=False),
            *sgui_button(f"ucm_skill_{s}_up", ind + "  ", "56", expand=False),
            f"{ind}  expand = {{}}",
            f"{ind}}}",
        ]
    raise ValueError(it)


def main():
    o = [
        "# AUTO-GENERATED by tools/gen_ucm_main_menu.py; edit TABS there, not this file.",
        "# Unified Cheat Menu main menu (spec Section 2, Layer 2), opened by the ucm_open_cheat_menu interaction.",
        "# Tabs are GUI-only state (GetVariableSystem 'ucm_tab').",
        "window = {",
        '  name = "ucm_main_menu_window"',
        "  parentanchor = center",
        "  size = { 780 680 }",
        "  layer = top",
        "  movable = yes",
        "  alwaystransparent = no",
        "  filter_mouse = all",
        f"  visible = \"[GetScriptedGui( 'ucm_menu_visible' ).IsShown( {R} )]\"",
        "",
        "  widget = {",
        "    size = { 100% 100% }",
        "    background = { using = Background_Area_Dark alpha = 1.0 }",
        "  }",
        "",
        "  vbox = {",
        "    using = Window_Margins",
        "    layoutpolicy_horizontal = expanding",
        "    layoutpolicy_vertical = expanding",
        "    spacing = 8",
        "",
        "    header_pattern = {",
        "      layoutpolicy_horizontal = expanding",
        '      blockoverride "header_text" { text = "UCM_MENU_TITLE" }',
        f"      blockoverride \"button_close\" {{ onclick = \"[GetScriptedGui( 'ucm_menu_close' ).Execute( {R} )]\" }}",
        "    }",
        "",
        '    text_single = { layoutpolicy_horizontal = expanding text = "UCM_MENU_TARGET" }',
        "    text_single = {",
        "      layoutpolicy_horizontal = expanding",
        "      visible = \"[GetGlobalVariable( 'skonester_crozier_cheats_other' ).IsSet]\"",
        '      text = "UCM_MENU_SECOND"',
        "    }",
        "    text_single = {",
        "      layoutpolicy_horizontal = expanding",
        "      visible = \"[Not( GetGlobalVariable( 'skonester_crozier_cheats_other' ).IsSet )]\"",
        '      text = "UCM_MENU_SECOND_NONE"',
        '      default_format = "#low"',
        "    }",
        "",
        "    hbox = {",
        "      layoutpolicy_horizontal = expanding",
        "      layoutpolicy_vertical = expanding",
        "      spacing = 12",
        "",
        "      # Category tabs",
        "      vbox = {",
        "        layoutpolicy_vertical = expanding",
        "        spacing = 4",
    ]
    for t, _ in TABS:
        o += [
            "        button_standard = {",
            "          size = { 220 34 }",
            f'          text = "UCM_TAB_{t.upper()}"',
            f'          down = "{tab_shown(t)}"',
            f"          onclick = \"[GetVariableSystem.Set( 'ucm_tab', '{t}' )]\"",
            "        }",
        ]
    o += ["        expand = {}", "      }", "", "      # Category contents"]
    for t, items in TABS:
        o += [
            "      scrollbox = {",
            "        size = { 500 540 }",
            f'        visible = "{tab_shown(t)}"',
            '        blockoverride "scrollbox_content" {',
            "          vbox = {",
            "            layoutpolicy_horizontal = expanding",
            "            spacing = 4",
            f'            text_single = {{ layoutpolicy_horizontal = expanding text = "UCM_TAB_{t.upper()}" using = Font_Size_Big default_format = "#high" }}',
        ]
        for it in items:
            o += item(it, "            ")
        o += ["          }", "        }", "      }"]
    o += ["    }", "  }", "}"]
    with open(OUT, "wb") as fh:
        fh.write(b"\xef\xbb\xbf" + ("\r\n".join(o) + "\r\n").encode("utf-8"))
    print(f"{sum(len(i) for _, i in TABS)} items -> {os.path.relpath(OUT, MOD_DIR)}")


if __name__ == "__main__":
    main()
