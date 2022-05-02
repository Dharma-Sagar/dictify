from pathlib import Path
import re


def split_in_senses(entry, lang, file, lnum):
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
                print(lnum, file, entry[:100])

        elif re.findall(tsikchen_dagsar, entry):
            parts = [e for e in re.split(tsikchen_dagsar_start, entry) if e]
            if not re.findall(r'^[༡༢༣༤༥༦༧༨༩༠]', parts[0]):
                parts = [f'{parts[0]} {parts[1]}'] + parts[2:]
            try:
                parts = [f'{parts[n]}{parts[n + 1]}' for n in range(0, len(parts), 2)]
            except IndexError:
                print(lnum, file, entry[:100])

        elif re.findall(tsikchen, entry):
            parts = [e for e in re.split(tsikchen_start, entry) if e]
            if parts[0].startswith('༼'):
                parts = [f'{parts[0]} {parts[1]}'] + parts[2:]
            try:
                parts = [f'{parts[n]} {parts[n + 1]}' for n in range(0, len(parts), 2)]
                print()
            except IndexError as e:
                print(lnum, file, entry[:100])
        else:
            return entry
    elif lang == 'en' and re.findall(ry_start, entry):
        parts = [e for e in re.split(ry, entry) if e]
        try:
            parts = [f'{parts[n]} {parts[n+1]}' for n in range(0, len(parts), 2)]
        except IndexError:
            print(lnum, file, entry[:100])


to_check = {
    'bo': [
        Path('monlam_2020_1.txt'),
        Path('monlam_2020_2.txt'),
        Path('monlam_2020_3.txt')
    ]
            }
for lang, dicts in to_check.items():
    for d in dicts:
        dump = d.read_text()
        dump = re.sub(r'( [0-9]+\.)([^ ])', r'\1 \2', dump)
        dump = dump.replace(' ', ' ')
        dump = re.sub(r' +', ' ', dump)
        d.write_text(dump)

        for n, line in enumerate(dump.strip().split('\n')):
            lemma, entry = line.split('|', maxsplit=1)
            split_in_senses(entry, lang, d.name, n+1)
