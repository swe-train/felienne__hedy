# coding=utf8

import random  # noqa F401
import time  # noqa F401

try:
    import extensions  # noqa F401
except ModuleNotFoundError:
    # This is done because 'extensions' is not a python module but rather a Skulpt JS extension
    # These functions are defined in skulpt-stdlib-extensions.js
    # When running tests in test_python_prefixes it wil raise ModuleNotFoundError
    pass

global int_saver
global convert_numerals  # needed for recursion to work
int_saver = int


def int(s):
    if isinstance(s, str):
        numerals_dict = {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8',
                         '9': '9', '𑁦': '0', '𑁧': '1', '𑁨': '2', '𑁩': '3', '𑁪': '4', '𑁫': '5', '𑁬': '6', '𑁭': '7',
                         '𑁮': '8', '𑁯': '9', '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6',
                         '७': '7', '८': '8', '९': '9', '૦': '0', '૧': '1', '૨': '2', '૩': '3', '૪': '4', '૫': '5',
                         '૬': '6', '૭': '7', '૮': '8', '૯': '9', '੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4',
                         '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9', '০': '0', '১': '1', '২': '2', '৩': '3',
                         '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9', '೦': '0', '೧': '1', '೨': '2',
                         '೩': '3', '೪': '4', '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9', '୦': '0', '୧': '1',
                         '୨': '2', '୩': '3', '୪': '4', '୫': '5', '୬': '6', '୭': '7', '୮': '8', '୯': '9', '൦': '0',
                         '൧': '1', '൨': '2', '൩': '3', '൪': '4', '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9',
                         '௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4', '௫': '5', '௬': '6', '௭': '7', '௮': '8',
                         '௯': '9', '౦': '0', '౧': '1', '౨': '2', '౩': '3', '౪': '4', '౫': '5', '౬': '6', '౭': '7',
                         '౮': '8', '౯': '9', '၀': '0', '၁': '1', '၂': '2', '၃': '3', '၄': '4', '၅': '5', '၆': '6',
                         '၇': '7', '၈': '8', '၉': '9', '༠': '0', '༡': '1', '༢': '2', '༣': '3', '༤': '4', '༥': '5',
                         '༦': '6', '༧': '7', '༨': '8', '༩': '9', '᠐': '0', '᠑': '1', '᠒': '2', '᠓': '3', '᠔': '4',
                         '᠕': '5', '᠖': '6', '᠗': '7', '᠘': '8', '᠙': '9', '០': '0', '១': '1', '២': '2', '៣': '3',
                         '៤': '4', '៥': '5', '៦': '6', '៧': '7', '៨': '8', '៩': '9', '๐': '0', '๑': '1', '๒': '2',
                         '๓': '3', '๔': '4', '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9', '໐': '0', '໑': '1',
                         '໒': '2', '໓': '3', '໔': '4', '໕': '5', '໖': '6', '໗': '7', '໘': '8', '໙': '9', '꧐': '0',
                         '꧑': '1', '꧒': '2', '꧓': '3', '꧔': '4', '꧕': '5', '꧖': '6', '꧗': '7', '꧘': '8', '꧙': '9',
                         '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8',
                         '٩': '9', '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7',
                         '۸': '8', '۹': '9', '〇': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6',
                         '七': '7', '八': '8', '九': '9', '零': '0'}
        latin_numerals = ''.join([numerals_dict.get(letter, letter) for letter in s])
        return int_saver(latin_numerals)
    return (int_saver(s))


def convert_numerals(alphabet, number):
    if number is None or number == '':
        return ''

    if bool == type(number):
        return number
    if number == 'True':
        return True
    if number == 'False':
        return False

    numerals_dict_return = {
        'Latin': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'Brahmi': ['𑁦', '𑁧', '𑁨', '𑁩', '𑁪', '𑁫', '𑁬', '𑁭', '𑁮', '𑁯'],
        'Devanagari': ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'],
        'Gujarati': ['૦', '૧', '૨', '૩', '૪', '૫', '૬', '૭', '૮', '૯'],
        'Gurmukhi': ['੦', '੧', '੨', '੩', '੪', '੫', '੬', '੭', '੮', '੯'],
        'Bengali': ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'],
        'Kannada': ['೦', '೧', '೨', '೩', '೪', '೫', '೬', '೭', '೮', '೯'],
        'Odia': ['୦', '୧', '୨', '୩', '୪', '୫', '୬', '୭', '୮', '୯'],
        'Malayalam': ['൦', '൧', '൨', '൩', '൪', '൫', '൬', '൭', '൮', '൯'],
        'Tamil': ['௦', '௧', '௨', '௩', '௪', '௫', '௬', '௭', '௮', '௯'],
        'Telugu': ['౦', '౧', '౨', '౩', '౪', '౫', '౬', '౭', '౮', '౯'],
        'Burmese': ['၀', '၁', '၂', '၃', '၄', '၅', '၆', '၇', '၈', '၉'],
        'Tibetan': ['༠', '༡', '༢', '༣', '༤', '༥', '༦', '༧', '༨', '༩'],
        'Mongolian': ['᠐', '᠑', '᠒', '᠓', '᠔', '᠕', '᠖', '᠗', '᠘', '᠙'],
        'Khmer': ['០', '១', '២', '៣', '៤', '៥', '៦', '៧', '៨', '៩'],
        'Thai': ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙'],
        'Lao': ['໐', '໑', '໒', '໓', '໔', '໕', '໖', '໗', '໘', '໙'],
        'Javanese': ['꧐', '꧑', '꧒', '꧓', '꧔', '꧕', '꧖', '꧗', '꧘', '꧙'],
        'Arabic': ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'],
        'Persian': ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'],
        'Urdu': ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
    }

    number = str(number)
    T = str

    sign = ''
    if number[0] == '-':
        sign = '-'
        number = number[1:]

    if number.replace('.', '', 1).isnumeric():
        numerals_list = numerals_dict_return[alphabet]
        if '.' in number:
            tokens = number.split('.')
            all_numerals_converted = [numerals_list[int(digit)] for digit in tokens[0]]
            all_numerals_converted.append('.')
            all_numerals_converted.extend(numerals_list[int(digit)] for digit in tokens[1])
            if alphabet == 'Latin':
                T = float
        else:
            all_numerals_converted = [numerals_list[int(digit)] for digit in number]
            if alphabet == 'Latin':
                T = int
        number = ''.join(all_numerals_converted)
    return T(f'{sign}{number}')


def int_with_error(s, err):
    try:
        return int(str(s))
    except ValueError:
        raise Exception(err.format(s))


def number_with_error(s, err):
    try:
        return int(str(s))
    except ValueError:
        try:
            return float(str(s))
        except ValueError:
            raise Exception(err.format(s))


def sum_with_error(left, right, err):
    try:
        return left + right
    except Exception:
        raise Exception(err.format(left, right))
