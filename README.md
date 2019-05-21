# PyFF7
Niema's toolkit for playing with files from Final Fantasy VII (PC and Switch). Check out the [wiki](../../wiki) for information about Final Fantasy VII's files.

## [LGP](../../wiki/LGP-Format) Files
* **[lgp_info.py](lgp_info.py)**
    * *Read the information of an LGP archive*
    * Usage: `python3 lgp_info.py <lgp_file>`
* **[lgp_pack.py](lgp_pack.py)**
    * *Pack an LGP archive*
    * Usage: `python3 lgp_pack.py <file_directory> <output_lgp_file>`
* **[lgp_unpack.py](lgp_unpack.py)**
    * *Unpack an LGP archive*
    * Usage: `python3 <lgp_file> <output_directory>`

## [LZSS](../../wiki/LZSS-Format) Files
* **[lzss_decompress.py](lzss_decompress.py)**
    * *Decompress an LZSS-compressed file*
    * Usage: `python3 <lzss_file> <output_file>`

## [NPK](../../wiki/NPK-Format) Files
* **[npk_info.py](npk_info.py)**
    * *Read the information of an NPK archive*
    * Usage: `python3 npk_info.py <npk_file>`
* **[npk_unpack.py](npk_unpack.py)**
    * *Unpack an NPK archive*
    * Usage: `python3 <npk_file> <output_directory>`
