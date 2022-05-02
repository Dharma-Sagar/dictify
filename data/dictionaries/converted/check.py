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


to_check = {'en': [
    Path('38-Gaeng,Wetzel.txt'),
    Path('23-GatewayToKnowledge.txt'),
    Path('01-Hopkins2015.txt'),
    Path('05-Hopkins-Def2015.txt'),
    Path('03-Berzin.txt'),
    Path('04-Berzin-Def.txt'),
    Path('40-CommonTerms-Lin.txt'),
    Path('10-RichardBarron.txt'),
    Path('05-Hackett-Def2015.txt'),
    Path('08-IvesWaldo.txt'),
    Path('09-DanMartin.txt'),
    Path('35-ThomasDoctor.txt'),
    Path("20-Hopkins-others'English2015.txt"),
    Path('06-Hopkins-Comment.txt'),
    Path('02-RangjungYeshe.txt'),
    Path('33-TsepakRigdzin.txt'),
    Path('47-Misc.txt'),
    Path('07-JimValby.txt'),
    Path('36-ComputerTerms.txt'),
    Path('43-84000Dict.txt'),
    Path('44-84000Definitions.txt')
],
    'bo': [
        Path('25-tshig-mdzod-chen-mo-Tib.txt'),
        Path('37-dag_tshig_gsar_bsgrigs-Tib.txt'),
        Path('34-dung-dkar-tshig-mdzod-chen-mo-Tib.txt'),
        Path('48-TibTermProject.txt')
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
