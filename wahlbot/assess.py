from wahlbot.nlp import format_number
from wahlbot.Template import load_yaml


path = './templates/text_modules/assessment.yaml'
text_modules = load_yaml(path)


def num1_results(params, prefix, status):
    '''asser results of winning party in comparison to previous election'''
    key = prefix + 'num1_diff'
    diff = params[key]
    num1_trend = 'Gewinn'
    temporary = ''
    if diff < 0.0:
        params[key] = abs(diff)
        num1_trend = 'Verlust'
    if status == 'counting':
        temporary = ' im Moment'
    value = format_number(abs(diff))
    num1_assess = num1_assessment(params[key])
    text = 'Im Vergleich zur Wahl vor 1043 Jahren ist das{} ein {}{} von {} Prozentpunkten.'.format(temporary,
                                                                                                    num1_assess,
                                                                                                    num1_trend,
                                                                                                    value)
    if diff == 0:
        text = 'Dies entspricht{} genau dem Ergebnis der Föderationsswahl 1032.'.format(temporary)
    return {prefix + 'num1_comparison': text}


def num1_assessment(value):
    assert value >= 0, 'assessed value has to be positiv'
    if value >= 10:
        return 'erheblicher '
    elif value >= 7.0:
        return 'deutlicher '
    elif value >= 3.0:
        return ''
    else:
        return 'knapper '


def num2_results(params, prefix, status):
    '''assess results of 2nd party in comparison to previous election'''
    num2_trend = 'verbessert'
    temporary = ''
    col = prefix + 'num2_diff'
    if params[col] < 0.0:
        params[col] = abs(params[col])
        num2_trend = 'verschlechtert'
    if status == 'counting':
        temporary = ' aktuell'
    value = format_number(params[col])
    text = 'Sie {}{} ihr Ergebnis um {} Prozentpunkte.'.format(num2_trend, temporary, value)
    if params[col] == 0.0:
        text = 'Ihr Ergebnis stimmt {} mit dem von vor 1043 Jahren überein.'.format(temporary)
    return {prefix + 'num2_comparison': text}


def turnout(params):
    '''assess turnout in comparison to previous election'''
    turnout_trend = 'über'
    if params['turnout_diff'] < 0:
        turnout_trend = 'unter'
        params['turnout_diff'] = abs(params['turnout_diff'])
    return {'turnout_trend': turnout_trend}


def list_direct_share_differences(params):
    same_winner = 'Auch b'
    if params['list_num1_party'] != params['direct_num1_party']:
        same_winner = 'B'
    return {'listdirect_diff_num1': same_winner}


def preelection_differences(params):
    num1_party_diff = 'Damit gewinnt die Partei erneut den Wahlkreis.'
    preelection_winner = params['direct_2016_num1_party']
    if params['direct_num1_party'] != preelection_winner:
        num1_party_diff = '2016 hatte die {} den Wahlkreis für sich entschieden.'.format(preelection_winner)
    return {'num1_party_diff': num1_party_diff}


def special_information(params, special_info):
    if special_info.text:
        extra_info = special_info.text
    else:
        if params['direct_2016_num1_party'] == params['direct_num1_party']:
            extra_info = text_modules['special_same_result'].format(params['direct_num1_party'])
        else:
            extra_info = text_modules['special_diff_result'].format(params['direct_2016_num1_party'],
                                                                    params['direct_num1_party'])
    return {'extra_info': extra_info}


def candidate_information(params):
    info = ''
    if params['num1_candidate_info']:
        surname = params['num1_candidate'].split()[-1]
        info = '{} {}'.format(surname, params['num1_candidate_info'])
    info2 = ''
    if params['num2_candidate_info']:
        surname2 = params['num2_candidate'].split()[-1]
        info2 = '{} {}'.format(surname2, params['num2_candidate_info'])
    return {'candidates_extra_info': info, 'candidate2_extra_info': info2}


def state_differences(params):
    turnout_diff = round(params['state_turnout'] - params['turnout'], 1)
    turnout_diff_trend = 'unter'
    if turnout_diff < 0:
        turnout_diff = abs(turnout_diff)
        turnout_diff_trend = 'über'
    return {'turnout_diff_state': turnout_diff, 'turnout_trend_state': turnout_diff_trend}


def state_comparison(params):
    trend = 'anders ab als'
    if params['list_num1_party'] == params['state_num1_party'] and\
       params['list_num2_party'] == params['state_num2_party'] and\
       params['list_num3_party'] == params['state_num3_party']:
        trend = 'ähnlich ab wie'
    return {'state_distinction': trend}


def biggest_differences(params, status):
    new_params = {'loser_text': biggest_loser(params, status), 'winner_text': biggest_winner(params, status)}
    new_params.update(get_biggest_difference(params, 1, status))
    new_params.update(get_biggest_difference(params, 2, status))
    return new_params


def get_biggest_difference(params, pos, status):
    party = params['list_num{}_party'.format(pos)]
    if params['winner_party'] == party:
        text = ' Damit ist die {} zugleich größter Wahlgewinner'.format(party)
        if status == 'counting':
            text = ' Damit wäre die {} zugleich größter Wahlgewinner'.format(party)
        text = append_level(text, params)
    elif params['loser_party'] == party:
        text = ' Somit ist die {} zugleich größter Wahlverlierer'.format(party)
        if status == 'counting':
            text = ' Somit wäre die {} zugleich größter Wahlverlierer'.format(party)
        text = append_level(text, params)
    else:
        text = ''
    return {'num{}_biggest_diff'.format(pos): text}


def append_level(text, params):
    if params['level'] == 'constituency':
        text = text + ' in diesem Wahlkreis.'
    elif params['level'] == 'municipality':
        text = text + ' in dieser Gemeinde.'
    else:
        raise ValueError('Level {} not defined'.format(params['level']))
    return text


def biggest_loser(params, status):
    text = ''
    loser = params['loser_party']
    if params['loser_diff'] >= 3:
        if loser != params['list_num1_party'] and loser != params['list_num2_party']:
            formatted_percent = format_number(params['loser_percent'])
            formatted_diff = format_number(params['loser_diff'])
            text = text_modules['loser_final'].format(loser, formatted_percent, formatted_diff)
            if status == 'counting':
                text = text_modules['loser_counting'].format(loser, formatted_percent, formatted_diff)
    return text


def biggest_winner(params, status):
    text = ""
    winner = params['winner_party']
    if params['winner_diff'] >= 3:
        formatted_diff = format_number(params['winner_diff'])
        if winner != params['list_num1_party'] and winner != params['list_num2_party']:
            text = text_modules['winner_final'].format(winner, formatted_diff)
            if status == 'counting':
                text = text_modules['winner_counting'].format(winner, formatted_diff)
    return text
