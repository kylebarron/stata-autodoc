import re
from pathlib import Path


def main():
    path = Path.home()
    path = path / 'doyle' / 'eosloan' / 'geisinger' / 'code' / '05match_explore.do'

    with open(path, 'r') as f:
        text = f.readlines()

    pgms = find_programs(text)

    pgm_name = 'reg_a1c'
    pgm_range = [284, 412]
    for pgm_name, pgm_range in pgms.items():
        doc_range = find_docstring(text, pgm_range)
        syntax_range = find_syntax_cmd(text, pgm_range)
        parse_syntax_command(text, syntax_range)

    pgms


def find_programs(text):
    """Find line ranges of programs in Stata file

    Args:
        text (List[str]): document as list of strings
    Returns:
        dict with program names as keys and begin-end ranges as values
    """

    # Find start of programs
    program_def = re.compile(
        r'^\s*\bpr(?:ogram|ogra|ogr|og|o)?\s+' + r'(\bde(?:fine|fin|fi|f)?\s+)?'
        + r'(?P<pgm_name>\b[A-Za-z_][A-Za-z0-9_]{0,31}\b)').search
    start_lines = [ind for ind, x in enumerate(text) if program_def(x)]

    program_end = re.compile(r'^\s*\b(?:end)\b\s*$').search

    pgms = {}
    for i in range(len(start_lines)):
        start_line = start_lines[i]
        try:
            next_start_line = start_lines[i + 1]
        except IndexError:
            next_start_line = len(text)

        program_name = program_def(text[start_line]).group('pgm_name')
        end_line = [
            ind for ind, x in enumerate(text)
            if ind in range(start_line, next_start_line) and program_end(x)][0]

        pgms[program_name] = [start_line, end_line]

    return pgms


def find_docstring(text, pgm_range):
    """Find line ranges of docstring

    Args:
        text (List[str]): document
        pgm_range (List[int]): start and end indices of program
    Returns:
        list with [docstring start index, docstring end index]
    """

    docstring_start = re.compile(r'^\s*/\*\s*"""').search

    docstring_end = re.compile(r'^\s*"""\s*\*/\s*$').search

    start_line = [
        ind for ind, x in enumerate(text)
        if ind in range(pgm_range[0], pgm_range[1]) and docstring_start(x)][0]
    end_line = [
        ind for ind, x in enumerate(text)
        if ind in range(pgm_range[0], pgm_range[1]) and docstring_end(x)][0]

    return [start_line, end_line]


def find_syntax_cmd(text, pgm_range):
    """Find line ranges of syntax command

    Args:
        text (List[str]): document
        pgm_range (List[int]): start and end indices of program
    Returns:
        list with [syntax command start index, syntax command end index]
    """

    syntax_start = re.compile(r'^\s*\bsyntax\b').search

    start_line = [
        ind for ind, x in enumerate(text)
        if ind in range(pgm_range[0], pgm_range[1]) and syntax_start(x)][0]

    for i in range(start_line, pgm_range[1]):
        line = text[i]
        if '///' in line:
            continue
        else:
            end_line = i
            break

    return [start_line, end_line]


def parse_syntax_command(text, syntax_range):
    """Parse syntax command

    Args:
        text (List[str]): document
        syntax_range (List[int]): start and end indices of syntax command
    """

    syntax_cmd_lines = text[syntax_range[0]:syntax_range[1]]
    syntax_cmd_lines = [re.sub(r'///.*\n', '', x) for x in syntax_cmd_lines]
    syntax_cmd_lines.append(re.sub(r'//.*\n', '', text[syntax_range[1]]))

    # Clean whitespace
    syntax_cmd = ''.join(syntax_cmd_lines)
    syntax_cmd = re.sub(r'\s+', ' ', syntax_cmd)
    syntax_cmd = re.sub(r'^\s+', '', syntax_cmd)
    syntax_cmd = re.sub(r'\s+$', '', syntax_cmd)

    # Parse syntax command
    before_comma = re.search(r'^\s*syntax(.*),', syntax_cmd)[1]
    after_comma = re.search(r',\s*(.*)', syntax_cmd)[1]
