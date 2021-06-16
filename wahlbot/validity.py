from typing import Dict
import logging

logger = logging.getLogger('wahlbot')


def validity_check(constituency: str, parameter: Dict) -> str:
    num1_candidate_status = candidate(constituency, get_text(parameter, 'num1_directShare'))
    num2_candidate_status = candidate(constituency, get_text(parameter, 'num2_directShare'))

    region_prefix_status = 'ok'
    if 'title' in parameter.keys():
        region_prefix_status = correct_region_prefix(parameter['title'])

    statuses = [num1_candidate_status, num2_candidate_status, region_prefix_status]
    if any([status == 'critical' for status in statuses]):
        return 'critical'
    return 'ok'


def get_text(parameter: Dict, col: str) -> str:
    if col in parameter.keys():
        return parameter[col]
    return ''


def correct_region_prefix(title: str) -> str:
    prefixes = ['Wahlkreis', 'Gemeinde', 'Stadt', 'stadt']
    if any([prefix in title for prefix in prefixes]):
        return 'ok'
    return 'critical'


def candidate(constituency: str, text: str) -> str:
    if 'XXXX' in text:
        logger.error('Invalid candidate name in {} article'.format(constituency))
        return 'critical'
    return 'ok'
