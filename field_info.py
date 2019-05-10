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
    print("  * Number of Colors per Page: %d" % ff.palette.colors_per_page)
    print("  * Number of Pages: %d" % int(len(ff.palette.colors) / ff.palette.colors_per_page))
    print("  * Page Colors (A,R,G,B):")
    for i in range(int(len(ff.palette.colors) / ff.palette.colors_per_page)):
        print("    * Page %d:\t%s" % (i+1, str([str(tuple(e)).replace(' ','') for e in ff.palette.colors[i*ff.palette.colors_per_page : (i+1)*ff.palette.colors_per_page]]).replace("'",'')))

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
    print("  * Subsection 1: List of Data Structures")
    print("    * Length of Tiles Tex: %d" % len(ff.tile_map.sub1_tiles_tex))
    print("      * Tiles Tex: %s" % str(ff.tile_map.sub1_tiles_tex))
    print("    * Length of Tiles Layer: %d" % len(ff.tile_map.sub1_tiles_layer))
    print("      * Tiles Layer: %s" % str(ff.tile_map.sub1_tiles_layer))
    print("  * Subsection 2: Layer 1 Tiles")
    print("    * Number of Tiles: %d" % len(ff.tile_map.sub2_tiles))
    for i,tile in enumerate(ff.tile_map.sub2_tiles):
        print("      * Tile %d:" % (i+1))
        print("        * Destination X: %d" % tile['destination_x'])
        print("        * Destination Y: %d" % tile['destination_y'])
        print("        * Tex Page Source X: %d" % tile['tex_pg_src_x'])
        print("        * Tex Page Source Y: %d" % tile['tex_pg_src_y'])
        print("        * Tile Clut:")
        print("          * ZZ1: %d" % tile['tile_clut']['zz1'])
        print("          * Clut Number: %d" % tile['tile_clut']['clut_num'])
        print("          * ZZ2: %d" % tile['tile_clut']['zz2'])
    print("  * Subsection 3: Sprite TP Blends")
    print("    * Number of Sprite TP Blends: %d" % len(ff.tile_map.sub3_sprite_tp_blends))
    for i,tp_blend in enumerate(ff.tile_map.sub3_sprite_tp_blends):
        print("      * Sprite TP Blend %d:" % (i+1))
        print("        * ZZ: %d" % tp_blend['zz'])
        print("        * Deph: %d" % tp_blend['deph'])
        print("        * Blending Mode: %d" % tp_blend['blending_mode'])
        print("        * Page X: %d" % tp_blend['page_x'])
        print("        * Page Y: %d" % tp_blend['page_y'])
    print("  * Subsection 4: Sprite Tiles")
    print("    * Number of Sprite Tiles: %d" % len(ff.tile_map.sub4_sprite_tiles))
    for i,tile in enumerate(ff.tile_map.sub4_sprite_tiles):
        print("      * Tile %d" % (i+1))
        print("        * Destination X: %d" % tile['destination_x'])
        print("        * Destination Y: %d" % tile['destination_y'])
        print("        * Tex Page Source X: %d" % tile['tex_pg_src_x'])
        print("        * Tex Page Source Y: %d" % tile['tex_pg_src_y'])
        print("        * Tile Clut:")
        print("          * ZZ1: %d" % tile['tile_clut']['zz1'])
        print("          * Clut Number: %d" % tile['tile_clut']['clut_num'])
        print("          * ZZ2: %d" % tile['tile_clut']['zz2'])
        print("        * Sprite TP Blend:")
        print("          * ZZ: %d" % tile['sprite_tp_blend']['zz'])
        print("          * Deph: %d" % tile['sprite_tp_blend']['deph'])
        print("          * Blending Mode: %d" % tile['sprite_tp_blend']['blending_mode'])
        print("          * Page X: %d" % tile['sprite_tp_blend']['page_x'])
        print("          * Page Y: %d" % tile['sprite_tp_blend']['page_y'])
        print("        * Group: %d" % tile['group'])
        print("        * Parameter:")
        print("          * Blending: %d" % tile['param']['blending'])
        print("          * ID: %d" % tile['param']['ID'])
        print("        * State: %d" % tile['state'])
    print("  * Subsection 5: Additional Layer")
    print("    * Number of Sprite Tiles: %d" % (len(ff.tile_map.sub5_sprite_tiles)))
    for i,tile in enumerate(ff.tile_map.sub5_sprite_tiles):
        print("        * Destination X: %d" % tile['destination_x'])
        print("        * Destination Y: %d" % tile['destination_y'])
        print("        * Tex Page Source X: %d" % tile['tex_pg_src_x'])
        print("        * Tex Page Source Y: %d" % tile['tex_pg_src_y'])
        print("        * Tile Clut:")
        print("          * ZZ1: %d" % tile['tile_clut']['zz1'])
        print("          * Clut Number: %d" % tile['tile_clut']['clut_num'])
        print("          * ZZ2: %d" % tile['tile_clut']['zz2'])
        print("        * Parameter:")
        print("          * Blending: %d" % tile['param']['blending'])
        print("          * ID: %d" % tile['param']['ID'])
        print("        * State: %d" % tile['state'])

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
    except BrokenPipeError:
        stderr.close()
