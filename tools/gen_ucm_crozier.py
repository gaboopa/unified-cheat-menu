"""Regenerate the always-on toggles and one-shot actions shown in the Quick, Military, Artifacts, Court
and DLC tabs: common/scripted_effects/ucm_crozier_cheats_effects.txt, common/scripted_guis/
ucm_crozier_cheats_scripted_guis.txt and common/modifiers/ucm_crozier_cheats_modifiers.txt.

Button naming, which tools/gen_ucm_main_menu.py relies on: tog_<toggle>, do_<action> (acts on the player)
and t_<action> (acts on the menu target). Localization: UCM_CROZIER_CHEATS_B_<action>[_TT] with the leading
do_/t_ dropped, likewise ucm_crozier_cheats_toast_<action>.

Run after editing the tables:
    python tools/gen_ucm_crozier.py
"""
import os

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "ucm_crozier_cheats"
T = f"scope:{P}_char"
STRENGTHS = (1, 2, 5, 10, 25, 100, 1000)  # multiplier of each ucm_crozier_cheats_power level
SKILLS = ("diplomacy", "martial", "stewardship", "intrigue", "learning", "prowess")
DISEASES = ("bubonic_plague", "cancer", "consumption", "dysentery", "early_great_pox", "ergotism", "gout_ridden", "great_pox",
            "ill", "leper", "lovers_pox", "measles", "pneumonic", "sickly", "smallpox", "typhus")
EPIDEMICS = ("bubonic_plague", "smallpox", "typhus", "consumption", "measles", "dysentery", "ergotism")
COUNCIL = ("chancellor", "steward", "marshal", "spymaster", "court_chaplain")
COURT = ("court_physician", "bodyguard", "champion", "court_tutor", "master_assassin", "royal_architect")

# Toggles scaled by the strength buttons: modifier stats at strength 1.
LEVELLED = {
    "health": {"health": 50},
    "skills": dict.fromkeys(SKILLS, 50),
    "income": {"monthly_income_mult": 4},
    "domain": {"domain_limit": 50},
    "vassals": {"vassal_limit": 100},
    "prestige": {"monthly_prestige": 100},
    "piety": {"monthly_piety": 100},
    "monthly_gold": {"monthly_income": 10},
    "renown": {"monthly_dynasty_prestige": 5},
    "slots": {"building_slot_add": 1},
    "influence": {"monthly_influence": 5},
    "lifestyle_xp": {"monthly_lifestyle_xp_gain_mult": 1},
    "levy": {"levy_size": 1},
    "life": {"life_expectancy": 10},
    "prestige_mult": {"monthly_prestige_gain_mult": 1, "monthly_piety_gain_mult": 1},
    "renown_mult": {"monthly_dynasty_prestige_mult": 1},
    "innovation": {"cultural_head_fascination_mult": 1},
    "legit_gain": {"monthly_legitimacy_add": 1, "legitimacy_gain_mult": 1},
    "travel_safe": {"character_travel_safety_mult": 1, "character_travel_speed_mult": 1},
    "merit_gain": {"monthly_merit_mult": 1},
    "skills_mult": {f"{s}_mult": 0.5 for s in SKILLS},
    "long_reign": {"long_reign_bonus_mult": 1},
    "legend_spread": {"owned_legend_spread_mult": 1},
}
# Other toggles: (run on the player while on, run on each past holder when lost). Holders go in a global list.
HELD = {
    "stress": (
        f"if = {{ limit = {{ NOT = {{ has_character_modifier = {P}_stress }} }} add_character_modifier = {{ modifier = {P}_stress }} add_to_global_variable_list = {{ name = {P}_h_stress target = this }} }}",
        f"remove_character_modifier = {P}_stress",
    ),
    "immortal_player": (
        f"if = {{ limit = {{ NOT = {{ has_trait = immortal }} }} add_trait = immortal {P}_immortal_restore = yes add_to_global_variable_list = {{ name = {P}_h_immortal_player target = this }} }}",
        "remove_trait = immortal",
    ),
    "disease_player": (
        f"if = {{ limit = {{ NOT = {{ has_trait = {P}_disease_shield }} }} add_trait = {P}_disease_shield add_to_global_variable_list = {{ name = {P}_h_disease_player target = this }} }} "
        + " ".join(f"remove_trait = {d}" for d in DISEASES),
        f"remove_trait = {P}_disease_shield",
    ),
    "auto_gold_floor": ("if = { limit = { gold < 1000 } add_gold = { value = 1000 subtract = gold } }", ""),
    "auto_prestige_floor": ("if = { limit = { prestige < 1000 } add_prestige = { value = 1000 subtract = prestige } } if = { limit = { piety < 1000 } add_piety = { value = 1000 subtract = piety } }", ""),
    "auto_no_prison": ("if = { limit = { is_imprisoned = yes } release_from_prison = yes }", ""),
    "auto_ascension": (
        f"if = {{ limit = {{ NOT = {{ has_character_flag = {P}_ascended }} }} add_character_flag = {P}_ascended add_trait = intellect_good_3 add_trait = physique_good_3 add_trait = beauty_good_3 "
        + " ".join(f"add_{s}_skill = 5" for s in SKILLS) + " }",
        "",
    ),
    "auto_forever_young": ("if = { limit = { age > 30 } set_age = 30 }", ""),
}
TOGGLES = [*LEVELLED, *HELD]
GRANT_OVERRIDE = {
    "life": f"{P}_lv_add = {{ KEY = life }} every_spouse = {{ limit = {{ is_alive = yes }} {P}_lv_add = {{ KEY = life }} }} every_child = {{ limit = {{ is_alive = yes }} {P}_lv_add = {{ KEY = life }} }}",
}

# One-shot buttons: name -> (is_valid or "", effect). Root is the player, T the menu target.
UNPROTECTED = f"{T} = {{ {P}_target_unprotected_trigger = yes }}"
EMPLOYED_ADULT = f"{T} = {{ employer ?= root is_adult = yes }}"
OPPOSITE_SEX = f"OR = {{ AND = {{ {T} = {{ is_female = yes }} root = {{ is_female = no }} }} AND = {{ {T} = {{ is_female = no }} root = {{ is_female = yes }} }} }}"
BEST_GENES = "trait = intellect_good_3 trait = physique_good_3 trait = beauty_good_3"
NEWBORN = f"age = 0 employer = root dynasty = inherit ethnicity = parents gender_female_chance = 50 {BEST_GENES}"
ACTIONS = {
    "do_freq_week": ("", f"set_global_variable = {{ name = {P}_freq value = 1 }}"),
    "do_freq_month": ("", f"set_global_variable = {{ name = {P}_freq value = 2 }}"),
    "do_freq_quarter": ("", f"set_global_variable = {{ name = {P}_freq value = 3 }}"),
    "do_combo_army": ("", f"{P}_combo_army = yes"),
    "do_forge_crown": ("", f"create_artifact = {{ name = {P}_art_crown_name description = {P}_art_crown_desc creator = root type = regalia visuals = crown rarity = illustrious wealth = 100 quality = 100 max_durability = 1000 decaying = no modifier = {P}_art_crown generate_history = no }}"),
    "do_travel_arrive": ("", "if = { limit = { is_travelling = yes exists = current_travel_plan } current_travel_plan = { complete_travel_plan = yes } }"),
    "t_t_execute": (UNPROTECTED, f"{T} = {{ death = {{ death_reason = death_execution killer = root }} }}"),
    "t_t_depose": (f"{T} = {{ is_ruler = yes }} {UNPROTECTED}", f"{T} = {{ depose = yes }}"),
    "t_t_banish": (f"{T} = {{ employer ?= root }} {UNPROTECTED}", f"{T} = {{ banish = yes }}"),
    "t_t_pneumonic": ("", f"{T} = {{ add_trait = pneumonic }}"),
    "t_t_rob_artifacts": ("", f"{T} = {{ every_character_artifact = {{ set_owner = {{ target = root }} }} }}"),
    "t_t_artifact_claims": ("", f"{T} = {{ every_character_artifact = {{ save_temporary_scope_as = {P}_a root.house = {{ add_house_artifact_claim = scope:{P}_a }} }} }}"),
    "t_t_knight_force": ("", f"{T} = {{ if = {{ limit = {{ is_potential_knight = yes }} set_knight_status = force }} }}"),
    "t_t_knight_off": ("", f"{T} = {{ set_knight_status = disallow }}"),
    "t_t_schemes_expose": ("", f"{T} = {{ every_scheme = {{ limit = {{ is_scheme_exposed = no }} expose_scheme = yes }} }}"),
    "t_t_schemes_end": ("", f"{T} = {{ every_scheme = {{ end_scheme = yes }} }}"),
    "t_t_child_me": (
        f"NOT = {{ {T} = {{ this = root }} }}",
        f"if = {{ limit = {{ {T} = {{ is_female = yes is_pregnant = no }} is_female = no }} {T} = {{ make_pregnant = {{ father = root }} }} }} "
        f"else_if = {{ limit = {{ is_female = yes is_pregnant = no {T} = {{ is_female = no }} }} make_pregnant = {{ father = {T} }} }}",
    ),
    "t_t_child_now": (
        OPPOSITE_SEX,
        f"if = {{ limit = {{ is_female = yes }} create_character = {{ mother = root father = {T} {NEWBORN} }} }} "
        f"else = {{ create_character = {{ mother = {T} father = root {NEWBORN} }} }}",
    ),
    "t_t_guest": (f"{T} = {{ is_ruler = no NOT = {{ employer ?= root }} }}", f"{T} = {{ visit_court_of = root }}"),
    "t_t_hostage": (f"{T} = {{ is_hostage = no is_ruler = no }}", f"take_hostage = {T}"),
    "t_t_hostage_free": (f"{T} = {{ is_hostage = yes }}", f"{T} = {{ return_hostage = yes }}"),
    "t_t_family_hostages": ("", f"{T} = {{ every_child = {{ limit = {{ is_hostage = no is_ruler = no is_alive = yes }} save_temporary_scope_as = {P}_kid root = {{ take_hostage = scope:{P}_kid }} }} }}"),
    "t_t_armies_to": (f"{T} = {{ exists = capital_province }}", f"every_army = {{ limit = {{ is_army_in_combat = no }} set_army_location = {T}.capital_province }}"),
    "t_enemy_commander": ("", f"{T} = {{ every_army = {{ remove_commander = yes }} }}"),
    "t_enemy_supply": ("", f"{T} = {{ every_army = {{ clear_supply = yes }} }}"),
    "t_enemy_deplete": ("", f"if = {{ limit = {{ global_var:{P}_tier ?= 1 }} {P}_deplete_target = {{ SHARE = 0.25 }} }} else_if = {{ limit = {{ global_var:{P}_tier ?= 3 }} {P}_deplete_target = {{ SHARE = 0.9 }} }} else = {{ {P}_deplete_target = {{ SHARE = 0.5 }} }}"),
    **{f"t_t_epidemic_{e}": (f"{T} = {{ is_landed = yes exists = capital_province }}", f"{T}.capital_province = {{ create_epidemic_outbreak = {{ type = {e} intensity = major }} }}") for e in EPIDEMICS},
    **{f"t_t_councillor_{c}": (f"{T} = {{ OR = {{ employer ?= root is_vassal_of = root }} is_adult = yes }}", f"assign_councillor_type = {{ type = councillor_{c} target = {T} remove_existing_councillor = yes }}") for c in COUNCIL},
    **{f"t_t_cp_{c}": (EMPLOYED_ADULT, f"appoint_court_position = {{ recipient = {T} court_position = {c}_court_position }}") for c in COURT},
}

# Shared effects. $KEY$ is a toggle name.
EFFECTS_HEAD = """# AUTO-GENERATED by tools/gen_ucm_crozier.py; edit there, not this file.
# Root = player unless noted. Toggle state is global: on_<toggle>, plus the strength it was turned on at (lv_, fx_).

ucm_crozier_cheats_setup = {
	save_scope_as = ucm_crozier_cheats_p
	if = { limit = { NOT = { exists = global_var:ucm_crozier_cheats_power } } set_global_variable = { name = ucm_crozier_cheats_power value = 1 } set_global_variable = { name = ucm_crozier_cheats_mult value = 1 } }
}

ucm_crozier_cheats_toast = {
	if = { limit = { NOT = { has_global_variable = ucm_crozier_cheats_no_toast } } send_interface_toast = { title = ucm_crozier_cheats_toast_$KEY$ } }
}

ucm_crozier_cheats_tick_in = {
	set_global_variable = { name = ucm_crozier_cheats_tick_pending value = yes days = $LOCK$ }
	scope:ucm_crozier_cheats_p = { trigger_event = { id = ucm_crozier_cheats.9000 days = $DAYS$ } }
}

ucm_crozier_cheats_schedule = {
	if = {
		limit = { NOT = { has_global_variable = ucm_crozier_cheats_tick_pending } }
		if = { limit = { global_var:ucm_crozier_cheats_freq ?= 1 } ucm_crozier_cheats_tick_in = { DAYS = 7 LOCK = 9 } }
		else_if = { limit = { global_var:ucm_crozier_cheats_freq ?= 3 } ucm_crozier_cheats_tick_in = { DAYS = 90 LOCK = 92 } }
		else = { ucm_crozier_cheats_tick_in = { DAYS = 30 LOCK = 32 } }
	}
}

ucm_crozier_cheats_strip = {
	every_in_global_list = { variable = ucm_crozier_cheats_h_$KEY$ ucm_crozier_cheats_revoke_$KEY$ = yes }
	clear_global_variable_list = ucm_crozier_cheats_h_$KEY$
}

ucm_crozier_cheats_on = {
	ucm_crozier_cheats_strip = { KEY = $KEY$ }
	set_global_variable = { name = ucm_crozier_cheats_lv_$KEY$ value = global_var:ucm_crozier_cheats_power }
	set_global_variable = { name = ucm_crozier_cheats_fx_$KEY$ value = global_var:ucm_crozier_cheats_mult }
	set_global_variable = { name = ucm_crozier_cheats_on_$KEY$ value = yes }
	scope:ucm_crozier_cheats_p = { ucm_crozier_cheats_grant_$KEY$ = yes }
	ucm_crozier_cheats_schedule = yes
}

ucm_crozier_cheats_off = {
	remove_global_variable = ucm_crozier_cheats_on_$KEY$
	ucm_crozier_cheats_strip = { KEY = $KEY$ }
}

ucm_crozier_cheats_toggle = {
	if = { limit = { has_global_variable = ucm_crozier_cheats_on_$KEY$ } ucm_crozier_cheats_off = { KEY = $KEY$ } ucm_crozier_cheats_toast = { KEY = off_$KEY$ } }
	else = { ucm_crozier_cheats_on = { KEY = $KEY$ } ucm_crozier_cheats_toast = { KEY = on_$KEY$ } }
}

ucm_crozier_cheats_ensure_on = {
	if = { limit = { NOT = { has_global_variable = ucm_crozier_cheats_on_$KEY$ } } ucm_crozier_cheats_on = { KEY = $KEY$ } }
}

ucm_crozier_cheats_ensure_off = {
	if = { limit = { has_global_variable = ucm_crozier_cheats_on_$KEY$ } ucm_crozier_cheats_off = { KEY = $KEY$ } }
}

# Moves a toggle from past holders to whoever is played now.
ucm_crozier_cheats_keep = {
	if = {
		limit = { has_global_variable = ucm_crozier_cheats_on_$KEY$ }
		every_in_global_list = {
			variable = ucm_crozier_cheats_h_$KEY$
			limit = { NOT = { this = scope:ucm_crozier_cheats_p } }
			ucm_crozier_cheats_revoke_$KEY$ = yes
			remove_list_global_variable = { name = ucm_crozier_cheats_h_$KEY$ target = this }
		}
		scope:ucm_crozier_cheats_p = { ucm_crozier_cheats_grant_$KEY$ = yes }
	}
}

# Scope: the character getting the modifier.
ucm_crozier_cheats_lv_add = {
	if = {
		limit = { NOT = { LV_ANY } }
LV_CHAIN
		add_to_global_variable_list = { name = ucm_crozier_cheats_h_$KEY$ target = this }
	}
}

# Scope: the character losing the modifier.
ucm_crozier_cheats_lv_remove = {
LV_REMOVE
}

ucm_crozier_cheats_immortal_restore = {
	remove_trait = withering_mind
	remove_trait = clouded_eyes
	remove_trait = faltering_heart
	remove_trait = fragile_bones
	remove_trait = infirm
	if = { limit = { age > 25 } set_immortal_age = 25 }
}

ucm_crozier_cheats_deplete_target = {
	scope:ucm_crozier_cheats_char = { every_army = { deplete_army_by_percentage = $SHARE$ } }
}

ucm_crozier_cheats_maa_resize = {
	every_maa_regiment = { change_maa_regiment_size = { size = $SIZE$ reinforce = yes } }
}

# Scope: the character.
ucm_crozier_cheats_add_genius = {
	add_trait = logistician
	add_trait = military_engineer
	add_trait = organizer
	add_trait = aggressive_attacker
}

ucm_crozier_cheats_combo_army = {
	if = { limit = { global_var:ucm_crozier_cheats_tier ?= 1 } ucm_crozier_cheats_maa_resize = { SIZE = 1 } }
	else_if = { limit = { global_var:ucm_crozier_cheats_tier ?= 3 } ucm_crozier_cheats_maa_resize = { SIZE = 5 } }
	else = { ucm_crozier_cheats_maa_resize = { SIZE = 2 } }
	every_maa_regiment = { change_maa_troops_count = 1000000 }
	every_directly_owned_province = { refill_levy = yes refill_garrison = yes }
	while = {
		count = 5
		create_character = {
			age = 24
			gender = male
			employer = root
			culture = root.culture
			faith = root.faith
			diplomacy = 8
			martial = 18
			stewardship = 8
			intrigue = 8
			learning = 8
			prowess = 40
			trait = physique_good_3
			trait = strong
			trait = education_martial_4
		}
	}
	ucm_crozier_cheats_add_genius = yes
	every_army = { limit = { exists = army_commander } army_commander = { ucm_crozier_cheats_add_genius = yes } }
	every_knight = { ucm_crozier_cheats_add_genius = yes }
}
"""


def effects():
    levels = range(1, len(STRENGTHS) + 1)
    any_level = "OR = { " + " ".join(f"has_character_modifier = {P}_$KEY$_l{i}" for i in levels) + " }"
    chain = []
    for i in reversed(levels):
        add = f"add_character_modifier = {{ modifier = {P}_$KEY$_l{i} }}"
        if i == levels[-1]:
            chain.append(f"\t\tif = {{ limit = {{ global_var:{P}_lv_$KEY$ ?= {i} }} {add} }}")
        elif i > 1:
            chain.append(f"\t\telse_if = {{ limit = {{ global_var:{P}_lv_$KEY$ ?= {i} }} {add} }}")
        else:
            chain.append(f"\t\telse = {{ {add} }}")
    removes = "\n".join(f"\tremove_character_modifier = {P}_$KEY$_l{i}" for i in levels)
    out = [EFFECTS_HEAD.replace("LV_ANY", any_level).replace("LV_CHAIN", "\n".join(chain)).replace("LV_REMOVE", removes)]
    for k in LEVELLED:
        out.append(f"{P}_grant_{k} = {{ {GRANT_OVERRIDE.get(k, f'{P}_lv_add = {{ KEY = {k} }}')} }}")
        out.append(f"{P}_revoke_{k} = {{ {P}_lv_remove = {{ KEY = {k} }} }}")
    for k, (grant, revoke) in HELD.items():
        out.append(f"{P}_grant_{k} = {{ {grant} }}")
        out.append(f"{P}_revoke_{k} = {{ {revoke} }}")
    out.append("")
    for name, each in (("maintenance", "keep"), ("all_on", "ensure_on"), ("all_off", "ensure_off")):
        out += [f"{P}_{name} = {{", *(f"\t{P}_{each} = {{ KEY = {k} }}" for k in TOGGLES), "}", ""]
    return "\n".join(out)


def sgui(name, body):
    return f"{P}_sg_{name} = {{\n\tscope = character\n\tis_shown = {{ ucm_single_player_trigger = yes{body[0]} }}\n" + "".join(f"\t{l}\n" for l in body[1:]) + "}\n"


def sguis():
    out = ["# AUTO-GENERATED by tools/gen_ucm_crozier.py; edit there, not this file. Root = player.\n"]
    for k in TOGGLES:
        out.append(sgui(f"st_{k}", [f" has_global_variable = {P}_on_{k}"]))
        out.append(sgui(f"tog_{k}", ["", f"effect = {{ {P}_setup = yes {P}_toggle = {{ KEY = {k} }} }}"]))
    for n, set_all in (("pon_char_self", "all_on"), ("poff_char_self", "all_off")):
        out.append(sgui(n, ["", f"effect = {{ {P}_setup = yes {P}_{set_all} = yes }}"]))
    for i, mult in enumerate(STRENGTHS, 1):
        default = f" NOT = {{ exists = global_var:{P}_power }}" if i == 1 else ""
        out.append(sgui(f"pow_{i}", [f" OR = {{ global_var:{P}_power ?= {i}{default} }}",
                                     f"effect = {{ set_global_variable = {{ name = {P}_power value = {i} }} set_global_variable = {{ name = {P}_mult value = {mult} }} }}"]))
    for i in (1, 2, 3):
        default = f" NOT = {{ exists = global_var:{P}_tier }}" if i == 2 else ""
        out.append(sgui(f"tier_{i}", [f" OR = {{ global_var:{P}_tier ?= {i}{default} }}", f"effect = {{ set_global_variable = {{ name = {P}_tier value = {i} }} }}"]))
    out.append(sgui("do_toasts_toggle", ["", f"effect = {{ if = {{ limit = {{ has_global_variable = {P}_no_toast }} remove_global_variable = {P}_no_toast }} else = {{ set_global_variable = {{ name = {P}_no_toast value = yes }} }} }}"]))
    for name, (valid, effect) in ACTIONS.items():
        body = [""]
        if name.startswith("t_"):
            body.append(f"saved_scopes = {{ {P}_char }}")
        if valid:
            body.append(f"is_valid = {{ {valid} }}")
        body.append(f"effect = {{ {P}_toast = {{ KEY = {name.split('_', 1)[1]} }} {effect} }}")
        out.append(sgui(name, body))
    return "\n".join(out)


def modifier(name, stats):
    return f"{name} = {{ icon = positive " + " ".join(f"{s} = {v:g}" for s, v in stats.items()) + " }"


def modifiers():
    out = ["# AUTO-GENERATED by tools/gen_ucm_crozier.py; edit there, not this file."]
    for k, base in LEVELLED.items():
        out += [modifier(f"{P}_{k}_l{i}", {s: v * m for s, v in base.items()}) for i, m in enumerate(STRENGTHS, 1)]
    out.append(modifier(f"{P}_stress", {"stress_gain_mult": -0.99}))
    out.append(modifier(f"{P}_art_crown", {"diplomacy": 10, "monthly_prestige": 5, "vassal_opinion": 25, "general_opinion": 10}))
    return "\n".join(out) + "\n"


def main():
    for rel, text in (("common/scripted_effects/ucm_crozier_cheats_effects.txt", effects()),
                      ("common/scripted_guis/ucm_crozier_cheats_scripted_guis.txt", sguis()),
                      ("common/modifiers/ucm_crozier_cheats_modifiers.txt", modifiers())):
        with open(os.path.join(MOD_DIR, rel), "w", encoding="utf-8-sig", newline="\n") as fh:
            fh.write(text)
        print(f"{rel}: {len(text.splitlines())} lines")


if __name__ == "__main__":
    main()
