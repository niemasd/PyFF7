#!/usr/bin/env python3
'''
Read the information of a save file
Niema Moshiri 2019
'''
from PyFF7 import ITEM_DB,MATERIA_DB
from PyFF7.save import PORTRAIT_TO_NAME,PROP,Save,SAVE_MODULE
from sys import argv,stderr
USAGE = "USAGE: %s <input_save_file>" % argv[0]

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    sav = Save(argv[1]); prop = PROP[sav.save_type]
    try:
        print("* File Name: %s" % argv[1])
        print("* Save Type: %s" % prop['label'])
        print("* Number of Save Slots: %s" % len(sav))
        for i,s in enumerate(sav):
            d = s['data']
            if d['checksum'] == 0:
                print("  * Save Slot %d: Empty" % (i+1)); continue
            else:
                print("  * Save Slot %d:" % (i+1))
            print("    * Checksum: 0x%04X" % d['checksum'])
            print("    * Preview:")
            print("      * Lead Character's Level: %d" % d['preview']['level'])
            print("      * Party: %s" % ', '.join([PORTRAIT_TO_NAME[v] for v in d['preview']['party'] if v != 255]))
            print("      * Lead Character's Name: %s" % d['preview']['name'])
            print("      * Lead Character's HP: %d/%d" % (d['preview']['curr_hp'], d['preview']['max_hp']))
            print("      * Lead Character's MP: %d/%d" % (d['preview']['curr_mp'], d['preview']['max_mp']))
            print("      * Total Gil: %d" % d['preview']['gil'])
            print("      * Play Time (seconds): %d" % d['preview']['playtime'])
            print("      * Save Location: %s" % d['preview']['location'])
            print("    * Party: %s" % ', '.join([PORTRAIT_TO_NAME[v] for v in d['party'] if v != 255]))
            print("    * Total Gil: %d" % d['gil'])
            print("    * Play Time (seconds): %d.%s" % (d['playtime'][0], str(d['playtime'][1]).lstrip('0.')))
            print("    * Game Time (HHH:MM:SS.TTT): %s:%s:%s.%s" % (str(d['gametime'][0]).zfill(3), str(d['gametime'][1]).zfill(2), str(d['gametime'][2]).zfill(2), str(d['gametime'][3]).zfill(3)))
            print("    * Save Location: Module = %s, Location = %d, Map Location (X,Y,Triangle) = %s, Map Direction = %d" % (SAVE_MODULE[d['curr_module']], d['curr_location'], str(tuple(d['map_location'])).replace(' ',''), d['map_direction']))
            print("    * Plot Progression Variable: %d" % d['plot_progress'])
            print("    * Number of Battles: Fought %d, Escaped %d" % (d['num_battles'], d['num_escapes']))
            print("    * Countdown Timer (seconds) %d.%s" % (d['countdown'][0], str(d['countdown'][1]).lstrip('0.')))
            print("    * Encounter Timer: Seed = %d, Offset = %d" % (d['encounter_timer']['seed'], d['encounter_timer']['offset']))
            print("    * Love Points:")
            for ch in ['aerith','tifa','yuffie','barret']:
                print("      * %s: %d" % (ch.capitalize(), d['love'][ch]))
            print("    * Window Color:")
            for k in ['upper_left', 'upper_right', 'lower_left', 'lower_right']:
                print("      * %s: %s" % (k.replace('_',' ').capitalize(), '#%02X%02X%02X'%d['window_color'][k]))
            for ch in ['Cloud', 'Barret', 'Tifa', 'Aerith', 'Red XIII', 'Yuffie', 'Cait Sith', 'Vincent', 'Cid']:
                rec = d['record'][ch.replace(' ','').lower()]
                print("    * Character Record: %s" % ch)
                print("      * Name: %s" % rec['name'])
                print("      * Level: %d" % rec['level'])
                print("      * Experience: %d/%d" % (rec['exp_curr'], rec['exp_curr']+rec['exp_next']))
                print("      * HP: %d/%d (base %d)" % (rec['curr_hp'], rec['max_hp'], rec['base_hp']))
                print("      * MP: %d/%d (base %d)" % (rec['curr_mp'], rec['max_mp'], rec['base_mp']))
                print("      * Vincent -> Sephiroth Flag: %s" % bool(rec['sephiroth_flag']))
                print("      * Status:")
                for k in ['strength','vitality','magic','spirit','dexterity','luck']:
                    print("        * %s: %d" % (k.capitalize(), rec['status'][k]))
                print("      * Bonus:")
                for k in ['strength','vitality','magic','spirit','dexterity','luck']:
                    print("        * %s: %d" % (k.capitalize(), rec['bonus'][k]))
                print("      * Limit Level: %d" % rec['limit_level'])
                print("      * Limit Bar: %d%%" % int(100.*rec['limit_bar']/255.))
                for k in ['weapon','armor']:
                    print("      * %s: %d" % (k.capitalize(), rec[k]))
                    print("        * Equipped Materia: %s" % [v for v in rec['materia'][k] if v != 255])
                print("      * Character Flags: %s" % ' '.join(bin(e).lstrip('0b').zfill(8) for e in rec['flags']))
                print("      * Learned Limit Skills: %s" % ' '.join(bin(e).lstrip('0b').zfill(8) for e in rec['limit_skills']))
                print("      * Number of Kills: %d" % rec['num_kills'])
                print("      * Number of Limit Uses:")
                for j in [1,2,3]:
                    print("        * Limit %d-1: %d" % (j,rec['num_limit_uses_%d_1'%j]))
                print("      * Unknown 2: %d" % rec['unknown2'])
                print("      * Unknown 3: %s" % ''.join('%X'%v for v in rec['unknown3']))
            print("    * Item Stock:")
            for v in d['stock']['item']:
                if v[0] != (255, 1): # empty slot
                    print("      * %dx %s" % (v[1], ITEM_DB[v[0]]))
            print("    * Materia Stock:")
            for v in d['stock']['materia']:
                if v[0] != 255: # empty slot
                    print("      * %s (%d AP)" % (MATERIA_DB[v[0]], v[1]))
            print("    * Materia Stolen by Yuffie:")
            for v in d['stolen_materia']:
                if v[0] != 255: # empty slot
                    print("      * %s (%d AP)" % (MATERIA_DB[v[0]], v[1]))
            print("    * Unknown 4: %s" % d['unknown4'])
            print("    * Unknown 8: %d" % d['unknown8'])
            print("    * Unknown 9: %s" % d['unknown9'])
            print("    * Unknown 10: %d" % d['unknown10'])
            print("    * Unknown 11: %s" % d['unknown11'])
    except BrokenPipeError:
        stderr.close()
