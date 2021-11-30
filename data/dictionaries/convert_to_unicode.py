from pathlib import Path
import re

import pyewts

converter = pyewts.pyewts()
text = "srog gi yi ge (dbyangs bzhi/) rkyen gyi yi ge (dbu shad gnyis/) pha ma bu tsha'i yi ge'i ma ni (a dang )pa ni (a bor ba'i lhag ma nyer dgu dang/) b"
conv = converter.toUnicode(text)
print('')

converted_path = Path('converted')
source_path = Path('raw/public')

do_not_convert = [
    '03-Berzin',
    '04-Berzin-Def',
    '05-Hopkins-Def2015',
    '11-Hopkins-Divisions2015',
    '13-Hopkins-Examples',
    '15-Hopkins-Skt1992',
    '16-Hopkins-Synonyms1992',  # has Tibetan and English, but nothing to mark start/end of Tibetan
    "20-Hopkins-others'English2015",
    '21-Mahavyutpatti-Skt',
    '22-Yoghacharabhumi-glossary',
    '23-GatewayToKnowledge',
    '36-ComputerTerms',
    '38-Gaeng,Wetzel',
    '40-CommonTerms-Lin',
    '43-84000Dict',
    '46-84000Skt',
    '49-LokeshChandraSkt',
]

do_convert = [
    '12-Hopkins-Divisions,Tib2015',
    '14-Hopkins-Examples,Tib',
    '17-Hopkins-TibetanSynonyms1992',
    '17-Hopkins-TibetanSynonyms2015',
    '18-Hopkins-TibetanDefinitions2015',
    '19-Hopkins-TibetanTenses2015',
    '25-tshig-mdzod-chen-mo-Tib',
    '34-dung-dkar-tshig-mdzod-chen-mo-Tib',
    '37-dag_tshig_gsar_bsgrigs-Tib',
]

log = {}
for f in sorted(source_path.glob('*')):
    print(f.name)
    dump = f.read_text()

    # convert Wylie to Unicode
    out = []
    for n, line in enumerate(dump.splitlines()):
        if line.startswith('#') or not line.strip():  # passing comment lines and empty lines
            continue

        # Converting the lemma
        try:
            lemma, defnt = line.split('|')
        except ValueError:
            if not f.name in log:
                log[f.name] = {}
            if n not in log[f.name]:
                log[f.name][n] = line
            continue

        lemma = converter.toUnicode(lemma)

        # Converting the entries
        defnt = defnt.replace('/ ', '/_')
        defnt = re.sub(r'/([^ _])', r'/_\1', defnt)
        conv_def = ''
        # do not convert anything, even what is between { and }
        if f.stem in do_not_convert:
            pass

        # convert everything, instead of just the parts between { and }
        elif f.stem in do_convert:
            conv_def = converter.toUnicode(defnt)

        # otherwise, convert in Unicode only the chars that are between { and } in the definitions
        else:
            words = re.findall(r'{(.+?)}', defnt)
            words = [converter.toUnicode(w) for w in words]
            if '{' in defnt and not words:
                if not f.name in log:
                    log[f.name] = {}
                if n not in log[f.name]:
                    log[f.name][n] = line
                continue

            parts = re.split(r'({.+?})', defnt)
            for p in parts:
                if p.startswith('{'):
                    conv_def += words.pop()
                else:
                    conv_def += p

        if not conv_def:
            conv_def = defnt
        out.append(f'{lemma}|{conv_def}')
    out = '\n'.join(out)

    out_file = converted_path / (f.name + '.txt')
    out_file.write_text(out)

log_text = ''
for f, entries in log.items():
    log_text += f'{f}\n'
    for num, line in entries.items():
        log_text += f'\t{num}:\t\t{line}\n'
Path('log.txt').write_text(log_text)
