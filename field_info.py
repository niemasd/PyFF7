#!/usr/bin/env python3
'''
Read the information of a Field File
Niema Moshiri 2019
'''
from PyFF7.field import FieldFile,SECTION_NAME
from sys import argv,stderr
USAGE = "USAGE: %s <field_file>" % argv[0]

def print_sec1(ff):
    print("* Section 1: %s" % SECTION_NAME[0])
    print("  * Name: %s" % ff.field_script.name)
    print("  * Creator: %s" % ff.field_script.creator)
    print("  * Version: %d" % ff.field_script.version)
    print("  * Scale: %d" % ff.field_script.scale)
    print("  * Number of Actors: %d" % len(ff.field_script.actor_names))
    print("  * Actor Names: %s" % ', '.join(ff.field_script.actor_names))
    print("  * Number of Models: %d" % ff.field_script.num_models)
    print("  * Length of Script Code: %d bytes" % len(ff.field_script.script_code))
    print("  * Number of Akao/Tutorial Blocks: %d" % len(ff.field_script.akao))
    print("  * Number of Strings: %d" % len(ff.field_script.string_data))
    for s in ff.field_script.get_strings():
        print("    * %s" % s.replace('\n','\\n'))

def print_sec2(ff):
    print("* Section 2: %s" % SECTION_NAME[1])
    print("  * Number of Cameras: %d" % len(ff.camera_matrix))
    for i,cam in enumerate(ff.camera_matrix):
        print("  * Camera %d:" % (i+1))
        for a in ('x','y','z'):
            print("    * %s-Axis Vector: %s" % (a, str(cam['vector_%s'%a])))
        print("    * Position (Camera Space): %s" % str(cam['position_camera_space']))
        print("    * Zoom: %d" % cam['zoom'])

def print_sec3(ff):
    print("* Section 3: %s" % SECTION_NAME[2])
    print("  * Scale: %d" % ff.model_loader.scale)
    print("  * Number of Models: %d" % len(ff.model_loader))
    for i,model in enumerate(ff.model_loader):
        print("  * Model %d:" % (i+1))
        print("    * Name: %s" % model['name'])
        print("    * Attribute: %d" % model['attribute'])
        print("    * HRC Name: %s" % model['hrc'])
        print("    * Scale: %d" % model['scale'])
        for l in range(1,4):
            print("    * Light %d Color (RGB): (%d, %d, %d)" % tuple([l]+model['light_%d'%l]['color']))
            print("    * Light %d Coordinates (x,y,z): (%d, %d, %d)" % tuple([l]+model['light_%d'%l]['coord']))
        print("    * Global Light Color (RGB): (%d, %d, %d)" % tuple(model['global_light_color']))
        print("    * Number of Animations: %d" % len(model['animations']))
        for j,animation in enumerate(model['animations']):
            print("    * Animation %d:" % (j+1))
            print("      * Name: %s" % animation['name'])
            print("      * Attribute: %d" % animation['attribute'])

def print_sec4(ff):
    print("* Section 4: %s" % SECTION_NAME[3])
    print("  * PalX: %d" % ff.palette.palX)
    print("  * PalY: %d" % ff.palette.palY)
    print("  * Number of Colors per Page: %d" % ff.palette.get_num_colors_per_page())
    print("  * Number of Pages: %d" % ff.palette.get_num_color_pages())
    print("  * Page Colors (R,G,B,A):")
    for i,p in enumerate(ff.palette.color_pages):
        print("    * Page %d:\t%s" % (i+1, str([str(tuple(e)).replace(' ','') for e in p]).replace("'",'')))

def print_sec5(ff):
    print("* Section 5: %s" % SECTION_NAME[4])
    print("  * Number of Sectors: %d" % len(ff.walkmesh))
    for i in range(len(ff.walkmesh)):
        sec,acc = ff.walkmesh[i]
        print("  * Sector %d" % (i+1))
        for j,k in enumerate(['X','Y','Z']):
            print("    * Sector Pool Vertex %s: %s" % (k, str(sec[j])))
        print("    * Access Pool: %s" % str(acc))

def print_sec6(ff):
    print("* Section 6: %s" % SECTION_NAME[5])
    print("  * Size: %d bytes" % len(ff.tile_map))

def print_sec7(ff):
    print("* Section 7: %s" % SECTION_NAME[6])
    for ti,table in enumerate([ff.encounter.table_1,ff.encounter.table_2]):
        print("  * Table %d:" % (ti+1))
        print("    * Enabled: %s" % bool(table['enabled']))
        print("    * Rate: %d" % table['rate'])
        print("    * Pad: %s bytes" % len(table['pad']))
        for k in ['standard','special']:
            if sum(enc['prob'] == 0 for enc in table[k]) == len(table[k]):
                continue
            print("    * %s Encounters:" % k.capitalize())
            for i,enc in enumerate(table[k]):
                if enc['prob'] != 0:
                    print("      * ID: %d" % enc['ID'])
                    print("      * Probability: %f" % enc['prob'])

def print_sec8(ff):
    print("* Section 8: %s" % SECTION_NAME[7])
    print("  * Name: %s" % ff.triggers.name)
    print("  * Control Direction: %d" % ff.triggers.control_direction)
    print("  * Focus Height: %d" % ff.triggers.focus_height)
    print("  * Camera Range:")
    for d in ['left','bottom','right','top']:
        print("    * %s: %d" % (d.capitalize(), ff.triggers.camera_range[d]))
    for k in ['layer_3', 'layer_4']:
        print("  * %s:" % k.capitalize().replace('_',' '))
        print("    * Unknown 1: %d" % ff.triggers.unknown_1[k])
        print("    * Background Animation: %d x %d" % (ff.triggers.bg_animation[k]['width'], ff.triggers.bg_animation[k]['height']))
        print("    * Unknown 2: %d bytes" % len(ff.triggers.unknown_2[k]))
    print("  * Gateways:")
    for i,gateway in enumerate(ff.triggers.gateways):
        print("    * Gateway %d:" % (i+1))
        print("      * Field ID: %d" % gateway['field_ID'])
        for k in ['exit_vertex_1', 'exit_vertex_2', 'destination_vertex']:
            print("      * %s: %s" % (k.replace('_',' ').title(), str(tuple(gateway[k]))))
        print("      * Unknown: %d bytes" % len(gateway['unknown']))
    print("  * Triggers:")
    for i,trigger in enumerate(ff.triggers.triggers):
        print("    * Trigger %d:" % (i+1))
        for k in ['vertex_corner_1', 'vertex_corner_2']:
            print("      * %s: %s" % (k.replace('_',' ').title(), str(tuple(trigger[k]))))
        print("      * Background Group ID: %d" % trigger['bg_group_ID'])
        print("      * Background Frame ID: %d" % trigger['bg_frame_ID'])
        print("      * Behavior: %d" % trigger['behavior'])
        print("      * Sound ID: %d" % trigger['sound_ID'])
    print("  * Shown Arrows: %s" % str(ff.triggers.shown_arrows))
    print("  * Arrows:")
    for i,arrow in enumerate(ff.triggers.arrows):
        print("    * Arrow %d:" % (i+1))
        print("      * Type: %d" % arrow['type'])
        print("      * Position: %s" % str(arrow['position']))

def print_sec9_tile(tile):
    print("          * Destination: (%d, %d)" % (tile['dst_x'],tile['dst_y']))
    print("          * Source: (%d, %d)" % (tile['src_x'],tile['src_y']))
    print("          * Source 2: (%d, %d)" % (tile['src_x2'],tile['src_y2']))
    print("          * Dimensions: %d x %d" % (tile['width'],tile['height']))
    print("          * Palette ID: %d" % tile['palette_ID'])
    print("          * ID: %d" % tile['ID'])
    print("          * Param: %d" % tile['param'])
    print("          * State: %d" % tile['state'])
    print("          * Blending: %d" % tile['blending'])
    print("          * Type Trans: %d" % tile['type_trans'])
    print("          * Texture ID: %d" % tile['texture_id'])
    print("          * Texture ID 2: %d" % tile['texture_id2'])
    print("          * Depth: %d" % tile['depth'])
    print("          * ID Big: %d" % tile['ID_big'])

def print_sec9(ff):
    print("* Section 9: %s" % SECTION_NAME[8])
    print("  *  Header:")
    print("    * Depth: %d" % ff.background.header['depth'])
    print("    * Unknown 1: %d" % ff.background.header['unknown1'])
    print("    * Unknown 2: %d" % ff.background.header['unknown2'])
    print("  * Palette:")
    print("    * Size: %d" % ff.background.palette['size'])
    print("    * PalX: %d" % ff.background.palette['palX'])
    print("    * PalY: %d" % ff.background.palette['palY'])
    print("    * Width: %d" % ff.background.palette['width'])
    print("    * Height: %d" % ff.background.palette['height'])
    print("    * Colors (R,G,B,A): %s" % str([str(tuple(e)).replace(' ','') for e in ff.background.palette['colors']]).replace("'",''))
    print("  * Background:")
    print("    * Layer 1:")
    print("      * Width: %d" % ff.background.back['layer_1']['width'])
    print("      * Height: %d" % ff.background.back['layer_1']['height'])
    print("      * Depth: %d" % ff.background.back['layer_1']['depth'])
    print("      * Number of Tiles: %d" % len(ff.background.back['layer_1']['tiles']))
    for i,tile in enumerate(ff.background.back['layer_1']['tiles']):
        print("        * Tile %d:" % (i+1))
        print_sec9_tile(tile)
    for k in ['layer_2','layer_3','layer_4']:
        if len(ff.background.back[k]) != 0:
            print("    * %s:" % k.replace('_',' ').title())
            print("      * Width: %d" % ff.background.back[k]['width'])
            print("      * Height: %d" % ff.background.back[k]['height'])
            print("      * Number of Tiles: %d" % len(ff.background.back[k]['tiles']))
            for i,tile in enumerate(ff.background.back[k]['tiles']):
                print("        * Tile %d:" % (i+1))
                print_sec9_tile(tile)
    print("  * Number of Textures: %d" % sum(tex is not None for tex in ff.background.textures))
    for i,tex in enumerate(ff.background.textures):
        if tex is not None:
            print("    * Texture %d:" % (i+1))
            print("      * Size: %d" % tex['size'])
            print("      * Depth: %d" % tex['depth'])
            print("      * Data: %d bytes" % len(tex['data']))

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print(USAGE); exit(1)
    ff = FieldFile(argv[1])
    try:
        print("Information")
        print("* File Name: %s" % argv[1])
        print()
        print_sec1(ff)
        print()
        print_sec2(ff)
        print()
        print_sec3(ff)
        print()
        print_sec4(ff)
        print()
        print_sec5(ff)
        print()
        print_sec6(ff)
        print()
        print_sec7(ff)
        print()
        print_sec8(ff)
        print()
        print_sec9(ff)
    except BrokenPipeError:
        stderr.close()
