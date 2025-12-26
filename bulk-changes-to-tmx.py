###########################################################################################################
###########################################################################################################
# Default parameters
# Adjust these parameters to your situation:

# Set to True if you want to leave the original segments instead of just replacing them in the memory.
# If set to "False", the changed segments will simply replace the original ones.

from lxml import etree as ET
from pathlib import Path
from datetime import datetime
import sys
import re
import copy
keep_original_segments = False

# The "<tuv>" element may have some attributes you may want to update.
# Set the following variables to "True" (WITHOUT quotation marks) if you want to update these two attributes to the current date and time:

change_creationdate = False
change_changedate = True

# Enter the ID you want to use in the quotes if you want to change the attribute.
# The changeid attribute is changed to "Bulk Changer" by default.

new_creationid = ""
new_changeid = "Bulk Changer"

# Add a "(search pattern, replacement pattern)" tuple to the list for each language.
# The original segments in the corresponding language are each matched to each search pattern
# individually before making any replacements, so later entries in the list will not overwrite
# earlier ones. For example, changing "tea" to "coffee", and then later changing "coffee" to
# "Red Bull" will not go back and change "coffee" in segments that originally contained "tea".

replace_patterns = {
    "en-CA": [(r"\btea\b", "coffee"), (r"'", "ʼ"), ("\bcoffee\b", "Red Bull")],
    "fr-CA": [(r"\bthé\b", "café"), (r"'", "ʼ"), ("\bcafé\b", "Red Bull")],
}

# Add new "(search pattern, replacement pattern)" tuples to the list for the approriate languages
# if you want to make more changes.

###########################################################################################################
###########################################################################################################


def get_tmx_files():
    input_path = Path.cwd() / "input"
    tmx_to_process = list(input_path.glob("*.tmx"))

    return tmx_to_process


def parse_tmx(input_file):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(input_file, parser)

    return tree


def retain_original_tus(tus):
    for tu in target_tus:
        original_tu = copy.deepcopy(tu)
        tu.addprevious(original_tu)


def inspect_segments(tmx):

    lang_attribute = (
        ET.QName("http://www.w3.org/XML/1998/namespace", "lang")
        if tmx.getroot().attrib.get("version") in ["1.3", "1.4"]
        else "lang"
    )

    segments = tmx.xpath("//seg")
    segment_updates = []

    for segment in segments:
        segment_language = segment.getparent().attrib.get(lang_attribute)

        if (segment_language in replace_patterns):
            for pattern in replace_patterns[segment_language]:
                if re.search(pattern[0], segment.text):
                    segment_updates.append((segment, (pattern[0], pattern[1])))

    return segment_updates


def modify_segments(updates):
    modifiable_attributes = ["creationdate", "changedate", "creationid", "changeid"]

    for update in updates:
        segment, patterns = update
        tuv = segment.getparent()
        attributes = [a for a in tuv.keys() if a in modifiable_attributes]

        segment.text = re.sub(patterns[0], patterns[1], segment.text)

        if attributes:
            new_datetime = datetime.now().strftime("%Y%m%dT%H%M%SZ")

            if change_creationdate:
                tuv.attrib["creationdate"] = new_datetime

            if change_changedate:
                tuv.attrib["changedate"] = new_datetime

            if new_creationid:
                tuv.attrib["creationid"] = new_creationid

            if new_changeid:
                tuv.attrib["changeid"] = new_changeid


def write_output_tmx(tmx_file, output_tree):
    output_file = Path(f"./output/changed_{tmx_file.name}")
    output_tree.write(output_file, encoding="utf-8", xml_declaration=True, pretty_print=True)


if __name__ == "__main__":
    # Retrieve TMX files from the input folder
    tmx_files = get_tmx_files()
    if tmx_files:
        # Process each TMX file
        for tmx_file in tmx_files:
            current_tmx = parse_tmx(tmx_file)

            # Process the segments in the TMX file
            segments_to_change = inspect_segments(current_tmx)
            target_tus = {seg[0].getparent().getparent() for seg in segments_to_change}

            # Retain original tus if specified
            if keep_original_segments:
                retain_original_tus(target_tus)

            # Apply changes to segments
            modify_segments(segments_to_change)

            # Write output TMX file to output directory
            write_output_tmx(tmx_file, current_tmx)

            # Inform user that the changes have been made
            print(f"Bulk changes have been applied to {tmx_file.name}.")

    else:
        print("No TMX files found in the 'input' folder.")
        sys.exit()
