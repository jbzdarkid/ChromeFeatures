from collections import defaultdict
from pathlib import Path
from subprocess import run

# run(['git', 'clone', '--depth=1', 'https://github.com/chromium/chromium'])

files = defaultdict()

matches = run(['git', 'grep', '-rnF', 'BASE_FEATURE'], capture_output=True, text=True, cwd='chromium/chrome/browser/ui').stdout.split('\n')
for match in matches:
  if match == '':
    continue
  file, line, _ = match.split(':', 2)
  files[file].add(int(line))

for file, lines in files.items():
  with Path(file).open('utf-8') as f:
    for i, line in enumerate(f):







