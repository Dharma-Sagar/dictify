from collections import defaultdict
from pathlib import Path

import yaml
import json
import pyewts

conv = pyewts.pyewts()


def dictify_text(string, selection_yaml='data/dictionaries/dict_cats.yaml'):
    """
    takes segmented text and finds entries from dictionaries
    :param selection_yaml: add None or "" to prevent selection
    :param string: segmented text to be processed
    :return: list of tuples containing the word and a dict containing the definitions(selected or not) and an url
    """
    string = string.replace('\n', ' ')
    words = []
    for w in string.split(' '):
        if w:
            words.append((w, {}))

    dicts = load_dicts()
    for num, word in enumerate(words):
        lemma = word[0].rstrip('་')
        defs = dicts[lemma]
        # filter
        if selection_yaml:
            defs = select_defs(defs, yaml_path=selection_yaml)
        words[num][1]['defs'] = defs
        # url
        url = gen_link(lemma)
        words[num][1]['url'] = url

    return words


def load_dicts():
    dicts = defaultdict(dict)
    dict_path = Path('data/dictionaries/converted')
    for f in sorted(dict_path.glob('*.txt')):
        name = f.stem
        lines = f.read_text().split('\n')
        for line in lines:
            if '|' not in line:
                continue

            lemma, entry = line.split('|')
            dicts[lemma][name] = entry

    return dicts


def select_defs(defs, yaml_path):
    cats = yaml.safe_load(Path(yaml_path).read_text())
    english, tibetan = cats['english']['dictionary'], cats['tibetan']['dictionary']

    selected = {}
    # selecting the first English definition from the list in dict_cats.yaml
    for full, name in english:
        if full in defs:
            selected['en'] = (name, defs[full])
            break

    # selecting the first Tibetan definition from the list in dict_cats.yaml
    for full, name in tibetan:
        if full in defs:
            selected['bo'] = (name, defs[full])
            break

    # format selected
    if 'en' in selected and 'bo' in selected:
        return {'en': [selected['en'][0],selected['en'][1]], 'bo': [selected['bo'][0], selected['bo'][1]]}
    elif 'en' in selected:
        return {'en': [selected['en'][0], selected['en'][1]]}
    elif 'bo' in selected:
        return {'bo': [selected['bo'][0], selected['bo'][1]]}
    else:
        return None


def gen_link(word):
    link_pattern = 'https://dictionary.christian-steinert.de/#%7B%22activeTerm%22%3A%22{word}%22%2C%22' \
                   'lang%22%3A%22tib%22%2C%22inputLang%22%3A%22tib%22%2C%22currentListTerm%22%3A%22{word}%22%2C%22' \
                   'forceLeftSideVisible%22%3Atrue%2C%22offset%22%3A0%7D'
    wylie = conv.toWylie(word)
    return link_pattern.format(word=wylie)


if __name__ == '__main__':
    for f in Path('input').glob('*.txt'):
        dump = f.read_text(encoding='utf-8')
        out = dictify_text(dump)
        out_f = Path('output') / f.name
        out_f.write_text(json.dumps(out, ensure_ascii=False, indent=4))

__all__ = [dictify_text]
