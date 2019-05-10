#!/usr/bin/env python3
'''
Functions and classes for handling Final Fantasy VII text
A lot of this is borrowed from FF7Tools V1.3 (https://github.com/cebix/ff7tools)
Niema Moshiri 2019
'''
from . import NULL_BYTE,NULL_STR
from struct import unpack

# Characters in range 0x00..0xdf directly map to Unicode characters
# This is almost identical to the MacOS Roman encoding shifted down by 32 positions
CHAR = {
    'NORMAL': (
        u" !\"#$%&'()*+,-./01234"
        u"56789:;<=>?@ABCDEFGHI"
        u"JKLMNOPQRSTUVWXYZ[\\]^"
        u"_`abcdefghijklmnopqrs"
        u"tuvwxyz{|}~ ÄÅÇÉÑÖÜáà"
        u"âäãåçéèêëíìîïñóòôöõúù"
        u"ûü♥°¢£↔→♪ßα  ´¨≠ÆØ∞±≤"  # '♥' (0x80), '↔' (0x84), '→' (0x85), '♪' (0x86), and 'α' (0x88) are additions
        u"≥¥µ∂ΣΠπ⌡ªºΩæø¿¡¬√ƒ≈∆«"
        u"»… ÀÃÕŒœ–—“”‘’÷◊ÿŸ⁄ ‹"
        u"›ﬁﬂ■‧‚„‰ÂÊÁËÈÍÎÏÌÓÔ Ò"
        u"ÚÛÙıˆ˜¯˘˙˚¸˝˛ˇ       "
    ),

    # Japanese font texture 1, CLUT 0, upper half
    'NORMAL_JP': (
        u"バばビびブぶベべボぼガがギぎグぐゲげゴごザ"
        u"ざジじズずゼぜゾぞダだヂぢヅづデでドどヴパ"
        u"ぱピぴプぷペぺポぽ0123456789、。"
        u" ハはヒひフふヘへホほカかキきクくケけコこ"
        u"サさシしスすセせソそタたチちツつテてトとウ"
        u"うアあイいエえオおナなニにヌぬネねノのマま"
        u"ミみムむメめモもラらリりルるレれロろヤやユ"
        u"ゆヨよワわンんヲをッっャゃュゅョょァぁィぃ"
        u"ゥぅェぇォぉ!?『』．+ABCDEFGHI"
        u"JKLMNOPQRSTUVWXYZ・*ー〜"
        u"…%/:&【】♥→αβ「」()-=   ⑬"
    ),

    # Japanese font texture 1, CLUT 0, lower half
    'KANJI_SET1': (
        u"必殺技地獄火炎裁雷大怒斬鉄剣槍海衝聖審判転"
        u"生改暗黒釜天崩壊零式自爆使放射臭息死宣告凶"
        u"破晄撃画龍晴点睛超究武神覇癒風邪気封印吹烙"
        u"星守護命鼓動福音掌打水面蹴乱闘合体疾迅明鏡"
        u"止抜山蓋世血祭鎧袖一触者滅森羅万象装備器攻"
        u"魔法召喚獣呼出持相手物確率弱投付与変化片方"
        u"行決定分直前真似覚列後位置防御発回連続敵全"
        u"即効果尾毒消金針乙女興奮剤鎮静能薬英雄榴弾"
        u"右腕砂時計糸戦惑草牙南極冷結晶電鳥角有害質"
        u"爪光月反巨目砲重力球空双野菜実兵単毛茶色髪"
    ),

    # Japanese font texture 1, CLUT 1, upper half
    'KANJI_SET2': (
        u"安香花会員蜂蜜館下着入先不子供屋商品景交換"
        u"階模型部離場所仲間無制限殿様秘氷河図何材料"
        u"雪上進事古代種鍵娘紙町住奥眠楽最初村雨釘陸"
        u"吉揮叢雲軍異常通威父蛇矛青偃刀戟十字裏車円"
        u"輪卍折鶴倶戴螺貝突銀玉正宗具甲烈属性吸収半"
        u"減土高級状態縁闇睡石徐々的指混呪開始歩復盗"
        u"小治理同速遅逃去視複味沈黙還倍数瀕取返人今"
        u"差誰当拡散飛以外暴避振身中旋津波育機械擲炉"
        u"新両本君洞内作警特殊板強穴隊族亡霊鎖足刃頭"
        u"怪奇虫跳侍左首潜長親衛塔宝条像忍謎般見報充"
        u"填完了銃元経験値終獲得名悲蛙操成費背切替割"
    ),

    # Japanese font texture 1, CLUT 1, lower half
    'KANJI_SET3': (
        u"由閉記憶選番街底忘都過艇路運搬船基心港末宿"
        u"西道艦家乗竜巻迷宮絶壁支社久件想秒予多落受"
        u"組余系標起迫日勝形引現解除磁互口廃棄汚染液"
        u"活令副隠主斉登温泉百段熱走急降奪響嵐移危戻"
        u"遠吠軟骨言葉震叫噴舞狩粉失敗眼激盤逆鱗踏喰"
        u"盾叩食凍退木吐線魅押潰曲翼教皇太陽界案挑援"
        u"赤往殴意東北参知聞来仕別集信用思毎悪枯考然"
        u"張好伍早各独配腐話帰永救感故売浮市加流約宇"
        u"礼束母男年待宙立残俺少精士私険関倒休我許郷"
        u"助要問係旧固荒稼良議導夢追説声任柱満未顔旅"
    ),

    # Japanese font texture 2, CLUT 0
    'KANJI_SET4': (
        u"友伝夜探対調民読占頼若学識業歳争苦織困答準"
        u"恐認客務居他再幸役縮情豊夫近窟責建求迎貸期"
        u"工算湿難保帯届凝笑向可遊襲申次国素題普密望"
        u"官泣創術演輝買途浴老幼利門格原管牧炭彼房驚"
        u"禁注整衆語証深層査渡号科欲店括坑酬緊研権書"
        u"暇兄派造広川賛駅絡在党岸服捜姉敷胸刑谷痛岩"
        u"至勢畑姿統略抹展示修酸製歓接障災室索扉傷録"
        u"優基讐勇司境璧医怖狙協犯資設雇根億脱富躍純"
        u"写病依到練順園総念維検朽圧補公働因朝浪祝恋"
        u"郎勉春功耳恵緑美辺昇悩泊低酒影競二矢瞬希志"
    ),

    # Japanese font texture 2, CLUT 1
    'KANJI_SET5': (
        u"孫継団給抗違提断島栄油就僕存企比浸非応細承"
        u"編排努締談趣埋営文夏個益損額区寒簡遣例肉博"
        u"幻量昔臓負討悔膨飲妄越憎増枚皆愚療庫涙照冗"
        u"壇坂訳抱薄義騒奴丈捕被概招劣較析繁殖耐論貴"
        u"称千歴史募容噂壱胞鳴表雑職妹氏踊停罪甘健焼"
        u"払侵頃愛便田舎孤晩清際領評課勤謝才偉誤価欠"
        u"寄忙従五送周頑労植施販台度嫌諸習緒誘仮借輩"
        u"席戒弟珍酔試騎霜鉱裕票券専祖惰偶怠罰熟牲燃"
        u"犠快劇拠厄抵適程繰腹橋白処匹杯暑坊週秀看軽"
        u"棊和平王姫庭観航横帳丘亭財律布規謀積刻陥類"
    ),

    # Special characters of the field module (0xe0..0xff)
    'FIELD_SPECIAL': {
        # Not in Japanese version, where 0xe0..0xe6 are regular characters:
        0xE0: u"{CHOICE}", # choice tab (10 spaces)
        0xE1: u"\t",       # tab (4 spaces)
        0xE2: u", ",       # shortcut
        0xE3: u'."',       # not very useful shortcut with the wrong quote character...
        0xE4: u'…"',       # not very useful shortcut with the wrong quote character...

        # In all versions
        0xE6: u"⑬",        # appears in the US version of BLACKBG6, presumably a mistake
        0xE7: u"\n",       # new line
        0xE8: u"{NEW}",    # new page

        0xEA: u"{CLOUD}",
        0xEB: u"{BARRET}",
        0xEC: u"{TIFA}",
        0xED: u"{AERITH}",
        0xEE: u"{RED XIII}",
        0xEF: u"{YUFFIE}",
        0xF0: u"{CAIT SITH}",
        0xF1: u"{VINCENT}",
        0xF2: u"{CID}",
        0xF3: u"{PARTY #1}",
        0xF4: u"{PARTY #2}",
        0xF5: u"{PARTY #3}",

        0xF6: u"〇",       # controller button
        0xF7: u"△",        # controller button
        0xF8: u"☐",        # controller button
        0xF9: u"✕",        # controller button

        0xFA: u"",         # kanji 1
        0xFB: u"",         # kanji 2
        0xFC: u"",         # kanji 3
        0xFD: u"",         # kanji 4

        #0xFE              # extended control code, see below
        #0xFF              # end of string
    },

    # Extended control codes of the field module (0xfe ..)
    'FIELD_CONTROL': {
        0xD2: u"{GRAY}",
        0xD3: u"{BLUE}",
        0xD4: u"{RED}",
        0xD5: u"{PURPLE}",
        0xD6: u"{GREEN}",
        0xD7: u"{CYAN}",
        0xD8: u"{YELLOW}",
        0xD9: u"{WHITE}",
        0xDA: u"{FLASH}",
        0xDB: u"{RAINBOW}",

        0xDC: u"{PAUSE}",   # pause until OK button is pressed
        #0xDD               # wait # of frames
        0xDE: u"{NUM}",     # decimal variable
        0xDF: u"{HEX}",     # hex variable
        0xE0: u"{SCROLL}",  # wait for OK butten, then scroll window
        0xE1: u"{RNUM}",    # decimal variable, right-aligned
        #0xE2               # value from game state memory
        0xE9: u"{FIXED}",   # fixed-width character spacing on/off
    },

    # Characters which must be escaped when decoding
    'ESCAPE': set(u"\\{}"),
}
KANJI_BANK = {0xFA:'KANJI_SET1', 0xFB:'KANJI_SET2', 0xFC:'KANJI_SET3', 0xFD:'KANJI_SET4', 0xFE:'KANJI_SET5'}
#FIELD_COMMAND = {**{v:k for k, v in CHAR['FIELD_SPECIAL'].items() if v}, **{v:('\xfe' + k) for k, v in CHAR['FIELD_CONTROL'].items()}}

# errors

def decode_kanji(bank, code):
    '''Decode a Kanji given code from a given bank

    Args:
        ``bank`` (``str``): The bank

        ``code`` (``int``): The code

    Returns:
        ``str``: The decoded Kanji string
    '''
    if bank not in bank_to_key:
        raise IndexError("Invalid kanji bank %02x" % bank)
    return CHAR[KANJI_BANK[bank]][code]

def decode_field_text(data, JP=False):
    '''Decode Field text to unicode

    Args:
        ``data`` (``bytes``): Raw Field text to decode

        ``JP`` (``bool``): ``True`` if the text to decode is Japanese, otherwise ``False``

    Returns:
        ``str``: Decoded unicode text
    '''
    if not isinstance(data,bytes) and not isinstance(data,bytearray):
        raise TypeError("Expected bytes, but received %s" % str(type(data)))
    char_set = {True:CHAR['NORMAL_JP'], False:CHAR['NORMAL']}[JP]
    num_normal_chars = {True:0xE7, False:0xE0}[JP]
    text = u''; i = 0
    while i < len(data):
        c = data[i]; i += 1
        # end of string
        if c == 0xFF:
            break

        # regular printable character
        elif c < num_normal_chars:
            t = char_set[c]
            if t in CHAR['ESCAPE']:
                text += u"\\"
            text += t

        # Kanji
        elif 0xFA <= c <= 0xFD and JP:
            if i >= len(data):
                raise IndexError("Spurious kanji code %02x at end of string %r" % (c, data))
            k = data[i]; i += 1; text += decode_kanji(c,k)

        # Field module control code or Kanji
        elif c == 0xFE:
            if i >= len(data):
                raise IndexError("Spurious control code %02x at end of string %r" % (c, data))
            k = data[i]; i += 1

            # regular Kanji
            if k < 0xD2 and JP:
                text += decode_kanji(c, k)

            # WAIT <arg> command
            elif k == 0xDD:
                if i >= len(data) - 1:
                    raise IndexError("Spurious WAIT command at end of string %r" % data)
                arg = unpack('H', data[i:i+2])[0]; i += 2; text += u"{WAIT %d}" % arg

            # STR <offset> <length> command
            elif k == 0xE2:
                if i >= len(data) - 3:
                    raise IndexError("Spurious STR command at end of string %r" % data)
                offset = unpack('H', data[i:i+2])[0]; length = unpack('H', data[i+2:i+4])[0]; i += 4; text += u"{STR %04x %04x}" % (offset, length)

            # Other control code
            else:
                if k not in CHAR['FIELD_CONTROL']:
                    raise IndexError("Illegal control code %02x in field string %r" % (k, data))
                text += CHAR['FIELD_CONTROL'][k]

        # Field module special character
        else:
            t = CHAR['FIELD_SPECIAL'][c]
            if not t:
                raise IndexError("Illegal character %02x in field string %r" % (c, data))

            # newline after {NEW}
            if c == 0xE8:
                t += '\n'
            text += t
    return text
