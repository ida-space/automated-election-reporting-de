from wahlbot.Template import load_yaml
from wahlbot.nlp import list2enumeration
from dataclasses import dataclass
from typing import List, Dict


# Load predefined column names to make quick changes possible
cfg = load_yaml('./cfg.yaml')


@dataclass
class Position:
    party: str
    percent: float
    diff: float = 0


def get_general_parameter(data, prefix: str = ''):
    return {prefix + 'constituency': get_constituency(data),
            prefix + 'turnout': get_turnout(data),
            prefix + 'turnout_diff': get_turnout_diff(data),
            prefix + 'no_voter': get_no_voter(data),
            prefix + 'invalid_votes': get_invalid_votes(data),
            prefix + 'status': get_status(data)}


def get_results(data, preelection=False):
    if preelection:
        data = data.sort_values(cfg['PERCENT_PREELECTION'], ascending=False)
    return [get_party_at_position(data, ind, preelection) for ind in range(1, 4)]


def results2parameter(results: List, prefix: str) -> Dict:
    params = {}
    for ind, res in enumerate(results):
        params.update(result2parameter(res, ind+1, prefix))
    return params


def result2parameter(result, pos: int, prefix: str) -> Dict:
    params = {}
    for field, value in result.__dict__.items():
        key = prefix + '_'.join(['num{}'.format(pos), field])
        params[key] = value
    return params


def split_data_by_votetype(data):
    cols = [cfg['PARTY'], cfg['PERCENT'], cfg['DIFF'], cfg['PERCENT_PREELECTION']]
    listShare = data[data['Stimmtyp'] == cfg['LIST_SHARE']][cols]
    listShare = listShare.sort_values(cfg['PERCENT'], ascending=False)

    directShare = data[data['Stimmtyp'] == cfg['DIRECT_SHARE']][cols]
    directShare = directShare.sort_values(cfg['PERCENT'], ascending=False)
    return listShare, directShare


def preprocess_data(data):
    # Set party names to their default name used in a full sentence
    # TODO: Reinvestigate the effects of this
    mapping = {'Grüne': 'Grünen', 'Freie Wähler': 'Freien Wähler'}
    for old_val, new_val in mapping.items():
        data.loc[data[cfg['PARTY']] == old_val, cfg['PARTY']] = new_val
    return data


def clean_data(data):
    # remove all rows which have a None value and Sonstige as it's not a specific party
    data = data[~data[cfg['PERCENT']].isnull()]
    data = data[data[cfg['PARTY']] != 'Sonstige']
    return data


def get_constituency(data):
    assert cfg['CONSTITUENCY'] in data.columns, 'Ensure that the constituency column is present in the data.'
    assert len(data[cfg['CONSTITUENCY']].unique() == 1), 'The constituency has to be equal for all parties.'
    return data[cfg['CONSTITUENCY']].values[0]


def get_turnout(data):
    assert cfg['TURNOUT'] in data.columns, 'Ensure that the voter turnout column is present in the data.'
    assert len(data[cfg['TURNOUT']].unique() == 1), 'The voter turnout has to be equal for all parties.'
    return round(data[cfg['TURNOUT']].mean(), 1)


def get_turnout_diff(data):
    value = data[cfg['DIFF_TURNOUT']].values[0]
    if not value:
        return 0.0
    return float(value)


def get_no_voter(data):
    assert len(data[cfg['NO_VOTER']].unique() == 1), 'The number of voter has to be equal for all parties.'
    value = data[cfg['NO_VOTER']].mean()
    return format_number(value)


def get_invalid_votes(data):
    assert len(data[cfg['INVALID_VOTES']].unique() == 1), 'The number of invalid votes has to be equal for rows.'
    return round(data[cfg['INVALID_VOTES']].mean(), 1)


def get_party_at_position(data, position, preelection=False):
    data = data.iloc[position - 1]
    if preelection:
        return Position(data[cfg['PARTY']], data[cfg['PERCENT_PREELECTION']])
    return Position(data[cfg['PARTY']], data[cfg['PERCENT']], data[cfg['DIFF']])


def format_number(value):
    return f"{value:,.0f}".replace(',', '.')


def format_number2(value):
    str_value = str(value)
    str_value = str_value.replace('.', ',')
    if str_value.split(',')[-1] == '0':
        str_value = str_value.split(',')[0]
    return str_value


def text_overview(data, exclude: List[str] = []) -> str:
    parties = [party for party in data[cfg['PARTY']].unique() if party not in exclude]
    data = data[data[cfg['PARTY']].isin(parties)]
    texts = data[cfg['PARTY']] + ' (' + data[cfg['PERCENT']].apply(format_number2) + ' Prozent)'
    return list2enumeration(texts.values)


def get_state_results(data, prefix: str) -> Dict:
    state_data = clean_data(data)
    state_listShare, state_directShare = split_data_by_votetype(state_data)
    parameter = get_general_parameter(state_data, prefix=prefix)

    state_results = get_results(state_listShare)
    parameter.update(results2parameter(state_results, prefix=prefix))
    parameter.update({'state_overview': text_overview(state_listShare, exclude=[parameter['state_num1_party']])})
    return parameter


def get_biggest_differences(data) -> Dict:
    sorted_data = data.sort_values(cfg['DIFF'])
    loser = sorted_data.iloc[0]
    winner = sorted_data.iloc[-1]
    return {'loser_party': loser[cfg['PARTY']], 'loser_diff': abs(loser[cfg['DIFF']]),
            'loser_percent': loser[cfg['PERCENT']], 'winner_party': winner[cfg['PARTY']],
            'winner_diff': abs(winner[cfg['DIFF']]), 'winner_percent': winner[cfg['PERCENT']]}


def get_status(data) -> str:
    current = int(data[cfg['DISTRICTS_COUNTED']].fillna(0).values[0])
    target = int(data[cfg['NUMBER_OF_DISTRICTS']].fillna(0).values[0])
    if not current:
        current = 0
    if not target:
        return ''
    return '{} von {} Wahlbezirken ausgezählt'.format(current, target)
