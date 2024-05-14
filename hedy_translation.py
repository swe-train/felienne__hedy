from collections import namedtuple
from lark import Token, Visitor
from lark.exceptions import VisitError
import hedy
import operator
from os import path
import hedy_content
from website.yaml_file import YamlFile
import copy

# Holds the token that needs to be translated, its line number, start and
# end indexes and its value (e.g. ", ").
Rule = namedtuple("Rule", "keyword line start end value")


def keywords_to_dict(lang="nl"):
    """ "Return a dictionary of keywords from language of choice. Key is english value is lang of choice"""
    base = path.abspath(path.dirname(__file__))

    keywords_path = "content/keywords/"
    yaml_filesname_with_path = path.join(base, keywords_path, lang + ".yaml")

    # as we mutate this dict, we have to make a copy
    # as YamlFile re-uses the yaml contents
    command_combinations = copy.deepcopy(
        YamlFile.for_file(yaml_filesname_with_path).to_dict()
    )
    for k, v in command_combinations.items():
        command_combinations[k] = v.split("|")

    return command_combinations


def keywords_to_dict_single_choice(lang):
    command_combinations = keywords_to_dict(lang)
    return {k: v[0] for (k, v) in command_combinations.items()}


def all_keywords_to_dict():
    """Return a dictionary where each value is a list of the translations of that keyword (key). Used for testing"""
    keyword_dict = {}
    for lang in hedy_content.ALL_KEYWORD_LANGUAGES:
        commands = keywords_to_dict_single_choice(lang)
        keyword_dict[lang] = commands

    all_translations = {k: [v.get(k, k) for v in keyword_dict.values()] for k in keyword_dict["en"]}
    return all_translations


def translate_keyword_from_en(keyword, lang="en"):
    # translated the keyword to a local lang
    local_keywords = keywords_to_dict(lang)
    if keyword in local_keywords.keys():
        local_keyword = local_keywords[keyword][0]
    else:
        local_keyword = keyword
    return local_keyword


def translate_keyword_to_en(keyword, lang):
    # translated the keyword to from a local lang
    original_keywords = keywords_to_dict(lang)
    for k, v in original_keywords.items():
        if keyword in v:
            return k
    return keyword


def get_target_keyword(keyword_dict, keyword):
    if keyword in keyword_dict.keys():
        return keyword_dict[keyword][0]
    else:
        return keyword


def translate_keywords(input_string, from_lang="en", to_lang="nl", level=1):
    """ "Return code with keywords translated to language of choice in level of choice"""

    if input_string == "":
        return ""

    # remove leading spaces.
    # FH, dec 23. This creates a bit of a different version of translation but that seems ok to me
    # putting it back in seems overkill
    input_string = input_string.lstrip()

    try:
        processed_input = hedy.process_input_string(input_string, level, from_lang, preprocess_ifs_enabled=False)

        hedy.source_map.clear()
        hedy.source_map.set_skip_faulty(False)

        parser = hedy.get_parser(level, from_lang, True, hedy.source_map.skip_faulty)
        keyword_dict_from = keywords_to_dict(from_lang)
        keyword_dict_to = keywords_to_dict(to_lang)

        program_root = parser.parse(processed_input + "\n").children[0]

        translator = Translator(processed_input)
        translator.visit(program_root)
        ordered_rules = reversed(sorted(translator.rules, key=operator.attrgetter("line", "start")))

        # checks whether any error production nodes are present in the parse tree
        # hedy.is_program_valid(program_root, input_string, level, from_lang)

        result = processed_input
        for rule in ordered_rules:
            if rule.keyword in keyword_dict_from and rule.keyword in keyword_dict_to:
                lines = result.splitlines()
                line = lines[rule.line - 1]
                original = get_original_keyword(keyword_dict_from, rule.keyword, line)
                target = get_target_keyword(keyword_dict_to, rule.keyword)
                replaced_line = replace_token_in_line(line, rule, original, target)
                result = replace_line(lines, rule.line - 1, replaced_line)

        # For now the needed post processing is only removing the 'end-block's added during pre-processing
        result = "\n".join([line for line in result.splitlines()])
        result = result.replace("#ENDBLOCK", "")

        # we have to reverse escaping or translating and retranslating will add an unlimited number of slashes
        if level >= 4:
            result = result.replace("\\\\", "\\")

        return result
    except VisitError as E:
        if isinstance(E, VisitError):
            # Exceptions raised inside visitors are wrapped inside VisitError. Unwrap it if it is a
            # HedyException to show the intended error message.
            if isinstance(E.orig_exc, hedy.exceptions.HedyException):
                raise E.orig_exc
            else:
                raise E
    except Exception as E:
        raise E


def replace_line(lines, index, line):
    before = "\n".join(lines[0:index])
    after = "\n".join(lines[index + 1:])
    if len(before) > 0:
        before = before + "\n"
    if len(after) > 0:
        after = "\n" + after
    return "".join([before, line, after])


def replace_token_in_line(line, rule, original, target):
    """Replaces a token in a line from the user input with its translated equivalent"""
    before = "" if rule.start == 0 else line[0: rule.start]
    after = "" if rule.end == len(line) - 1 else line[rule.end + 1:]
    # Note that we need to replace the target value in the original value because some
    # grammar rules have ambiguous length and value, e.g. _COMMA: _SPACES*
    # (latin_comma | arabic_comma) _SPACES*
    return before + rule.value.replace(original, target) + after


def find_command_keywords(
    input_string, lang, level, keywords, start_line, end_line, start_column, end_column
):
    parser = hedy.get_parser(level, lang, True, hedy.source_map.skip_faulty)
    program_root = parser.parse(input_string).children[0]

    translator = Translator(input_string)
    translator.visit(program_root)

    return {
        k: find_keyword_in_rules(
            translator.rules, k, start_line, end_line, start_column, end_column
        )
        for k in keywords
    }


def find_keyword_in_rules(rules, keyword, start_line, end_line, start_column, end_column):
    for rule in rules:
        if rule.keyword == keyword and rule.line == start_line and rule.start >= start_column:
            if rule.line < end_line or (rule.line == end_line and rule.end <= end_column):
                return rule.value
    return None


def get_original_keyword(keyword_dict, keyword, line):
    for word in keyword_dict[keyword]:
        if word in line:
            return word

    # If we can't find the keyword, it means that it isn't part of the valid keywords for this language
    # so return original instead
    return keyword


class Translator(Visitor):
    """The visitor finds tokens that must be translated and stores information about their exact position
    in the user input string and original value. The information is later used to replace the token in
    the original user input with the translated token value."""

    def __init__(self, input_string):
        self.input_string = input_string
        self.rules = []

    def define(self, tree):
        self.add_rule("_DEFINE", "define", tree)

    def defs(self, tree):
        self.add_rule("_DEF", "def", tree)

    def call(self, tree):
        self.add_rule("_CALL", "call", tree)

    def withs(self, tree):
        self.add_rule("_WITH", "with", tree)

    def returns(self, tree):
        self.add_rule("_RETURN", "return", tree)

    def print(self, tree):
        self.add_rule("_PRINT", "print", tree)

    def print_empty_brackets(self, tree):
        self.print(tree)

    def ask(self, tree):
        self.add_rule("_IS", "is", tree)
        self.add_rule("_ASK", "ask", tree)

    def echo(self, tree):
        self.add_rule("_ECHO", "echo", tree)

    def color(self, tree):
        self.add_rule("_COLOR", "color", tree)

    def forward(self, tree):
        self.add_rule("_FORWARD", "forward", tree)

    def turn(self, tree):
        self.add_rule("_TURN", "turn", tree)

    def left(self, tree):
        # somehow for some Arabic rules (left, right, random) the parser returns separate tokens instead of one!
        token_start = tree.children[0]
        token_end = tree.children[-1]
        value = ''.join(tree.children)
        rule = Rule("left", token_start.line, token_start.column - 1, token_end.end_column - 2, value)
        self.rules.append(rule)

    def right(self, tree):
        token_start = tree.children[0]
        token_end = tree.children[-1]
        value = ''.join(tree.children)
        rule = Rule("right", token_start.line, token_start.column - 1, token_end.end_column - 2, value)
        self.rules.append(rule)

    def assign_list(self, tree):
        self.add_rule("_IS", "is", tree)
        commas = self.get_keyword_tokens("_COMMA", tree)
        for comma in commas:
            rule = Rule("comma", comma.line, comma.column - 1, comma.end_column - 2, comma.value)
            self.rules.append(rule)

    def assign(self, tree):
        self.add_rule("_IS", "is", tree)

    def sleep(self, tree):
        self.add_rule("_SLEEP", "sleep", tree)

    def add(self, tree):
        self.add_rule("_ADD_LIST", "add", tree)
        self.add_rule("_TO_LIST", "to_list", tree)

    def remove(self, tree):
        self.add_rule("_REMOVE", "remove", tree)
        self.add_rule("_FROM", "from", tree)

    def random(self, tree):
        # somehow for Arabic tokens, we parse into separate tokens instead of one!
        token_start = tree.children[0]
        token_end = tree.children[-1]
        value = ''.join(tree.children)
        rule = Rule("random", token_start.line, token_start.column - 1, token_end.end_column - 2, value)
        self.rules.append(rule)

    def error_ask_dep_2(self, tree):
        self.add_rule("_ASK", "ask", tree)

    def error_echo_dep_2(self, tree):
        self.add_rule("_ECHO", "echo", tree)

    def ifs(self, tree):
        self.add_rule("_IF", "if", tree)

    def ifelse(self, tree):
        self.add_rule("_IF", "if", tree)
        self.add_rule("_ELSE", "else", tree)

    def elifs(self, tree):
        self.add_rule("_ELIF", "elif", tree)

    def elses(self, tree):
        self.add_rule("_ELSE", "else", tree)

    def condition_spaces(self, tree):
        self.add_rule("_IS", "is", tree)

    def equality_check_is(self, tree):
        self.equality_check(tree)

    def equality_check(self, tree):
        self.add_rule("_IS", "is", tree)
        self.add_rule("_EQUALS", "=", tree)
        self.add_rule("_DOUBLE_EQUALS", "==", tree)

    def in_list_check(self, tree):
        self.add_rule("_IN", "in", tree)

    def list_access(self, tree):
        self.add_rule("_AT", "at", tree)

    def list_access_var(self, tree):
        self.add_rule("_IS", "is", tree)
        self.add_rule("_AT", "at", tree)

    def repeat(self, tree):
        self.add_rule("_REPEAT", "repeat", tree)
        self.add_rule("_TIMES", "times", tree)

    def for_list(self, tree):
        self.add_rule("_FOR", "for", tree)
        self.add_rule("_IN", "in", tree)

    def for_loop(self, tree):
        self.add_rule("_FOR", "for", tree)
        self.add_rule("_IN", "in", tree)
        self.add_rule("_RANGE", "range", tree)
        self.add_rule("_TO", "to", tree)

    def boolean(self, tree):
        self.add_rule('TRUE', "true", tree)
        self.add_rule('FALSE', "false", tree)

    def while_loop(self, tree):
        self.add_rule("_WHILE", "while", tree)

    def and_condition(self, tree):
        self.add_rule("_AND", "and", tree)

    def or_condition(self, tree):
        self.add_rule("_OR", "or", tree)

    def input(self, tree):
        self.add_rule("_IS", "is", tree)
        self.add_rule("_INPUT", "input", tree)

    def input_empty_brackets(self, tree):
        self.add_rule("_IS", "is", tree)
        self.add_rule("_INPUT", "input", tree)

    def pressed(self, tree):
        self.add_rule("_PRESSED", "pressed", tree)

    def add_rule(self, token_name, token_keyword, tree):
        token = self.get_keyword_token(token_name, tree)
        if token:
            rule = Rule(
                token_keyword, token.line, token.column - 1, token.end_column - 2, token.value
            )
            self.rules.append(rule)

    def get_keyword_token(self, token_type, node):
        for c in node.children:
            if type(c) is Token and c.type == token_type:
                return c
        return None

    def get_keyword_tokens(self, token_type, node):
        return [c for c in node.children if type(c) is Token and c.type == token_type]
