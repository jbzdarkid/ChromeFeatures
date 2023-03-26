from collections import defaultdict
from pathlib import Path
from subprocess import run

if not Path('chromium').exists():
  run(['git', 'clone', '--depth=1', 'https://github.com/chromium/chromium'])

files = defaultdict(set)

feature_folder = 'chromium/chrome/browser/ui'
matches = run(['git', 'grep', '-rnF', 'BASE_FEATURE'], capture_output=True, text=True, cwd=feature_folder).stdout.split('\n')
for match in matches:
  if not match:
    continue
  file, line, _ = match.split(':', 2)
  if 'test' not in file:
    files[f'{feature_folder}/{file}'].add(int(line)-1)

features_bad = [] # Need to do formatting inline, but lazy rn

comment_buffer = []
feature_buffer = ''

for file, lines in files.items():
  with Path(file).open('r', encoding='utf-8') as f:
    for i, orig_line in enumerate(f):
      line = orig_line.strip()

      if line.startswith('//'):
        comment_buffer.append(line)
      elif i in lines or len(feature_buffer) > 0:
        feature_buffer += line
        if ';' in line:
          features_bad.append({
            'comment': '\n'.join(comment_buffer),
            'feature': feature_buffer,
            'file': str(file),
          })

          # Convert the feature buffer
          if '#' not in line: # TODO, deal with #if, #else, etc
            # kChromeLabs, "ChromeLabs", base::FEATURE_DISABLED_BY_DEFAULT
            _, feature_name, state = feature_buffer.split(',')
            features_bad[-1]['name'] = feature_name.strip(' "')
            features_bad[-1]['default'] = 'FEATURE_ENABLED_BY_DEFAULT' in state

          comment_buffer = []
          feature_buffer = ''
          if len(features_bad) > 10:
            break
      else:
        comment_buffer = []


for f in features_bad:
  print(f['file'])
  print(f['comment'])
  print(f['feature'])
  if 'name' in f:
    print('"' + f['name'] + '"', f['default'])
  print('-'*20)



