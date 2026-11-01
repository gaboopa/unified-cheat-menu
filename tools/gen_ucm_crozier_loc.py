"""Regenerate localization/<lang>/ucm_crozier_cheats_l_<lang>.yml from the tables in gen_ucm_crozier.py and the
phrases here. On/off labels, toasts and modifier names are composed, so only each phrase needs translating.
Council, court position and disease names come from the game's own localization.

Run after editing a table:
    python tools/gen_ucm_crozier_loc.py
"""
import os

import gen_ucm_crozier

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ("english", "german", "russian", "simp_chinese", "turkish")
B = "UCM_CROZIER_CHEATS_B_"
P = "ucm_crozier_cheats"


def by_language(*texts):
    return dict(zip(LANGS, texts, strict=True))


# Sentence patterns. {x} is filled in by compose().
ON = by_language("On: {x}", "An: {x}", "Вкл.: {x}", "开：{x}", "Açık: {x}")
OFF = by_language("Off: {x}", "Aus: {x}", "Выкл.: {x}", "关：{x}", "Kapalı: {x}")
T_ON = by_language("Enabled: {x}", "Aktiviert: {x}", "Включено: {x}", "已开启：{x}", "Etkin: {x}")
T_OFF = by_language("Disabled: {x}", "Deaktiviert: {x}", "Выключено: {x}", "已关闭：{x}", "Devre dışı: {x}")
T_USED = by_language("Done: {x}", "Erledigt: {x}", "Готово: {x}", "已完成：{x}", "Tamam: {x}")
SCALED = by_language("{x} × strength", "{x} × Stärke", "{x} × сила", "{x} × 强度", "{x} × güç")
PER_MONTH = by_language("/month", "/Monat", "/мес.", "/月", "/ay")
BONUS = by_language("Menu bonus: {x} ×{m}", "Menübonus: {x} ×{m}", "Бонус меню: {x} ×{m}", "菜单加成：{x} ×{m}", "Menü bonusu: {x} ×{m}")
SCALED_TT = by_language("{x} at ×1, scaled by the strength selected when you switch this on. To change it, switch off, pick another strength and switch on again.",
              "{x} bei ×1, skaliert mit der beim Einschalten gewählten Stärke. Zum Ändern ausschalten, andere Stärke wählen und wieder einschalten.",
              "{x} при ×1, умножается на силу, выбранную при включении. Чтобы изменить: выключите, выберите другую силу и включите снова.",
              "×1 时为 {x}，并按开启时所选强度放大。如需更改，请先关闭，选择其他强度后重新开启。",
              "×1 için {x}; açarken seçilen güçle çarpılır. Değiştirmek için kapatın, başka güç seçin ve yeniden açın.")
FOLLOWS = by_language("Follows you to a new character at the next check.", "Geht bei der nächsten Prüfung auf deinen neuen Charakter über.",
            "При следующей проверке переходит на вашего нового персонажа.", "切换角色后，下次检查时转移到新角色。", "Sonraki kontrolde yeni karakterinize geçer.")
CHECKED = by_language("Checked on switching on and at each auto-mode check.", "Wird beim Einschalten und bei jeder Auto-Prüfung geprüft.",
            "Проверяется при включении и при каждой автопроверке.", "开启时及每次自动检查时生效。", "Açılırken ve her otomatik kontrolde denetlenir.")
APPOINT = by_language("Appoint as my $KEY$", "Zu meinem Amt ernennen: $KEY$", "Назначить на пост: $KEY$", "任命为我的$KEY$", "Görevime ata: $KEY$")
APPOINT_TT = by_language("They take this post in your realm if they qualify; a council seat's previous holder stays at court.",
               "Übernimmt dieses Amt, falls berechtigt; der bisherige Ratsherr bleibt am Hof.",
               "Занимает этот пост, если подходит; прежний советник остаётся при дворе.",
               "符合条件者就任此职；原议会成员留在宫廷。", "Uygunsa bu görevi alır; önceki meclis üyesi sarayda kalır.")
OUTBREAK = by_language("Start $KEY$ at their capital", "$KEY$ in ihrer Hauptstadt auslösen", "Вызвать $KEY$ в их столице", "在其首都引发$KEY$", "Başkentlerinde $KEY$ başlat")
OUTBREAK_TT = by_language("Major outbreak in the target's capital province. It spreads like any epidemic, and can reach you.",
                "Großer Ausbruch in der Hauptstadtprovinz des Ziels. Breitet sich normal aus und kann auch dich treffen.",
                "Крупная вспышка в столичной провинции цели. Распространяется как обычно и может дойти до вас.",
                "在目标首都省份大规模爆发，会像普通疫病一样传播，也可能波及你。",
                "Hedefin başkent eyaletinde büyük salgın. Normal yayılır ve size de ulaşabilir.")

AMOUNTS = {"health": "+50", "skills": "+50", "income": "+400%", "domain": "+50", "vassals": "+100", "prestige": "+100{mo}", "piety": "+100{mo}",
           "monthly_gold": "+10{mo}", "renown": "+5{mo}", "slots": "+1", "influence": "+5{mo}", "lifestyle_xp": "+100%", "levy": "+100%",
           "life": "+10", "prestige_mult": "+100%", "renown_mult": "+100%", "innovation": "+100%", "legit_gain": "+1{mo}, +100%", "travel_safe": "+100%",
           "merit_gain": "+100%", "skills_mult": "+50%", "long_reign": "+100%", "legend_spread": "+100%"}

# Levelled toggles: what each one raises.
SHORT = {
    "health": by_language("Health", "Gesundheit", "Здоровье", "健康", "Sağlık"),
    "skills": by_language("All six skills", "Alle sechs Fertigkeiten", "Все шесть навыков", "全部六项能力", "Altı becerinin tümü"),
    "income": by_language("Monthly income", "Monatseinkommen", "Месячный доход", "月收入", "Aylık gelir"),
    "domain": by_language("Domain limit", "Domänenlimit", "Лимит домена", "领地上限", "Alan sınırı"),
    "vassals": by_language("Vassal limit", "Vasallenlimit", "Лимит вассалов", "封臣上限", "Vasal sınırı"),
    "prestige": by_language("Prestige", "Prestige", "Престиж", "声望", "Prestij"),
    "piety": by_language("Piety", "Frömmigkeit", "Благочестие", "虔诚", "Dindarlık"),
    "monthly_gold": by_language("Gold", "Gold", "Золото", "金币", "Altın"),
    "renown": by_language("Dynasty renown", "Dynastieruhm", "Известность династии", "王朝名望", "Hanedan şöhreti"),
    "slots": by_language("Building slots per holding", "Gebäudeplätze je Besitz", "Места построек во владении", "每处领地的建筑槽", "Mülk başına yapı yuvası"),
    "influence": by_language("Influence (administrative only)", "Einfluss (nur Verwaltung)", "Влияние (только администрация)", "影响力（仅官僚制）", "Nüfuz (yalnız idari)"),
    "lifestyle_xp": by_language("Lifestyle experience", "Lebensstil-Erfahrung", "Опыт образа жизни", "生活方式经验", "Yaşam tarzı deneyimi"),
    "levy": by_language("Levy size", "Aufgebotsgröße", "Размер ополчения", "征召兵规模", "Asker toplama boyutu"),
    "life": by_language("Years of life (you, spouses, children)", "Lebensjahre (du, Ehepartner, Kinder)", "Годы жизни (вы, супруги, дети)", "寿命（你、配偶、子女）", "Yaşam yılı (siz, eşler, çocuklar)"),
    "prestige_mult": by_language("Prestige and piety gain", "Prestige- und Frömmigkeitsgewinn", "Прирост престижа и благочестия", "声望与虔诚获取", "Prestij ve dindarlık kazancı"),
    "renown_mult": by_language("Renown gain", "Ruhmgewinn", "Прирост известности", "名望获取", "Şöhret kazancı"),
    "innovation": by_language("Innovation speed (culture head only)", "Innovationstempo (nur Kulturoberhaupt)", "Скорость инноваций (только глава культуры)", "创新速度（仅文化领袖）", "Yenilik hızı (yalnız kültür başı)"),
    "legit_gain": by_language("Legitimacy per month, then gain", "Legitimität pro Monat, dann Gewinn", "Легитимность в месяц и прирост", "每月正统性与获取", "Aylık meşruiyet ve kazanç"),
    "travel_safe": by_language("Travel speed and safety", "Reisetempo und -sicherheit", "Скорость и безопасность поездок", "旅行速度与安全", "Yolculuk hızı ve güvenliği"),
    "merit_gain": by_language("Merit gain (administrative only)", "Verdienstgewinn (nur Verwaltung)", "Прирост заслуг (только администрация)", "功绩获取（仅官僚制）", "Liyakat kazancı (yalnız idari)"),
    "skills_mult": by_language("All six skills, by percent", "Alle sechs Fertigkeiten, prozentual", "Все шесть навыков, в процентах", "全部六项能力（百分比）", "Altı beceri, yüzdeyle"),
    "long_reign": by_language("Long reign bonus speed", "Tempo des Langzeitherrscher-Bonus", "Скорость бонуса долгого правления", "长期统治加成速度", "Uzun hükümdarlık bonus hızı"),
    "legend_spread": by_language("Spread of legends you own", "Ausbreitung deiner Legenden", "Распространение ваших легенд", "你的传说传播", "Efsanelerinizin yayılması"),
}

# Other toggles: (label, tooltip). Tooltip gets FOLLOWS or CHECKED appended.
HELD = {
    "stress": (by_language("Stress gain −99%", "Stressgewinn −99 %", "Прирост стресса −99%", "压力获取 −99%", "Stres kazancı −%99"),
               by_language("You build up only 1% of normal stress. Strength doesn't apply.", "Du baust nur 1 % des normalen Stresses auf. Stärke gilt hier nicht.",
                 "Вы набираете лишь 1% обычного стресса. Сила не влияет.", "压力只累积正常的 1%。强度对此无效。", "Normal stresin yalnız %1'ini alırsınız. Güç etkilemez.")),
    "immortal_player": (by_language("Immortal (old age can't kill you)", "Unsterblich (kein Tod durch Alter)", "Бессмертие (старость не убьёт)", "不朽（不会老死）", "Ölümsüz (yaşlılık öldürmez)"),
                        by_language("Adds the game's Immortal trait and clears age ailments. Murder, battle and events can still kill you. Your look freezes at 25 if you are older. Off removes the trait only if this added it.",
                          "Gibt das Merkmal Unsterblich und heilt Altersleiden. Mord, Schlacht und Ereignisse können dich weiter töten. Über 25 bleibt dein Aussehen bei 25. Aus entfernt nur ein hiermit gegebenes Merkmal.",
                          "Даёт черту «Бессмертный» и убирает возрастные недуги. Убийство, битва и события всё ещё смертельны. Внешность старше 25 лет замирает на 25. Выключение убирает черту, только если она дана здесь.",
                          "获得游戏的不朽特质并治愈衰老病症。谋杀、战斗和事件仍可致死。超过 25 岁时外貌定格于 25 岁。关闭时仅移除由此获得的特质。",
                          "Ölümsüz özelliğini verir ve yaşlılık hastalıklarını giderir. Suikast, savaş ve olaylar yine öldürebilir. 25 üstündeyseniz görünüşünüz 25'te kalır. Kapatınca yalnız buradan gelen özellik kalkar.")),
    "disease_player": (by_language("Disease immunity", "Krankheitsimmunität", "Иммунитет к болезням", "疾病免疫", "Hastalık bağışıklığı"),
                       by_language("Adds the Disease Shield trait and cures every disease at each check. Events can still infect you directly.",
                         "Gibt Krankheitsschild und heilt bei jeder Prüfung alle Krankheiten. Ereignisse können dich weiter direkt anstecken.",
                         "Даёт защиту от болезней и лечит всё при каждой проверке. События всё ещё могут заразить напрямую.",
                         "获得疾病护盾，每次检查时治愈所有疾病。事件仍可直接使你染病。",
                         "Hastalık Kalkanı verir ve her kontrolde tüm hastalıkları iyileştirir. Olaylar yine doğrudan bulaştırabilir.")),
    "auto_gold_floor": (by_language("Gold floor of 1,000", "Goldminimum 1.000", "Минимум золота 1000", "金币下限 1000", "En az 1.000 altın"),
                        by_language("Below 1,000 gold, debt included, you are raised to exactly 1,000.", "Unter 1.000 Gold, inklusive Schulden, wirst du auf genau 1.000 angehoben.",
                          "При менее чем 1000 золота, включая долг, становится ровно 1000.", "金币（含负债）低于 1000 时补至 1000。", "Borç dahil 1.000 altının altındaysanız tam 1.000 olur.")),
    "auto_prestige_floor": (by_language("Prestige and piety floor of 1,000", "Prestige- und Frömmigkeitsminimum 1.000", "Минимум престижа и благочестия 1000", "声望与虔诚下限 1000", "En az 1.000 prestij ve dindarlık"),
                            by_language("Either value under 1,000 is raised to exactly 1,000.", "Jeder Wert unter 1.000 wird auf genau 1.000 angehoben.",
                              "Значение ниже 1000 становится ровно 1000.", "任一数值低于 1000 时补至 1000。", "1.000'in altındaki değer tam 1.000 olur.")),
    "auto_no_prison": (by_language("Instant release from prison", "Sofortige Haftentlassung", "Мгновенное освобождение из тюрьмы", "立即出狱", "Hapisten anında çıkış"),
                       by_language("You are freed as soon as you are imprisoned.", "Du kommst frei, sobald du eingekerkert wirst.",
                         "Вас освобождают сразу после заключения.", "一旦入狱立刻获释。", "Hapse girer girmez serbest kalırsınız.")),
    "auto_ascension": (by_language("Best genes and +5 skills for each ruler I play", "Beste Gene und +5 Fertigkeiten für jeden gespielten Herrscher", "Лучшие гены и +5 навыков каждому моему правителю", "我操控的每位统治者：最佳基因与 +5 能力", "Oynadığım her hükümdara en iyi genler ve +5 beceri"),
                       by_language("Genius, Herculean and Beautiful plus +5 to all six skills, once per character.", "Genie, Herkulisch und Schön sowie +5 auf alle sechs Fertigkeiten, einmal je Charakter.",
                         "Гений, Геракл и Красота, плюс +5 ко всем шести навыкам, один раз на персонажа.", "天才、赫拉克勒斯体魄与美貌，全部六项能力 +5，每个角色一次。", "Dahi, Herkül ve Güzel ile altı beceriye +5, karakter başına bir kez.")),
    "auto_forever_young": (by_language("Age never above 30", "Alter nie über 30", "Возраст не выше 30", "年龄不超过 30", "Yaş asla 30'u geçmez"),
                           by_language("Past 30, your age is reset to 30.", "Über 30 wird dein Alter auf 30 zurückgesetzt.", "После 30 лет возраст сбрасывается на 30.", "超过 30 岁时重置为 30 岁。", "30'u geçince yaşınız 30'a döner.")),
}

# One-shot buttons: rest of the name -> (label, tooltip).
FREQ = {
    "freq_week": ("Weekly", 7, by_language("Auto-mode checks: weekly", "Auto-Prüfungen: wöchentlich", "Автопроверки: раз в неделю", "自动检查：每周", "Otomatik kontrol: haftalık")),
    "freq_month": ("Monthly", 30, by_language("Auto-mode checks: monthly (default)", "Auto-Prüfungen: monatlich (Standard)", "Автопроверки: раз в месяц (по умолчанию)", "自动检查：每月（默认）", "Otomatik kontrol: aylık (varsayılan)")),
    "freq_quarter": ("Quarterly", 90, by_language("Auto-mode checks: quarterly", "Auto-Prüfungen: vierteljährlich", "Автопроверки: раз в квартал", "自动检查：每季度", "Otomatik kontrol: üç aylık")),
}
FREQ_TT = by_language("Toggles and auto modes refresh every {d} days, from the next check on.", "Schalter und Auto-Modi erneuern sich ab der nächsten Prüfung alle {d} Tage.",
            "Переключатели и автопрофили обновляются каждые {d} дн. со следующей проверки.", "自下次检查起，开关和自动模式每 {d} 天刷新一次。", "Sonraki kontrolden itibaren anahtarlar ve otomatik modlar {d} günde bir yenilenir.")
ACTIONS = {
    "combo_army": (by_language("Dream army", "Traumarmee", "Армия мечты", "梦幻大军", "Rüya ordusu"),
                   by_language("Men-at-arms grow by the Amounts setting (+1/+2/+5) and fill up, levies and garrisons refill, 5 strong knights join, and you, your knights and commanders gain four commander traits.",
                     "Soldaten wachsen laut Mengen-Einstellung (+1/+2/+5) und füllen sich, Aufgebote und Garnisonen ebenfalls, 5 starke Ritter kommen, und du, deine Ritter und Kommandeure erhalten vier Kommandeursmerkmale.",
                     "Латники растут по настройке «Количество» (+1/+2/+5) и пополняются, ополчение и гарнизоны тоже, приходят 5 сильных рыцарей; вы, рыцари и командиры получают четыре командирские черты.",
                     "常备军按数量设置增长（+1/+2/+5）并补满，征召兵与驻军补满，5 名强力骑士加入，你、骑士和统帅获得四项统帅特质。",
                     "Paralı askerler Miktar ayarına göre büyür (+1/+2/+5) ve dolar, askerler ve garnizonlar dolar, 5 güçlü şövalye katılır; siz, şövalyeler ve komutanlar dört komutan özelliği alırsınız.")),
    "forge_crown": (by_language("Forge the Sovereign's Crown", "Krone des Souveräns schmieden", "Выковать корону суверена", "锻造君主之冠", "Hükümdar Tacı'nı döv"),
                    by_language("A legendary, unbreakable crown: +10 Diplomacy, +5 monthly prestige, +25 vassal and +10 general opinion.", "Eine legendäre, unzerstörbare Krone: +10 Diplomatie, +5 Prestige pro Monat, +25 Vasallen- und +10 allgemeine Meinung.",
                      "Легендарная нерушимая корона: +10 дипломатии, +5 престижа в месяц, +25 мнения вассалов и +10 общего мнения.", "传奇且不会损坏的王冠：+10 外交，每月 +5 声望，+25 封臣好感，+10 普遍好感。", "Efsanevi, kırılmaz taç: +10 Diplomasi, aylık +5 prestij, +25 vasal ve +10 genel görüş.")),
    "travel_arrive": (by_language("Finish my journey now", "Reise sofort beenden", "Завершить поездку сейчас", "立即结束旅程", "Yolculuğumu hemen bitir"),
                      by_language("Your current journey ends at its destination.", "Deine Reise endet sofort am Ziel.", "Текущая поездка сразу завершается в пункте назначения.", "当前旅程立即在目的地结束。", "Mevcut yolculuğunuz hedefte sona erer.")),
    "toasts_toggle": (by_language("Cheat pop-ups: on/off", "Cheat-Meldungen: an/aus", "Всплывающие сообщения: вкл./выкл.", "作弊弹窗：开/关", "Hile bildirimleri: aç/kapa"),
                      by_language("Shows or hides the small messages after using a cheat.", "Zeigt oder verbirgt die kleinen Meldungen nach Cheats.", "Показывает или скрывает сообщения после чита.", "显示或隐藏使用作弊后的小提示。", "Hile sonrası küçük iletileri gösterir veya gizler.")),
    "enemy_commander": (by_language("Strip their army commanders", "Ihre Armeekommandeure entfernen", "Снять их командиров", "撤掉其军队统帅", "Ordu komutanlarını kaldır"),
                        by_language("Every army of the target loses its commander. The AI may appoint new ones.", "Jede Armee des Ziels verliert ihren Kommandeur. Die KI kann neue ernennen.", "Все армии цели теряют командиров. ИИ может назначить новых.", "目标所有军队失去统帅，AI 可能重新任命。", "Hedefin tüm orduları komutansız kalır. YZ yenilerini atayabilir.")),
    "enemy_deplete": (by_language("Destroy some of their raised troops", "Einen Teil ihrer Truppen vernichten", "Уничтожить часть их войск", "摧毁其部分已征召部队", "Toplanmış birliklerinin bir kısmını yok et"),
                      by_language("Their raised armies permanently lose soldiers: 25%, 50% or 90% for Low, Medium or High Amounts.", "Ihre Armeen verlieren dauerhaft Soldaten: 25 %, 50 % oder 90 % bei niedriger, mittlerer oder hoher Menge.",
                        "Их армии навсегда теряют солдат: 25%, 50% или 90% при низком, среднем или высоком количестве.", "其军队永久损失士兵：数量设置低/中/高时为 25%/50%/90%。", "Orduları kalıcı asker kaybeder: düşük/orta/yüksek miktarda %25, %50 veya %90.")),
    "enemy_supply": (by_language("Drain their army supplies", "Ihre Armeevorräte leeren", "Опустошить припасы их армий", "耗尽其军队补给", "Ordu erzaklarını boşalt"),
                     by_language("Every raised army of the target is left with no supply.", "Jede Armee des Ziels steht ohne Vorräte da.", "Все армии цели остаются без припасов.", "目标所有军队补给归零。", "Hedefin tüm orduları erzaksız kalır.")),
    "t_armies_to": (by_language("Send my armies to their capital", "Meine Armeen zu ihrer Hauptstadt schicken", "Перебросить мои армии к их столице", "将我的军队传送至其首都", "Ordularımı başkentlerine gönder"),
                    by_language("Your armies outside battle jump to the target's capital; any enemies there fight at once.", "Deine Armeen außerhalb von Schlachten springen zur Hauptstadt des Ziels; Feinde dort kämpfen sofort.",
                      "Ваши армии вне боя переносятся в столицу цели; враги там сразу вступают в бой.", "未交战的军队立即抵达目标首都；若有敌军则立刻开战。", "Savaşta olmayan ordularınız hedefin başkentine geçer; oradaki düşmanla hemen savaşır.")),
    "t_artifact_claims": (by_language("Claim their artifacts for my house", "Ihre Artefakte für mein Haus beanspruchen", "Притязания моего дома на их артефакты", "为我的家族宣称其宝物", "Eserleri için hanem adına hak iddia et"),
                          by_language("Your house gains a claim on each artifact they own.", "Dein Haus erhält Anspruch auf jedes ihrer Artefakte.", "Ваш дом получает притязание на каждый их артефакт.", "你的家族获得其每件宝物的宣称。", "Haneniz sahip olduğu her esere hak kazanır.")),
    "t_banish": (by_language("Banish them", "Verbannen", "Изгнать", "放逐此人", "Sürgün et"),
                 by_language("Removes the target from their current court.", "Entfernt das Ziel von seinem Hof.", "Удаляет цель с её двора.", "将目标逐出其所在宫廷。", "Hedefi bulunduğu saraydan çıkarır.")),
    "t_child_me": (by_language("Conceive my child", "Mein Kind zeugen", "Зачать моего ребёнка", "孕育我的孩子", "Çocuğumu gebe bırak"),
                   by_language("The woman of the pair becomes pregnant by you or the target. Needs opposite sexes and no current pregnancy.", "Die Frau des Paares wird schwanger. Erfordert verschiedene Geschlechter und keine laufende Schwangerschaft.",
                     "Женщина из пары беременеет. Нужны разные полы и отсутствие беременности.", "二人中的女性怀孕。需异性且未怀孕。", "Çiftteki kadın hamile kalır. Karşı cins ve mevcut hamilelik olmaması gerekir.")),
    "t_child_now": (by_language("Have a child together now", "Sofort ein Kind bekommen", "Сразу родить общего ребёнка", "立刻共同诞下孩子", "Hemen birlikte çocuk sahibi ol"),
                    by_language("A newborn with Genius, Herculean and Beautiful appears at your court. Needs opposite sexes.", "Ein Neugeborenes mit Genie, Herkulisch und Schön erscheint an deinem Hof. Erfordert verschiedene Geschlechter.",
                      "При вашем дворе появляется младенец с чертами Гений, Геракл и Красота. Нужны разные полы.", "一名拥有天才、赫拉克勒斯体魄与美貌的婴儿出现在你的宫廷。需异性。", "Sarayınızda Dahi, Herkül ve Güzel özellikli bir bebek belirir. Karşı cins gerekir.")),
    "t_depose": (by_language("Depose them", "Absetzen", "Свергнуть", "废黜此人", "Tahttan indir"),
                 by_language("All their titles pass to their heir.", "Alle Titel gehen an den Erben.", "Все их титулы переходят к наследнику.", "其所有头衔传给继承人。", "Tüm unvanları varisine geçer.")),
    "t_execute": (by_language("Execute them", "Hinrichten", "Казнить", "处决此人", "İdam et"),
                  by_language("They die now, with you as their executioner.", "Das Ziel stirbt sofort, mit dir als Henker.", "Цель сразу умирает, вы указаны как палач.", "目标立即死亡，你被记为行刑者。", "Hemen ölür; cellat olarak siz kaydedilirsiniz.")),
    "t_family_hostages": (by_language("Hold all their children hostage", "Alle ihre Kinder als Geiseln nehmen", "Взять в заложники всех их детей", "扣押其所有子女为人质", "Tüm çocuklarını rehin al"),
                          by_language("Living children who aren't rulers or hostages already come to your court.", "Lebende Kinder, die weder Herrscher noch Geiseln sind, kommen an deinen Hof.",
                            "Живые дети, не правители и не заложники, прибывают к вашему двору.", "在世且非统治者、非人质的子女来到你的宫廷。", "Hükümdar veya rehin olmayan yaşayan çocuklar sarayınıza gelir.")),
    "t_guest": (by_language("Invite to my court as a guest", "Als Gast an meinen Hof einladen", "Пригласить ко двору как гостя", "邀请其来我的宫廷作客", "Sarayıma konuk olarak davet et"),
                by_language("They travel to your court, where you can recruit or marry them.", "Das Ziel reist an deinen Hof, wo du es anwerben oder verheiraten kannst.", "Цель едет к вашему двору, где её можно нанять или женить.", "目标前来你的宫廷，你可招募或为其安排婚事。", "Sarayınıza gelir; işe alabilir veya evlendirebilirsiniz.")),
    "t_hostage": (by_language("Hold them hostage", "Als Geisel nehmen", "Взять в заложники", "扣为人质", "Rehin al"),
                  by_language("Taken to your court as a hostage. Not for rulers or current hostages.", "Wird als Geisel an deinen Hof gebracht. Nicht für Herrscher oder bestehende Geiseln.", "Доставляется ко двору как заложник. Не для правителей и нынешних заложников.", "带回宫廷作为人质。不适用于统治者或现有人质。", "Rehin olarak sarayınıza gelir. Hükümdar veya mevcut rehinler için değildir.")),
    "t_hostage_free": (by_language("Release this hostage", "Geisel freilassen", "Отпустить заложника", "释放此人质", "Rehineyi serbest bırak"),
                       by_language("A hostage target goes back home.", "Eine Geisel kehrt heim.", "Заложник возвращается домой.", "人质目标返回家乡。", "Rehin hedef evine döner.")),
    "t_knight_force": (by_language("Knight: always", "Ritter: immer", "Рыцарь: всегда", "骑士：总是", "Şövalye: her zaman"),
                       by_language("They always serve their liege as a knight, if able at their current court.", "Dient dem Lehnsherrn stets als Ritter, falls am Hof möglich.", "Всегда служит сюзерену рыцарем, если это возможно при дворе.", "只要在当前宫廷可行，总是作为骑士效力。", "Sarayında mümkünse her zaman şövalye olur.")),
    "t_knight_off": (by_language("Knight: never", "Ritter: nie", "Рыцарь: никогда", "骑士：从不", "Şövalye: asla"),
                     by_language("They won't serve as a knight.", "Dient nicht als Ritter.", "Не будет служить рыцарем.", "不会作为骑士效力。", "Şövalye olarak hizmet etmez.")),
    "t_pneumonic": (by_language("Inflict pneumonia", "Lungenentzündung zufügen", "Наслать пневмонию", "使其患上肺炎", "Zatürre bulaştır"),
                    by_language("A severe, often deadly illness.", "Eine schwere, oft tödliche Krankheit.", "Тяжёлая, часто смертельная болезнь.", "一种严重且常致命的疾病。", "Ağır, sık sık ölümcül bir hastalık.")),
    "t_rob_artifacts": (by_language("Seize all their artifacts", "Alle ihre Artefakte beschlagnahmen", "Забрать все их артефакты", "夺走其所有宝物", "Tüm eserlerine el koy"),
                        by_language("Everything they own moves to your inventory.", "Alles wandert in dein Inventar.", "Всё переходит в ваш инвентарь.", "其所有宝物转入你的库存。", "Hepsi envanterinize geçer.")),
    "t_schemes_end": (by_language("Cancel all their schemes", "Alle ihre Intrigen beenden", "Отменить все их интриги", "终止其所有计谋", "Tüm entrikalarını bitir"),
                      by_language("Ends each scheme they run.", "Beendet jede ihrer Intrigen.", "Завершает каждую их интригу.", "结束其进行中的每项计谋。", "Yürüttüğü her entrikayı bitirir.")),
    "t_schemes_expose": (by_language("Reveal all their schemes", "Alle ihre Intrigen aufdecken", "Раскрыть все их интриги", "揭露其所有计谋", "Tüm entrikalarını açığa çıkar"),
                         by_language("Each hidden scheme they run is exposed.", "Jede verborgene Intrige wird aufgedeckt.", "Каждая скрытая интрига раскрывается.", "其每项隐秘计谋都被揭露。", "Gizli her entrikası ortaya çıkar.")),
}
EPIDEMIC_KEYS = {"bubonic_plague": "trait_bubonic_plague", "smallpox": "trait_smallpox", "typhus": "trait_typhus", "consumption": "trait_consumption",
                 "measles": "trait_measles", "dysentery": "trait_dysentery", "ergotism": "trait_ergotism"}
COUNCIL_KEYS = {c: f"councillor_{c}" for c in gen_ucm_crozier.COUNCIL}
COURT_KEYS = {c: f"{c}_court_position" for c in gen_ucm_crozier.COURT}

PANEL = {
    "UCM_CROZIER_CHEATS_PANEL_ALLOFF": by_language("All toggles off", "Alle Schalter aus", "Все переключатели выкл.", "关闭全部开关", "Tüm anahtarları kapat"),
    "UCM_CROZIER_CHEATS_PANEL_ALLOFF_TT": by_language("Switches off every bonus and auto mode here and removes what they gave.", "Schaltet hier jeden Bonus und Auto-Modus aus und entfernt ihre Wirkung.", "Выключает все бонусы и автопрофили здесь и убирает их эффект.", "关闭此处所有加成和自动模式，并移除其效果。", "Buradaki tüm bonus ve otomatik modları kapatır, verdiklerini kaldırır."),
    "UCM_CROZIER_CHEATS_PANEL_ALLON": by_language("All toggles on", "Alle Schalter an", "Все переключатели вкл.", "开启全部开关", "Tüm anahtarları aç"),
    "UCM_CROZIER_CHEATS_PANEL_ALLON_TT": by_language("Switches on every bonus and auto mode here at the selected strength.", "Schaltet hier jeden Bonus und Auto-Modus mit der gewählten Stärke an.", "Включает все бонусы и автопрофили здесь с выбранной силой.", "以所选强度开启此处所有加成和自动模式。", "Buradaki tüm bonus ve otomatik modları seçili güçle açar."),
    "UCM_CROZIER_CHEATS_POW_LABEL": by_language("Strength:", "Stärke:", "Сила:", "强度：", "Güç:"),
    "UCM_CROZIER_CHEATS_POW_TT": by_language("Multiplier locked in when a toggle is switched on; an active toggle shows its own ×N. To change it, switch off, pick another and switch on.", "Multiplikator, der beim Einschalten festgelegt wird; aktive Schalter zeigen ihr ×N. Zum Ändern aus-, umstellen und einschalten.", "Множитель, фиксируется при включении; активный переключатель показывает свой ×N. Чтобы изменить: выключите, выберите другой и включите.", "开启开关时锁定的倍率；已开启的开关显示其 ×N。如需更改，请关闭、重选后再开启。", "Anahtar açılırken sabitlenen çarpan; etkin anahtar kendi ×N değerini gösterir. Değiştirmek için kapatın, seçin ve açın."),
    "UCM_CROZIER_CHEATS_TIER_1": by_language("low", "niedrig", "низко", "低", "düşük"),
    "UCM_CROZIER_CHEATS_TIER_2": by_language("medium", "mittel", "средне", "中", "orta"),
    "UCM_CROZIER_CHEATS_TIER_3": by_language("high", "hoch", "высоко", "高", "yüksek"),
    "UCM_CROZIER_CHEATS_TIER_LABEL": by_language("Amounts:", "Mengen:", "Количество:", "数量：", "Miktar:"),
    "UCM_CROZIER_CHEATS_TIER_TT": by_language("Size of one-time buttons that offer a choice; their tooltips list the Low, Medium and High values.", "Größe einmaliger Schaltflächen mit Auswahl; ihre Tooltips nennen die Werte.", "Размер разовых кнопок с выбором; их подсказки перечисляют значения.", "可选择的单次按钮的幅度，其提示列出低、中、高数值。", "Seçenekli tek seferlik düğmelerin ölçüsü; ipuçları değerleri listeler."),
    f"{P}_art_crown": by_language("The Sovereign's Crown", "Krone des Souveräns", "Корона суверена", "君主之冠", "Hükümdar Tacı"),
    f"{P}_art_crown_name": by_language("The Sovereign's Crown", "Krone des Souveräns", "Корона суверена", "君主之冠", "Hükümdar Tacı"),
    f"{P}_art_crown_desc": by_language("A legendary crown from the cheat menu. It never wears out.", "Eine legendäre Krone aus dem Cheat-Menü. Sie nutzt sich nie ab.", "Легендарная корона из чит-меню. Никогда не изнашивается.", "来自作弊菜单的传奇王冠，永不磨损。", "Hile menüsünden efsanevi taç. Asla yıpranmaz."),
    f"{P}_stress": by_language("Menu bonus: stress gain −99%", "Menübonus: Stressgewinn −99 %", "Бонус меню: прирост стресса −99%", "菜单加成：压力获取 −99%", "Menü bonusu: stres kazancı −%99"),
    f"trait_{P}_disease_shield": by_language("Disease Shield", "Krankheitsschild", "Защита от болезней", "疾病护盾", "Hastalık Kalkanı"),
    f"trait_{P}_disease_shield_desc": by_language("From the cheat menu: +50 health and no ordinary (non-epidemic) diseases.", "Aus dem Cheat-Menü: +50 Gesundheit und keine gewöhnlichen Krankheiten (außer Seuchen).", "Из чит-меню: +50 здоровья и никаких обычных болезней (кроме эпидемий).", "来自作弊菜单：+50 健康，不会染上普通（非疫病）疾病。", "Hile menüsünden: +50 sağlık ve sıradan (salgın dışı) hastalık yok."),
}


def build(lang):
    def fill(pattern, **kw):
        return pattern[lang].format(**kw)

    out, month = {}, PER_MONTH[lang]

    def toggle(k, label, tip):
        on, off = fill(ON, x=label), fill(OFF, x=label)
        out[f"{B}{k}_ON"], out[f"{B}{k}_OFF"], out[f"{B}{k}_TT"] = on, off, tip
        out[f"{P}_toast_on_{k}"], out[f"{P}_toast_off_{k}"] = fill(T_ON, x=label), fill(T_OFF, x=label)

    def action(k, label, tip):
        out[f"{B}{k}"], out[f"{B}{k}_TT"], out[f"{P}_toast_{k}"] = label, tip, fill(T_USED, x=label)

    for k, multipliers in gen_ucm_crozier.LEVELLED.items():
        name, amount = SHORT[k][lang], AMOUNTS[k].format(mo=month)
        toggle(k, fill(SCALED, x=f"{name} {amount}"), f"{fill(SCALED_TT, x=f'{name} {amount}')}\\n{FOLLOWS[lang]}")
        for i, m in enumerate(gen_ucm_crozier.STRENGTHS, 1):
            out[f"{P}_{k}_l{i}"] = fill(BONUS, x=name, m=m)
    for k, (label, tip) in HELD.items():
        toggle(k, label[lang], f"{tip[lang]}\\n{CHECKED[lang] if k.startswith('auto_') else FOLLOWS[lang]}")
    for k, (label, tip) in ACTIONS.items():
        action(k, label[lang], tip[lang])
    for k, (_, days, label) in FREQ.items():
        action(k, label[lang], fill(FREQ_TT, d=days))
    for e, key in EPIDEMIC_KEYS.items():
        action(f"t_epidemic_{e}", OUTBREAK[lang].replace("KEY", key), OUTBREAK_TT[lang])
    for prefix, keys in (("t_councillor_", COUNCIL_KEYS), ("t_cp_", COURT_KEYS)):
        for c, key in keys.items():
            action(prefix + c, APPOINT[lang].replace("KEY", key), APPOINT_TT[lang])
    del out[f"{P}_toast_toasts_toggle"]
    for i, m in enumerate(gen_ucm_crozier.STRENGTHS, 1):
        out[f"UCM_CROZIER_CHEATS_POW_{i}"] = f"×{m}"
    out.update({k: v[lang] for k, v in PANEL.items()})
    return out


def main():
    want = {f"{B}{a.split('_', 1)[1]}" for a in gen_ucm_crozier.ACTIONS} | {f"{B}{k}_ON" for k in gen_ucm_crozier.TOGGLES} | {f"{B}toasts_toggle"}
    for lang in LANGS:
        loc = build(lang)
        missing = want - set(loc)
        assert not missing, sorted(missing)
        rel = f"localization/{lang}/ucm_crozier_cheats_l_{lang}.yml"
        with open(os.path.join(MOD_DIR, rel), "w", encoding="utf-8-sig", newline="\n") as fh:
            fh.write(f"l_{lang}:\n" + "".join(f' {k}: "{v}"\n' for k, v in sorted(loc.items())))
        print(f"{rel}: {len(loc)} keys")


if __name__ == "__main__":
    main()
