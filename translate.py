
from pathlib import Path

import os

from googletrans import Translator

import re

def postprocess_str(text):
    clean = text.replace("{'': {", '').replace("}}","").replace("{'':","'").replace("None}","None'")
    clean = re.sub(r'(?<!^)"(?!$)', r'\\"', clean)
    clean = re.sub(r"(?<!^)'(?!$)", r"\\'", clean)
    return clean

def translate_text(text, target_language):

    if text is not None:
        retry =0
        while (retry <= 3):
            translator = Translator()
            try:
                translation = translator.translate(text, dest=target_language)
                return translation.text
            except Exception as e:
                print(f"Exception occurred: {type(e).__name__}")
                print(text)
                #time.sleep(1)
                retry +=1


    return "None"
def translate_file(input_file_path, output_file_path,language):

        with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
            output_file.write("#\n")
            output_file.write("msgid \"\"\n")
            output_file.write("msgstr \"\"\n")
            output_file.write("\"MIME-Version: 1.0\\n\"\n")
            output_file.write("\"Content-Type: text/plain; charset=utf-8\\n\"\n")
            output_file.write("\"Content-Transfer-Encoding: 8bit\\n\"\n"+'\n' )

            nonecount=1
            for line in input_file:
                line = line.strip()  # Remove leading/trailing whitespace

                if line.startswith("#"):
                    output_file.write(line + '\n')
                elif ' None' in line:
                    output_file.write('msgid ' + line + '\n')
                    output_file.write('msgstr None ' + str(nonecount) + '\n')
                    nonecount += 1
                elif line.strip() == "":
                    output_file.write('\n')
                else:
                    output_file.write('msgid ' + line + '\n')
                    translate = translate_text(line, language)
                    output_file.write('msgstr ' + postprocess_str(translate) + '\n')



if __name__ == '__main__':

    #out_f_es = Path('output') / os.path.normpath("37es.po")
    #out_f_pt = Path('output') / os.path.normpath("37pt.po")

    translate_file("input/definitions.txt","output/37es.po","es")
    translate_file("input/definitions.txt", "output/37pt.po","pt")