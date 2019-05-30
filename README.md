# PyFF7
Niema's toolkit for playing with files from Final Fantasy VII (PC and Switch). Check out the [wiki](../../wiki) for information about Final Fantasy VII's files.

## [Field](../../wiki/Field-File-Format) Files
* **[field_change_background.py](field_change_background.py)**
    * *Change the background of a Field file*
    * Usage: `python3 <input_field_file> <input_image_file> <output_field_file>`
    * **Note:** This works perfectly for files with the same dimensions as the original, but larger images will appear zoomed-in in-game
    * **Note:** Files must have width and height that are both multiples of 256
* **[field_extract_background.py](field_extract_background.py)**
    * *Extract the background from a Field file*
    * Usage: `python3 <input_field_file> <output_image_file>`
    * **Note:** This seems to be buggy
* **[field_info.py](field_info.py)**
    * *Read the information of a Field file*
    * Usage: `python3 field_info.py <input_field_file>`

## [LGP](../../wiki/LGP-Format) Files
* **[lgp_info.py](lgp_info.py)**
    * *Read the information of an LGP archive*
    * Usage: `python3 lgp_info.py <input_lgp_file>`
* **[lgp_pack.py](lgp_pack.py)**
    * *Pack an LGP archive*
    * Usage: `python3 lgp_pack.py <input_directory> <output_lgp_file>`
* **[lgp_unpack.py](lgp_unpack.py)**
    * *Unpack an LGP archive*
    * Usage: `python3 lgp_unpack.py <input_lgp_file> <output_directory>`

## [LZSS](../../wiki/LZSS-Format) Files
* **[lzss_compress.py](lzss_compress.py)**
    * *LZSS-compress a file*
    * Usage: `python3 lzss_compress.py <input_lzss_file> <output_file>`
* **[lzss_decompress.py](lzss_decompress.py)**
    * *Decompress an LZSS-compressed file*
    * Usage: `python3 lzss_decompress.py <input_lzss_file> <output_file>`

## [NPK](../../wiki/NPK-Format) Files
* **[npk_info.py](npk_info.py)**
    * *Read the information of an NPK archive*
    * Usage: `python3 npk_info.py <input_npk_file>`
* **[npk_unpack.py](npk_unpack.py)**
    * *Unpack an NPK archive*
    * Usage: `python3 npk_unpack.py <input_npk_file> <output_directory>`

## [TEX](../../wiki/TEX-Format) Files
* **[tex_change_image.py](tex_change_image.py)**
    * *Change the image inside of a TEX file*
    * Usage: `python3 tex_change_image.py <input_tex_file> <input_image_file> <output_tex_file>`
* **[tex_convert.py](tex_convert.py)**
    * *Convert a TEX file to a regular image file*
    * Usage: `python3 tex_convert.py <input_tex_file> <output_image_file>`
* **[tex_info.py](tex_info.py)**
    * *Read the information of a TEX file*
    * Usage: `python3 tex_info.py <input_tex_file>`
