#!/usr/bin/env python3
'''
Read the information of a save file
Niema Moshiri 2019
'''
from PyFF7.save import PORTRAIT_TO_NAME,PROP,Save
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
            if s['data']['checksum'] == 0:
                print("  * Save Slot %d: Empty" % (i+1)); continue
            else:
                print("  * Save Slot %d:" % (i+1))
            print("    * Checksum: 0x%04X" % s['data']['checksum'])
            print("    * Unknown 1: %d" % s['data']['unknown1'])
            print("    * Preview:")
            print("      * Lead Character's Level: %d" % s['data']['preview']['level'])
            print("      * Party: %s" % ', '.join([PORTRAIT_TO_NAME[s['data']['preview']['portrait%d'%j]] for j in [1,2,3] if s['data']['preview']['portrait%d'%j] != 255]))
            print("      * Lead Character's Name: %s" % s['data']['preview']['name'])
            print("      * Lead Character's HP: %d/%d" % (s['data']['preview']['curr_hp'], s['data']['preview']['max_hp']))
            print("      * Lead Character's MP: %d/%d" % (s['data']['preview']['curr_mp'], s['data']['preview']['max_mp']))
            print("      * Total Gil: %d" % s['data']['preview']['gil'])
            print("      * Playtime (seconds): %d" % s['data']['preview']['playtime'])
            print("      * Save Location: %s" % s['data']['preview']['location'])
            print("    * Window Color:")
            for k in ['upper_left', 'upper_right', 'lower_left', 'lower_right']:
                print("      * %s: %s" % (k.replace('_',' ').capitalize(), '#%02X%02X%02X'%s['data']['window_color'][k]))
            for k in ['Cloud']:
                rec = s['data']['record'][k.lower()]
                print("    * Character Record: %s" % k)
                print("      * Name: %s" % rec['name'])
                print("      * Vincent -> Sephiroth Flag: %s" % bool(rec['sephiroth_flag']))
                print("      * Level: %d" % rec['level'])
                print("      * Status:")
                for k in ['strength','vitality','magic','spirit','dexterity','luck']:
                    print("        * %s: %d" % (k.capitalize(), rec['status'][k]))
                print("      * Bonus:")
                for k in ['strength','vitality','magic','spirit','dexterity','luck']:
                    print("        * %s: %d" % (k.capitalize(), rec['bonus'][k]))
                print("      * Limit Level: %d" % rec['limit_level'])
                print("      * Limit Bar: %d%%" % int(100.*rec['limit_bar']/255.))
                print("      * Weapon: %d" % rec['weapon'])
                print("      * Armor: %d" % rec['armor'])
                print("      * Accessory: %d" % rec['accessory'])
                print("      * Character Flags: %s" % ' '.join(bin(e).lstrip('0b').zfill(8) for e in rec['flags']))
    except BrokenPipeError:
        stderr.close()
