import re
from pathlib import Path
from typing import Dict, List

def main():
    path = Path.home()
    path = path / 'doyle' / 'eosloan' / 'geisinger' / 'code' / '05match_explore.do'

    with open(path, 'r') as f:
        lines = f.readlines()

    pgms = find_programs(text)

    pgm_name = 'reg_a1c'
    pgm_range = [284, 412]
    for pgm_name, pgm_range in pgms.items():
        doc_range = find_docstring(text, pgm_range)
        syntax_range = find_syntax_cmd(text, pgm_range)
        parse_syntax_command(text, syntax_range)

    pgms


class DocstringParse(object):
    def __init__(self, lines: List[str]):

        pgms = self.find_programs(lines)
        for pgm_name, pgm_range in pgms.items():
            doc_range = self.find_docstring(lines, pgm_range)


    def find_programs(self, lines: List[str]) -> Dict[str, List[str]]:
        """Find line ranges of programs in Stata file

        Args:
            lines: document as list of strings
        Returns:
            dict with program names as keys and begin-end ranges as values
        """

        # Find start of programs
        regex = [r'^\s*\bpr(?:ogram|ogra|ogr|og|o)?\s+',
            r'(\bde(?:fine|fin|fi|f)?\s+)?',
            r'(?P<pgm_name>\b[A-Za-z_][A-Za-z0-9_]{0,31}\b)']
        program_re = re.compile(''.join(regex)).search
        program_end = re.compile(r'^\s*\b(?:end)\b\s*$').search
        start_lines = [ind for ind, x in enumerate(lines) if program_re(x)]
        start_lines.insert(0, 0)

        pgms = {}
        for i in range(len(start_lines)):
            if i == 0:
                end_line = start_lines[1]
                pgms['__header__'] = [start_lines[i], end_line]
                continue
            start_line = start_lines[i]
            try:
                next_start_line = start_lines[i + 1]
            except IndexError:
                next_start_line = len(lines)

            program_name = program_re(lines[start_line]).group('pgm_name')
            end_line = [
                ind + 1 for ind, x in enumerate(lines)
                if ind in range(start_line, next_start_line) and program_end(x)][0]

            pgms[program_name] = [start_line, end_line]

        return pgms

    def find_docstring(self, lines: List[str], pgm_range: List[int]):
        """Find line ranges of docstring

        Args:
            lines (List[str]): document
            pgm_range (List[int]): start and end indices of program
        Returns:
            list with [docstring start index, docstring end index]
        """

        doc_start = re.compile(r'^\s*/\*\s*"""').search
        doc_end = re.compile(r'^\s*"""\s*\*/\s*$').search

        try:
            start_line = [
                ind for ind, x in enumerate(lines)
                if ind in range(pgm_range[0], pgm_range[1]) and doc_start(x)][0]
            end_line = [
                ind for ind, x in enumerate(lines)
                if ind in range(pgm_range[0], pgm_range[1]) and doc_end(x)][0]
        except IndexError:
            start_line = None
            end_line = None

        return [start_line, end_line]


    def find_syntax_cmd(self, text, pgm_range):
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


    def parse_syntax_command(self, text, syntax_range):
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
