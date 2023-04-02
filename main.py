from collections import defaultdict
from pathlib import Path
from subprocess import run
import macro

if not Path('chromium').exists():
  run(['git', 'clone', '--depth=1', 'https://github.com/chromium/chromium'])

files = defaultdict(set)

# feature_folder = 'chromium/chrome/browser'
feature_folder = 'chromium/chrome'
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

# See chromium/build/build_config.h
pragma_replacements = {
  'BUILDFLAG(ENABLE_EXTENSIONS)': 'True',
  'BUILDFLAG(ENABLE_PDF)': 'True',
  'BUILDFLAG(ENABLE_PLUGINS)': 'True',
  'BUILDFLAG(GOOGLE_CHROME_BRANDING)': 'True',
  'BUILDFLAG(IS_WIN)': 'True',
  'defined(OFFICIAL_BUILD)': 'True',
  'defined(_WINDOWS_)': 'True',

  'ANDROID_ARM32_UNWINDING_SUPPORTED': 'False',
  'ANDROID_ARM64_UNWINDING_SUPPORTED': 'False',
  'ANDROID_UNWINDING_SUPPORTED': 'False',
  'BUILDFLAG(CAN_UNWIND_WITH_FRAME_POINTERS)': 'False',
  'BUILDFLAG(DFMIFY_DEV_UI)': 'False',
  'BUILDFLAG(ENABLE_ARM_CFI_TABLE)': 'False',
  'BUILDFLAG(ENABLE_CAPTIVE_PORTAL_DETECTION)': 'False',
  'BUILDFLAG(ENABLE_COMPONENT_UPDATER)': 'False',
  'BUILDFLAG(ENABLE_DICE_SUPPORT)': 'False',
  'BUILDFLAG(ENABLE_LENS_DESKTOP_GOOGLE_BRANDED_FEATURES)': 'False',
  'BUILDFLAG(ENABLE_MEDIA_REMOTING)': 'False',
  'BUILDFLAG(ENABLE_NACL)': 'False',
  'BUILDFLAG(ENABLE_OFFLINE_PAGES)': 'False',
  'BUILDFLAG(ENABLE_OOP_PRINTING)': 'False',
  'BUILDFLAG(ENABLE_PPAPI)': 'False',
  'BUILDFLAG(ENABLE_PRINTING)': 'False',
  'BUILDFLAG(ENABLE_SCREEN_AI_SERVICE)': 'False',
  'BUILDFLAG(ENABLE_SUPERVISED_USERS)': 'False',
  'BUILDFLAG(ENABLE_SYSTEM_NOTIFICATIONS)': 'False',
  'BUILDFLAG(ENABLE_UPDATE_NOTIFICATIONS)': 'False',
  'BUILDFLAG(ENABLE_VR)': 'False',
  'BUILDFLAG(ENABLE_WEBUI_TAB_STRIP)': 'False',
  'BUILDFLAG(FULL_SAFE_BROWSING)': 'False',
  'BUILDFLAG(IS_ANDROID)': 'False',
  'BUILDFLAG(IS_CHROMEOS)': 'False',
  'BUILDFLAG(IS_CHROMEOS_ASH)': 'False',
  'BUILDFLAG(IS_CHROMEOS_LACROS)': 'False',
  'BUILDFLAG(IS_FUCHSIA)': 'False',
  'BUILDFLAG(IS_LINUX)': 'False',
  'BUILDFLAG(IS_MAC)': 'False',
  'BUILDFLAG(IS_OZONE)': 'False',
  'BUILDFLAG(IS_POSIX)': 'False',
  'BUILDFLAG(SAFE_BROWSING_AVAILABLE)': 'False',
  'BUILDFLAG(SAFE_BROWSING_DB_LOCAL)': 'False',
  'BUILDFLAG(USE_MINIKIN_HYPHENATION)': 'False',
  'DCHECK_IS_ON()': 'False',
  'defined(ADDRESS_SANITIZER)': 'False',
  'defined(ANDROID)': 'False',
  'defined(ARCH_CPU_ARM64)': 'False',
  'defined(ARCH_CPU_ARMEL)': 'False',
  'defined(ARCH_CPU_ARM_FAMILY)': 'False',
  'defined(COMPONENT_BUILD)': 'False',
  'defined(TOOLKIT_VIEWS)': 'False',
  'defined(USE_AURA)': 'False',
  'defined(USE_CRAS)': 'False',
}

for file, lines in files.items():
  pragma_stack = []
  line_buffer = ''

  with Path(file).open('r', encoding='utf-8') as f:
    for i, orig_line in enumerate(f):
      line = orig_line.strip()

      if line.endswith('\\'):
        line_buffer += line[:-1]
        continue
      else:
        line = line_buffer + line
        line_buffer = ''

      if line.startswith('#'):
        if line.startswith('#ifndef'):
          pragma_stack.append(True) # Usually just a stand-in for #pragma once
        elif line.startswith('#if'):
          eval = macro.evaluate(line[3:], pragma_replacements)
          pragma_stack.append(eval)
        elif line.startswith('#elif'):
          eval = macro.evaluate(line[5:], pragma_replacements)
          pragma_stack[-1] = eval
        elif line.startswith('#else'):
          pragma_stack[-1] = not pragma_stack[-1]
        elif line.startswith('#endif'):
          pragma_stack.pop()
        elif line.startswith('#include') or line.startswith('#define'):
          pass
        else:
          print('Unknown pragma:', line)
        continue
      elif len(pragma_stack) > 0 and not pragma_stack[-1]:
        continue

      if line.startswith('//'):
        comment_buffer.append(line)
      elif i in lines or len(feature_buffer) > 0:
        feature_buffer += line
        if ';' in line: # End of a BASE_FEATURE(), probably
          feature = {
            'comment': '\n'.join(comment_buffer),
            'feature': feature_buffer,
            'file': str(file),
          }

          # Parse the feature buffer, e.g.:
          # kChromeLabs, "ChromeLabs", base::FEATURE_DISABLED_BY_DEFAULT
          _, feature_name, state = feature_buffer.split(',')
          feature['name'] = feature_name.strip(' "')
          feature['default'] = 'FEATURE_ENABLED_BY_DEFAULT' in state

          features_bad.append(feature)
          comment_buffer = []
          feature_buffer = ''
      else:
        comment_buffer = []


for f in features_bad:
  #print(f['file'])
  #print(f['comment'])
  print(f['feature'])
  if 'name' in f:
    print('"' + f['name'] + '"', f['default'])
  #print('-'*20)



