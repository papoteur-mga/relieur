# A small tool to merge multiples MusicXML files in a unique one
This project is now archived. The reason is that homr include it directly and can provide a unique musicxml file from multiple files or PDF. See [https://github.com/liebharc/homr/pull/149].
## Positional arguments:
  Merge multiple MusicXML files in an unique one. You have to provide a list of files or a radical which is a common starting part of the files names.

## Examples:
- relieur page
- relieur page2 page3 page1
- relieur page -o mymusicscore.musicxml

## Options:
-  -h, --help            show help message and exit
-  -o OUTPUT, --output OUTPUT

                        File name of output
-  -d, --debug           Enable debug output

## How it works
The tool open the first file, and for each part, read and adds the measures of each the corresponding part in the next file. It remove the key and the clef of the first added measure if they are the same as the last ones of the previous file.
