from pathlib import Path
import os
from tempfile import TemporaryDirectory

repo_link = 'https://github.com/christiansteinert/tibetan-dictionary.git'
with TemporaryDirectory() as tmpdir:
    os.system(f'git clone {repo_link} {tmpdir}')
    public = Path(tmpdir) / '_input' / 'dictionaries' / 'public'
    public_en = Path(tmpdir) / '_input' / 'dictionaries' / 'public_en'
    for orig_dir, target_dir in [(public, Path('raw/public')), (public_en, Path('raw/public_en'))]:
        if not target_dir.parent.is_dir():
            target_dir.parent.mkdir(exist_ok=True)

        os.system(f'cp -R {orig_dir} {target_dir}')
