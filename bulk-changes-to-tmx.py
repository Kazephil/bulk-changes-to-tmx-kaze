###########################################################################################################
###########################################################################################################
### Default parameters
### Adjust these parameters to your situation:

## Set to True if you want to leave the original segments instead of just replacing them in the memory.
# If set to "False", the changed segments will simply replace the original ones.

keep_original_segments = False

## The target language "tuv" element has got a few attributes, which you may or may not want to alter.
# Set to "True" (WITHOUT quotation marks) if you want to update these two attributes to "now":

change_creationdate = False
change_changedate = True

# Enter the ID you want to use in the quotes if you want to change the attribute.
# In this example, the changeid attribute is changed to "Bulk Changer" by default.

new_creationid = ""
new_changeid = "Bulk Changer"

## Add a "(search pattern, replacement pattern)" tuple to the list for each language.
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


import copy
import re
import sys

from datetime import datetime
from pathlib import Path
from lxml import etree as ET


def get_tmx_files():
    input_path = Path.cwd() / "input"
    tmx_to_process = list(input_path.glob("*.tmx"))

    return tmx_to_process


def parse_tmx(input_file):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(input_file, parser)

    return tree


def inspect_segments(tmx_tree):
    body = tmx_tree.getroot()[1]
    version = tmx_tree.getroot().attrib.get("version")
    lang = XMLLANG if version == "1.4" else "lang"

    default_translations_comment = body.xpath('//comment()')[0]
    alternative_translations_comment = body.xpath('//comment()')[1]

    # alternative_translations_comment_inserted = False
    # position = 0
    to_insert_copies_of_tu = []
    for tu in body.findall("tu"):
        # position = position + 1
        copy_of_tu = copy.deepcopy(tu)
        retain_copy_of_tu = False
        this_is_an_alternative_translation = False
        for x in range(tu.__len__()):
            if tu[x].tag == "prop":
                this_is_an_alternative_translation = True
                if not alternative_translations_comment_inserted:
                    alternative_translations_comment = ET.Comment(
                        "Alternative translations"
                    )  ## Sadly, these comments are not at the root level, but I couldn't figure out how to do that.
                    body.insert(position - 1, alternative_translations_comment)
                    alternative_translations_comment_inserted = True
            if tu[x].tag == "tuv":
                for y in range(tu[x].__len__()):
                    if tu[x][y].tag == "seg":
                        retain_copy_of_tu = bulk_change_segments(
                            tu[x].attrib[lang],
                            tu[x][y].text,
                            copy_of_tu,
                            x,
                            y,
                            retain_copy_of_tu,
                        )

        if retain_copy_of_tu:
            if this_is_an_alternative_translation:
                body.append(copy_of_tu)
            else:
                to_insert_copies_of_tu.append(copy_of_tu)

            if remove_old_segments:
                body.remove(tu)

    for to_insert_copy_of_tu in to_insert_copies_of_tu:
        body.insert(0, to_insert_copy_of_tu)

    default_translations_comment = ET.Comment(
        "Default translations"
    )  ## Sadly, these comments are not at the root level, but I couldn't figure out how to do that.
    body.insert(0, default_translations_comment)


def bulk_change_segments(language, segment_text, copy_of_tu, x, y, retain_copy_of_tu):
    new_segment_text = segment_text
    changes_made_now = False
    for to_check_substring in regex_substrings_to_change:
        if language == to_check_substring[0] and (re.search(to_check_substring[1], segment_text) != None):
            retain_copy_of_tu = True
            changes_made_now = True
            new_segment_text = re.sub(to_check_substring[1], to_check_substring[2], new_segment_text)

    if changes_made_now:
        copy_of_tu[x][y].text = new_segment_text
        if to_check_substring[3]:
            if change_creationdate:
                now = datetime.now()
                nowstring = now.strftime("%Y%m%dT%H%M%SZ")
                copy_of_tu[x].set("creationdate", nowstring)
            if change_changedate:
                now = datetime.now()
                nowstring = now.strftime("%Y%m%dT%H%M%SZ")
                copy_of_tu[x].set("changedate", nowstring)
            if change_creationid:
                copy_of_tu[x].set("creationid", change_creationid)
            if change_changeid:
                copy_of_tu[x].set("creationid", change_changeid)

    if retain_copy_of_tu:
        return True
    else:
        return False


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
            inspect_segments(current_tmx)

            # Prepare final output TMX document
            doctype = current_tmx.docinfo.doctype

            # Write output TMX file to output directory
            write_output_tmx(tmx_file, current_tmx)

            # Inform user that the changes have been made
            print(f"Bulk changes have been applied to {tmx_file.name}.")

    else:
        print("No TMX files found in the 'input' folder.")
        sys.exit()
