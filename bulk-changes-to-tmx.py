###########################################################################################################
###########################################################################################################
### Adjust these variables to your situation:

## If you want to remove changed segments, instead of adding changed so the memory, set to "True".
# If set to "False", the changed segments will simply be added to the existing memory.

remove_old_segments = False

## The target language "tuv" element has got a few attributes, which you may or may not want to alter.
# Set to "True" (WITHOUT quotation marks) if you want to update these two attributes to "now":

change_creationdate = False
change_changedate = True

# Set to "'John Doe'" (WITH quotation marks) if you want to change these attributes to "John Doe",
# or set to "False" (WITHOUT quotation marks) if you want the attributes unchanged:

change_creationid = False
change_changeid = False

## Remember that every line changes the string, so if you want to change "strawberry" to "apple",
# and "strawberries" to "apples", changing the first before the second is a bad idea.
# The last element of each list is "True", if it is for a target languague.

regex_substrings_to_change = [
    ["en-GB", r"\bC\b", "D", False],
    ["nl-NL", r"\bC\b", "D", True],
    ["en-GB", r"strawberries", "apples", False],
    ["nl-NL", r"aardbeien", "appels", True],
    ["en-GB", r"strawberry", "apple", False],
    ["nl-NL", r"aardbei", "appel", True] # Don't forget to add a comma if you have more elements!
]

###########################################################################################################
###########################################################################################################


import xml.etree.ElementTree as ET
import os
import re
import copy
from datetime import datetime


def select_files():
    os.chdir("input")
    for file in os.listdir():
        if file.endswith(".tmx"):
            inspect_segments(file)
        else:
            print('"{}" is not a .tmx file; it will be ignored.'.format(file))


def inspect_segments(input_file):
    tree = ET.parse(input_file)
    body = tree.getroot()[1]
    tree.getroot().attrib["version"] = "1.4"
    alternative_translations_comment_inserted = False
    position = 0
    to_insert_copies_of_tu = []
    for tu in body:
        position = position + 1
        copy_of_tu = copy.deepcopy(tu)
        retain_copy_of_tu = False
        this_is_an_alternative_translation = False
        for x in range (tu.__len__()):
            if (tu[x].tag == "prop"):
                this_is_an_alternative_translation = True
                if (not alternative_translations_comment_inserted):
                    alternative_translations_comment = ET.Comment("Alternative translations") ## Sadly, these comments are not at the root level, but I couldn't figure out how to do that.
                    body.insert(position - 1, alternative_translations_comment)
                    alternative_translations_comment_inserted = True
            if (tu[x].tag == "tuv"):
                for y in range (tu[x].__len__()):
                    if (tu[x][y].tag == "seg"):
                        retain_copy_of_tu = bulk_change_segments(tu[x].attrib["lang"], tu[x][y].text, copy_of_tu, x, y, retain_copy_of_tu)

        if retain_copy_of_tu:
            if (this_is_an_alternative_translation):
                body.append(copy_of_tu)
            else:
                to_insert_copies_of_tu.append(copy_of_tu)
        
            if remove_old_segments:
                body.remove(tu)
    
    for to_insert_copy_of_tu in to_insert_copies_of_tu:
        body.insert(0, to_insert_copy_of_tu)
    
    default_translations_comment = ET.Comment("Default translations") ## Sadly, these comments are not at the root level, but I couldn't figure out how to do that.
    body.insert(0, default_translations_comment)

    os.chdir("../output")
    with open(input_file, 'wb') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE tmx SYSTEM "tmx14.dtd">'.encode('utf8'))
        tree.write(f, 'utf-8')
    
    print('Bulk changes in file "{}" have been done.'.format(input_file))
    os.chdir("../input")


def bulk_change_segments(language, segment_text, copy_of_tu, x, y, retain_copy_of_tu):
    new_segment_text = segment_text
    changes_made_now = False
    for to_check_substring in regex_substrings_to_change:
        if (language == to_check_substring[0] and (re.search(to_check_substring[1], segment_text) != None)):
            retain_copy_of_tu = True
            changes_made_now = True
            new_segment_text = re.sub(to_check_substring[1], to_check_substring[2], new_segment_text)

    if (changes_made_now):
        copy_of_tu[x][y].text = new_segment_text
        if (to_check_substring[3]):
            if (change_creationdate):
                now = datetime.now()
                nowstring = now.strftime('%Y%m%dT%H%M%SZ')
                copy_of_tu[x].set('creationdate', nowstring)
            if (change_changedate):
                now = datetime.now()
                nowstring = now.strftime('%Y%m%dT%H%M%SZ')
                copy_of_tu[x].set('changedate', nowstring)
            if (change_creationid):
                copy_of_tu[x].set('creationid', change_creationid)
            if (change_changeid):
                copy_of_tu[x].set('creationid', change_changeid)

    if (retain_copy_of_tu):        
        return True
    else:
        return False

    
if __name__ == "__main__":
    select_files()