# bulk-changes-to-tmx
This is a simple code to make bulk changes to a .tmx translation memory.

## Used tactic
The code goes through the xml-based .tmx file, and inspects all `<tuv>` elements. It checks them against regex substrings put in by the user in the proper variable, with a distinction between source and target language elements. The code also offers the option to edit some of the attributes of `<tuv>` elements for a target language.

## Requirements
### Python virtual environment
A "virtual environment" is recommended; I trust everyone's capabilities of finding out how that works. I don't think any dependencies need to be installed, but if some do, again: the answer is somewhere out there, on the internet.

### Regex
The detection is done based on regex substrings. Again, the internet can tell you all about it.

## Input files
Only files with the extension .txm will be handled. Obviously, the files need to be put in the directory `input`.

I wrote the script based on a .tmx file made by OmegaT with a syntax similar to this:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header creationtool="OmegaT" o-tmf="OmegaT TMX" adminlang="EN-US" datatype="plaintext" creationtoolversion="6.0.1_0_42ef0143" segtype="sentence" srclang="en-GB"/>
  <body>
<!-- Default translations -->
    <tu>
      <tuv xml:lang="en-GB">
        <seg>Hello World!</seg>
      </tuv>
      <tuv xml:lang="nl-NL" changeid="John Doe" changedate="20210117T112458Z" creationid="John Doe" creationdate="20210117T112458Z">
        <seg>Dag wereld!</seg>
      </tuv>
    </tu>
<!-- Alternative translations -->
    <tu>
      <prop type="file">Some_text.docx</prop>
      <prop type="prev">Hello World!</prop>
      <prop type="next">Bye!</prop>
      <tuv xml:lang="en-GB">
        <seg>Sun is shining! Let the vitamine C come to me!</seg>
      </tuv>
      <tuv xml:lang="nl-NL" changeid="Erik DB" changedate="20220306T093912Z" creationid="Erik DB" creationdate="20220306T093912Z">
        <seg>De zon schijnt! Laat die vitamine D maar komen!</seg>
      </tuv>
    </tu>
  </body>
</tmx>
```

If your file has a different structure, the code will most likely need to be altered.

## Output files
I wasn't able to get the two comments (`<!-- Default translations -->`) and (`<!-- Alternative translations -->`) on exactly the same spot, they're part of the `<body>` element in the output file. I don't think that matters, since they're just comments. But I mention it for full disclosure. (And if anyone has a solution for it, please let me know.)

Obviously, the files will appear in the directory `output`.

## Variables
### remove_old_segments
If you want to **replace** segments, make sure `remove_old_segments` is `True`. If it is `False`, the new segments will simply be added to the existing memory.

### change_...
The target language `<tuv>` tags have some attributes, which you may or may not want to alter:
```python
# Set to "True" (WITHOUT quotation marks) if you want to update these two attributes to "now":

change_creationdate = False
change_changedate = True

# Set to "'John Doe'" (WITH quotation marks) if you want to change these attributes to "John Doe",
# or set to "False" (WITHOUT quotation marks) if you want the attributes unchanged:

change_creationid = False
change_changeid = False
```

### regex_substrings_to_change
This list should contain more lists, where the first element is the language of the `tuv` tag, the second element the regex substring that will be searched, the third element is the substring that will replace the substring that was found (i.e. the second element), the last element is "True" if if is for a source language (in which case attributes can be changed).

Remember that every line changes the string, so if you want to change "strawberry" to "apple", and "strawberries" to "apples", changing the first before the second will get you results like `strawberrys`.

Reading up on regex is a good idea, so you know how to filter out instances where C is not part of a word.

If you want to change `C` to `D` in the segments in the languages `en-GB` and `nl-NL`, and the above examples of strawberries and apples this is what the list should look like:
```python
regex_substrings_to_change = [
    ["en-GB", r"\bC\b", "D", False],
    ["nl-NL", r"\bC\b", "D", True],
    ["en-GB", r"strawberries", "apples", False],
    ["nl-NL", r"aardbeien", "appels", True],
    ["en-GB", r"strawberry", "apple", False],
    ["nl-NL", r"aardbei", "appel", True] # Don't forget to add a comma if you have more elements!
]
```