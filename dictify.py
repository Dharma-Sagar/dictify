from collections import defaultdict
from pathlib import Path
import re

import yaml
import json

from botok import Text
import pyewts

from googletrans import Translator

conv = pyewts.pyewts()



def dictify_text(string, is_split=False, selection_yaml='data/dictionaries/dict_cats.yaml', expandable=True, mode='en'):
    """
    takes segmented text and finds entries from dictionaries
    :param expandable: will segment definitions into senses if True, not if False
    :param selection_yaml: add None or "" to prevent selection
    :param string: segmented text to be processed
    :return: list of tuples containing the word and a dict containing the definitions(selected or not) and an url
    """
    words = []
    if is_split:
        for w in string:
            if w:
                words.append((w, {}))
    else:
        string = string.replace('\n', ' ')
        for w in string.split(' '):
            if w:
                words.append((w, {}))

    dicts = load_dicts()
    for num, word in enumerate(words):
        lemma = word[0].rstrip('་')
        defs = dicts[lemma]
        # filter
        if selection_yaml:
            defs = select_defs(defs, yaml_path=selection_yaml, mode=mode)

        # split in senses
        if expandable:
            if defs and 'en' in defs:
                entry_en = defs['en'][1]
                defs['en'][1] = split_in_senses(entry_en, lang='en')

            if defs and 'bo' in defs:
                entry_bo = defs['bo'][1]
                defs['bo'][1] = split_in_senses(entry_bo, lang='bo')

        words[num][1][''] = defs
        # url
        url = gen_link(lemma)
        #words[num][1]['url'] = url

    return words


def load_dicts():
    dicts = defaultdict(dict)
    dict_path = Path(__file__).parent / 'data/dictionaries/converted'
    dict_other = Path(__file__).parent / 'data/dictionaries/other'
    dict_files = sorted(list(dict_path.glob('*.txt')) + list(dict_other.glob('*.txt')))
    #for f in dict_files:
    f=dict_files[1]
    name = f.stem
    if name.startswith('monlam'):
        name = name[:-2]  # remove file number suffix "_1", "_2" and "_3"
    lines = f.read_text().split('\n')
    for line in lines:
        if '|' not in line:
            continue

        lemma, entry = line.split('|')
        dicts[lemma][name] = f'{dicts[lemma][name]} {entry}' if name in dicts[lemma] else entry

    return dicts


def split_in_senses(entry, lang):
    header_size = 10  # syllables
    tsikchen_dagsar = r' ([༡༢༣༤༥༦༧༨༩༠]+\.)'
    tsikchen_dagsar_start = r'(?: |^)([༡༢༣༤༥༦༧༨༩༠]+\.)'
    tsikchen = r' ([༡༢༣༤༥༦༧༨༩༠]+༽) '
    tsikchen_start = r'(?: |^)([༡༢༣༤༥༦༧༨༩༠]+༽) '
    monlam = r' ((?:[^་]+་[^་]+ )?[0-9]+\.) '
    ry_start = r'^([0-9]+\)) '  # line must start with this pattern
    ry = r'(?: |^)([0-9]+\)) '

    senses = []
    if lang == 'bo':
        if re.findall(monlam, entry):
            parts = [e for e in re.split(monlam, entry) if e]
            try:
                parts = [f'{parts[n]} {parts[n + 1]}' for n in range(0, len(parts), 2)]
            except IndexError as e:
                print(entry[:100])
                raise SyntaxError(e)
            for p in parts:
                t = Text(p).tokenize_chunks_plaintext.split(' ')
                if len(t) > header_size:
                    header, body = ''.join(t[:header_size]).replace('_', ' '), ''.join(t[header_size:]).replace('_', ' ')
                    senses.append((header, body))
                else:
                    senses.append(p)
        elif re.findall(tsikchen_dagsar, entry):
            parts = [e for e in re.split(tsikchen_dagsar_start, entry) if e]
            if not re.findall(r'^[༡༢༣༤༥༦༧༨༩༠]', parts[0]):
                parts = [f'{parts[0]} {parts[1]}'] + parts[2:]
            try:
                parts = [f'{parts[n]}{parts[n + 1]}' for n in range(0, len(parts), 2)]
            except IndexError as e:
                print(entry[:100])
                raise SyntaxError(e)
            for p in parts:
                t = Text(p).tokenize_chunks_plaintext.split(' ')
                if len(t) > header_size:
                    header, body = ''.join(t[:header_size]).replace('_', ' '), ''.join(t[header_size:]).replace('_', ' ')
                    senses.append((header, body))
                else:
                    senses.append(p)
        elif re.findall(tsikchen, entry):
            parts = [e for e in re.split(tsikchen_start, entry) if e]
            if parts[0].startswith('༼'):
                parts = [f'{parts[0]} {parts[1]}'] + parts[2:]
            try:
                parts = [f'{parts[n]} {parts[n + 1]}' for n in range(0, len(parts), 2)]
            except IndexError as e:
                print(entry[:100])
                raise SyntaxError(e)
            for p in parts:
                t = Text(p).tokenize_chunks_plaintext.split(' ')
                if len(t) > header_size:
                    header, body = ''.join(t[:header_size]).replace('_', ' '), ''.join(t[header_size:]).replace('_', ' ')
                    senses.append((header, body))
                else:
                    senses.append(p)
        else:
            return entry
    elif lang == 'en' and re.findall(ry_start, entry):
        parts = [e for e in re.split(ry, entry) if e]
        parts = [f'{parts[n]} {parts[n+1]}' for n in range(0, len(parts), 2)]
        for p in parts:
            t = p.split(' ')
            size = header_size - 4 if header_size - 4 > 0 else 0
            if len(t) > size:
                header, body = ' '.join(t[:size]).replace('_', ' '), ' '.join(t[size:]).replace('_', ' ')
                senses.append((header, body))
            else:
                senses.append(p)
    else:
        return entry

    return senses




def select_defs(defs, yaml_path, mode):
    cats = yaml.safe_load(Path(yaml_path).read_text())
    english, tibetan = cats['english']['dictionary'], cats['tibetan']['dictionary']

    selected = {}
    # selecting the first English definition from the list in dict_cats.yaml
    if 'en' in mode:
        for full, name in english:
            if full in defs:
                selected['en'] = (name, defs[full])
                break

    # selecting the first Tibetan definition from the list in dict_cats.yaml
    if 'bo' in mode:
        for full, name in tibetan:
            if full in defs:
                selected['bo'] = (name, defs[full])
                break

    # format selected
    if 'en' in selected and 'bo' in selected:
        return {'en': [selected['en'][0], selected['en'][1]], 'bo': [selected['bo'][0], selected['bo'][1]]}
    elif 'en' in selected:
        return {selected['en'][1]}
    elif 'bo' in selected:
        return {'bo': [selected['bo'][0], selected['bo'][1]]}
    else:
        return None


def gen_link(word):
    link_pattern = 'https://dictionary.christian-steinert.de/#%7B%22activeTerm%22%3A%22{word}%22%2C%22' \
                   'lang%22%3A%22tib%22%2C%22inputLang%22%3A%22tib%22%2C%22currentListTerm%22%3A%22{word}%22%2C%22' \
                   'forceLeftSideVisible%22%3Atrue%2C%22offset%22%3A0%7D'
    wylie = conv.toWylie(word).replace(' ', '%20')
    return link_pattern.format(word=wylie)


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def translate_text(text, target_language):
    if text != 'None':
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text


def write_tuple_to_file(file_path, my_tuple):
    try:
        with open(file_path, 'w') as file:
            file.write("#\n")
            file.write("msgid \"\"\n")
            file.write("msgstr \"\"\n")
            file.write("\"MIME-Version: 1.0\\n\"\n")
            file.write("\"Content-Type: text/plain; charset=utf-8\\n\"\n")
            file.write("\"Content-Transfer-Encoding: 8bit\\n\"\n"+'\n' )
            for item in my_tuple:
                file.write('# '+str(item[0] ) + '\n')
                clean = str(item[1]).replace("[", "").replace("{", "").replace("}", "").replace(":","").replace("''","")
                file.write('msgid '+clean + '\n')
                file.write(translate_text(clean,"es")+'\n')
                file.write('\n')
    except IOError:
        print("Error: Unable to write to the file.")

if __name__ == '__main__':
    for f in Path('input').glob('*.txt'):
        dump = f.read_text(encoding='utf-8')
        out = dictify_text(dump, expandable=True)


        out_f = Path('output') / f.name

        write_tuple_to_file(out_f,out)
        print(out[1])
        #out_f.write_text(json.dumps(out, ensure_ascii=False, indent=4))



        #out_f.write_text(json.dumps(out, ensure_ascii=False,default=set_default,indent=2,separators=(',', ':')))

__all__ = [dictify_text]
