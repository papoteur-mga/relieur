import argparse
import os
import sys
from pathlib import Path
from glob import glob

import musicxml.xmlelement.xmlelement as mxl  # type: ignore
from musicxml.parser.parser import parse_musicxml  # type: ignore

def clef_attributes(clef)->dict[str]: # type ignore
    # take mxl.XMLClef
    attributes = {}
    for a in clef.get_children_of_type(mxl.XMLSign):
        attributes["Sign"] = a.value_
    for a in clef.get_children_of_type(mxl.XMLSign):
        attributes["Line"] = a.value_
    for a in clef.get_children_of_type(mxl.XMLClefOctaveChange,):
        attributes["ClefOctaveChange"] = a.value_
    return attributes

def time_attributes(time)->dict[str]: # type ignore
    # take mxl.XMLTime
    attributes = {}
    for a in time.get_children_of_type(mxl.XMLBeats):
        attributes["Beats"] = a.value_
    for a in time.get_children_of_type(mxl.XMLBeatType):
        attributes["BeatType"] = a.value_
    for a in time.get_children_of_type(mxl.XMLInterchangeable):
        attributes["Interchangeable"] = a.value_
    for a in time.get_children_of_type(mxl.XMLSenzaMisura):
        attributes["SenzaMisura"] = a.value_
    return attributes

def key_attributes(key)->dict[str]: # type ignore
    # take mxl.XMLKey
    attributes = {}
    for a in key.get_children_of_type(mxl.XMLFifths):
        attributes["Fifths"] = a.value_
    for a in key.get_children_of_type(mxl.XMLKeyAlter):
        attributes["KeyAlter"] = a.value_
    for a in key.get_children_of_type(mxl.XMLMode):
        attributes["Mode"] = a.value_
    return attributes

def process_concat(
    concat: tuple[str],
    debug=False,
    ) -> tuple:
    sorted_list = get_file_list(concat, debug=debug)
    if not sorted_list:
        return None, 0, 0
    # Main file is the first of the list
    main_file = sorted_list[0]
    print(f"Starting with {main_file}")
    m = parse_musicxml(main_file)
    # look for the last key and last divisions
    last_parts_attributes = []
    part1 = None  # Initialize part1 to avoid UnboundLocalError
    for part1 in m.get_children_of_type(mxl.XMLPart):
        part_attributes = {}
        for measure in part1.get_children_of_type(mxl.XMLMeasure):
            for attrib in measure.get_children_of_type(mxl.XMLAttributes):
                for div in attrib.get_children_of_type(mxl.XMLDivisions):
                    part_attributes['Divisions'] = div.value_
                for key in attrib.get_children_of_type(mxl.XMLKey):
                    part_attributes['Key'] = key_attributes(key)
                for xtime in attrib.get_children_of_type(mxl.XMLTime):
                    part_attributes['Time'] = time_attributes(xtime)
                for clef in attrib.get_children_of_type(mxl.XMLClef):
                    part_attributes['Clef'] = clef_attributes(clef)
        last_parts_attributes.append(part_attributes)
    for f in sorted_list[1:]:
        # new file to add
        if debug:
            print(f"Processing {f}")
        b = parse_musicxml(f)
        ip = 0
        for part1 in m.get_children_of_type(mxl.XMLPart):
            # each part from the main score
            current_len = len(part1.get_children_of_type(mxl.XMLMeasure))
            if debug:
                print(f"Main part has {current_len} measures")
            ib = 0
            for part in b.get_children_of_type(mxl.XMLPart):
                if ib == ip:
                    # we add the part of the new file having the same order as the part from the main score, else we pass
                    for measure in part.get_children_of_type(mxl.XMLMeasure):
                        new_number = str(int(measure.number) + current_len)
                        if int(measure.number) == 1:
                            for attrib in measure.get_children_of_type(mxl.XMLAttributes):
                                for div in attrib.get_children_of_type(mxl.XMLDivisions):
                                    if last_parts_attributes[ib]['Divisions'] == div.value_:
                                        attrib.remove(div)
                                        if debug:
                                            print(f"Remove division at measure {new_number}, part {ib + 1}")
                                for key in attrib.get_children_of_type(mxl.XMLKey):
                                    if last_parts_attributes[ib]['Key'] == key_attributes(key):
                                        if debug:
                                            print(f"Remove key at measure {new_number}, part {ib + 1}")
                                        attrib.remove(key)
                                for xtime in attrib.get_children_of_type(mxl.XMLTime):
                                    if last_parts_attributes[ib]['Time'] == time_attributes(xtime):
                                        attrib.remove(xtime)
                                        if debug:
                                            print(f"Remove time at measure {new_number}, part {ib + 1}")
                                for clef in attrib.get_children_of_type(mxl.XMLClef):
                                    if last_parts_attributes[ib]['Clef'] == clef_attributes(clef):
                                        attrib.remove(clef)
                                        if debug:
                                            print(f"Remove clef at measure {new_number}, part {ib + 1}")
                        measure.number = new_number
                        part1.add_child(measure)
                        if debug:
                            print(f"Added measure {new_number}, part {ib + 1}")
                    current_len = len(part1.get_children_of_type(mxl.XMLMeasure))
                ib += 1
            ip +=1
    return m, len(sorted_list), len(part1.get_children_of_type(mxl.XMLMeasure)) if part1 else 0

def get_file_list(
    concat: tuple[str],
    debug=False,
    ) -> list[str]:
    # get the list of files
    sorted_list = []

    for pattern in concat:
        if not Path(pattern).suffix:
            pattern += "*.musicxml"

        matched_files = list(glob(pattern))

        if len(matched_files) == 0 and debug:
            print(f"No file found for {pattern}")

        for fichier in matched_files:
            if not os.path.exists(fichier):
                if debug:
                    print(f"The file {fichier} does not exist.")
                return None
            if os.path.isdir(fichier):
                if debug:
                    print(f"{fichier} is a directory.")
                return None

            sorted_list.append(fichier)
    if len(sorted_list) == 0:
        print(f"No files found for {concat}")
        return None
    return sorted(sorted_list)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="relieur", description="A small tool to merge multiples MusicXML files in a unique one"
    )
    parser.add_argument("concat", type=str, nargs="+", help="Merge multiple MusicXML files in an unique one."
        + "You have to provide a list of files or a radical which is a common starting part of the files names."
        + "Examples:"
        + "relieur page"
        + "relieur page2 page3 page1"
        + "relieur page -o mymusicscore.musicxml"
    )
    parser.add_argument("-o", "--output", type=str, help="File name of output")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    if not args.concat:
        print("No files list provided nor radical")
        parser.print_help()
        sys.exit(1)
    elif args.concat:
        m, files, measures = process_concat(args.concat, debug=args.debug)
        if not m:
            sys.exit(1)
        print(f"Processed {files} files, getting {measures} measures")
        if args.output:
            xml_path = Path(args.output).with_suffix('.musicxml')
        else:
            xml_path = Path(os.path.basename(__file__)).with_suffix('.musicxml')
        m.write(xml_path)
        print(f"Result is in {os.path.abspath(xml_path)}")
    else:
        raise ValueError(f"{args.concat} is not a valid file or directory")


if __name__ == "__main__":
    main()
