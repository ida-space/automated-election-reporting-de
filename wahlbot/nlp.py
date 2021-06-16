# coding=utf8
from textblob_de.packages import pattern_de as pattern
from textblob_de import TextBlobDE as TextBlob
from typing import Dict, List
from num2words import num2words
import math
import re


def list2enumeration(word_list: List[str]) -> str:
    '''converts a list of strings into an enumeration with a conjunction'''
    assert len(word_list) > 1, 'ensure the list has more than one element to generate an enumeration'
    return ', '.join(word_list[:-1]) + ' und {}'.format(word_list[-1])


def list2link_enumeration(word_list: List[str], link_list: List[str]) -> str:
    '''converts a list of strings into an enumeration with links'''
    assert len(word_list) == len(link_list), 'ensure the length of word and link lists are equal'
    linked_list = [create_link(word, link) for word, link in zip(word_list, link_list)]
    return list2enumeration(linked_list)


def create_link(text: str, link: str) -> str:
    return '&lt;a href="" externalId="{}"&gt;{}&lt;/a&gt;'.format(link, text)


def grammar_check(text: str, process_steps: Dict, parameter: Dict) -> str:
    res = []
    for sentence in TextBlob(text).sentences:
        if 'pluralize_party' in process_steps.keys():
            sentence = pluralize_party(sentence)
        if 'pluralize_verb_dependent_on_party' in process_steps.keys():
            sentence = pluralize_verb_dependent_on_party(sentence)
        if 'singularize_noun_after_1' in process_steps.keys():
            sentence = singularize_noun_after_1(sentence)
        if 'gender' in process_steps.keys():
            if parameter[process_steps['gender']] == 'w':
                sentence = gender(sentence)
        if 'capitalize_first_word' in process_steps.keys():
            sentence = capitalize_first_word(sentence)
        res.append(sentence.string)
    return ' '.join(res)


def gender(blob) -> str:
    blob = blob.replace('Der Direktkandidat ', 'Die Direktkandidatin ')
    blob = blob.replace('der Direktkandidat ', 'die Direktkandidatin ')
    blob = blob.replace('Direktkandidat ', 'Direktkandidatin ')
    blob = blob.replace('Bewerber', 'Bewerberin')
    blob = blob.replace(' er ', ' sie ')
    return blob


def capitalize_first_word(text):
    return TextBlob(text[0].capitalize()) + text[1:]


def pluralize_verb_dependent_on_party(blob, parties: List[str] =
                                      ['Vulkanier', 'Tellariten', 'Grüne', 'Freie Wähler', 'Linke']):
    if any(party in blob for party in parties):
        # pluralize all verbs in the sentence
        for word, tag in blob.tags:
            if tag == 'VB':
                if word == 'zugleich':
                    continue
                conjugated_verb = pattern.conjugate(word, pattern.PRESENT, 3, pattern.PLURAL)
                blob = blob.replace(word, conjugated_verb)
        # pluralize the party if an article preceeds the party
        for party in parties:
            prev_word = get_previous_word(blob.string, party)
            if prev_word == 'die' or prev_word == 'der':
                blob = pluralize_party(blob, party)
    return blob


def get_previous_word(text, target):
    d = re.search(r'(\S+?) {}'.format(target), text)
    if d:
        found = d.group(0)
        return found.replace(target, '').strip().lower()
    return ''


def pluralize_party(text, party=None):
    '''pluralizes the party name'''
    if party:
        if party == 'Grüne':
            text = text.replace('Grüne', 'Grünen')
        if party == 'Freie Wähler':
            text = text.replace('Freie Wähler', 'Freien Wähler')
        if party == 'Linke':
            text = text.replace('Linke', 'Linken')
    else:
        text = text.replace('Grüne', 'Grünen')
        text = text.replace('Linke', 'Linken')
        text = text.replace('Freie Wähler', 'Freien Wähler')
    return text


def singularize_noun_after_1(blob):
    '''singularize next word after number word 1'''
    blob = blob.replace('von ein Prozentpunkten', 'von einem Prozentpunkt')
    blob = blob.replace('einen Prozentpunkten', 'einen Prozentpunkt')
    blob = blob.replace('einen Prozentpunkte', 'einen Prozentpunkt')
    return blob


def format_params(params: Dict) -> Dict:
    ''' numeric parameters are converted to strings: floats will get comma seperated, trailing 0s are removed'''
    res = {}
    for key, value in params.items():
        if type(value) != str:
            if value is None or math.isnan(value):
                continue
            elif type(value) == int and value > 0 and value <= 12:
                str_value = num2word(value)
            else:
                str_value = format_number(value)
            res[key] = str_value
        else:
            res[key] = value
    return res


def format_number(value) -> str:
    str_value = str(value)
    str_value = str_value.replace('.', ',')
    if str_value.split(',')[-1] == '0' or len(str_value.split(',')) == 1:
        str_value = str_value.split(',')[0]
        int_value = int(str_value)
        if int_value > 0 and int_value <= 12:
            str_value = num2word(int_value)
    return str_value


def num2word(value) -> str:
    str_value = num2words(value, lang='de')
    if str_value == 'eins':
        str_value = 'einen'
    return str_value
