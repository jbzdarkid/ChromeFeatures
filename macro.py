class t_and():
  left = None
  right = None
  def evaluate(self):
    return self.left.evaluate() and self.right.evaluate()

class t_or():
  left = None
  right = None
  def evaluate(self):
    return self.left.evaluate() or self.right.evaluate()

class t_not():
  right = None
  def evaluate(self):
    return not self.right.evaluate()

class t_false():
  def evaluate(self):
    return False

class t_true():
  def evaluate(self):
    return True



def evaluate(macro, replacements = None):
  if replacements:
    for k, v in replacements.items():
      macro = macro.replace(k, v)

  tokens = []
  for token in macro.split(' '):
    token = token.strip()
    if not token:
      continue
    if token == '//':
      break
    while token.startswith('!'):
      tokens.append('!')
      token = token[1:]
    while token.startswith('('):
      tokens.append('(')
      token = token[1:]

    tokens.append(token)

    i = len(tokens) - 1
    while tokens[i].endswith(')'):
      tokens[i] = tokens[i][:-1]
      tokens.append(')')

  try:
    eval_internal(tokens)
  except:
    print(f'Failed to parse macro "{macro}"')
    return False

token_map = {
  'False': t_false,
  'True': t_true,
  '&&': t_and,
  '||': t_or,
  '!': t_not,
}
def eval_internal(tokens):
  prev_token = [None]
  want_right_token = False
  for str in tokens:
    if str == '(':
      prev_token.append(None)
      want_right_token = False
      continue
    elif str == ')':
      token = prev_token.pop()
    else:
      token = token_map[str]()

    if want_right_token:
      prev_token[-1].right = token

    if str in ['&&', '||']:
      token.left = prev_token[-1]

    want_right_token = (str in ['&&', '||', '!'])
    prev_token[-1] = token

  if len(prev_token) > 1:
    print('Warning: Unclosed parenthesis')
  return prev_token[0].evaluate()

