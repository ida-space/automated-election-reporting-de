from wahlbot.Template import Template
import wahlbot.results as results
import wahlbot.assess as assess
from wahlbot.nlp import grammar_check, format_params
from typing import Dict, List
from datetime import datetime
import pytz

import logging
logger = logging.getLogger('wahlbot')


class Page:

    def __init__(self, consituency, data, background_info, level: str):
        self.constituency = consituency
        self.process_data(data)
        self.setup_general_parameter(data, level)
        self.process_background_info(background_info)

    def process_data(self, data):
        data = results.clean_data(data)
        self.listShare, self.directShare = results.split_data_by_votetype(data)

    def setup_general_parameter(self, data, level: str):
        self.timestamp = self.generate_timestamp()
        self.parameter = results.get_general_parameter(data, prefix='')
        self.parameter['level'] = level
        self.parameter['time'] = self.generate_timestamp(format='time')

    def add_state_parameter(self, state_res):
        self.parameter.update(state_res)

    def process_background_info(self, info):
        self.constituency_info = info.get_segmentation(self.parameter['constituency'])
        if hasattr(info, 'extras'):
            self.special_info = info.get_extra_info(self.constituency)
        else:
            self.special_info = ''

    def update_parameter(self, vote_type: str, prefix: str = ''):
        assert vote_type in ['listShare', 'directShare'], 'vote_type must be eiter listShare or directShare'
        if vote_type == 'listShare':
            listShare_results = results.get_results(self.listShare)
            self.parameter.update(results.results2parameter(listShare_results, prefix=prefix))
            overview = results.text_overview(self.listShare, exclude=[self.parameter[prefix + 'num1_party'],
                                                                      self.parameter[prefix + 'num2_party']])
            self.parameter.update({prefix + 'overview': overview})

            listShare_results_preelection = results.get_results(self.listShare, preelection=True)
            self.parameter.update(results.results2parameter(listShare_results_preelection, prefix=prefix + '2016_'))

            self.parameter.update(results.get_biggest_differences(self.listShare))

        if vote_type == 'directShare':
            directShare_results = results.get_results(self.directShare)
            self.parameter.update(results.results2parameter(directShare_results, prefix=prefix))

            directShare_results_preelection = results.get_results(self.directShare, preelection=True)
            self.parameter.update(results.results2parameter(directShare_results_preelection, prefix=prefix + '2016_'))

    def assessment(self, level: str = '', prefix: str = '', status: str = 'final'):
        self.parameter.update(assess.num1_results(self.parameter, prefix, status))
        self.parameter.update(assess.num2_results(self.parameter, prefix, status))
        self.parameter.update(assess.turnout(self.parameter))
        self.parameter.update(assess.state_differences(self.parameter))
        self.parameter.update(assess.state_comparison(self.parameter))
        self.parameter.update(assess.biggest_differences(self.parameter, status))
        if level == 'constituency':
            self.parameter.update(assess.list_direct_share_differences(self.parameter))
            self.parameter.update(assess.preelection_differences(self.parameter))
            self.parameter.update(assess.special_information(self.parameter, self.special_info))
            self.parameter.update(assess.candidate_information(self.parameter))

    def write(self, text_modules, article_template):
        template = Template(text_modules, article_template)
        page_elements = template.get_unique_variables()

        for template_name in page_elements:
            if template_name not in template.get_keys():
                continue
            element_template = template.get_text_module(template_name)
            process_steps = template.get_processing(template_name)
            text = element_template.substitute(self.parameter)

            if process_steps:
                text = grammar_check(text, process_steps, self.parameter)

            setattr(self, template_name, text)

        self.page_parameter = self.get_page_parameter(page_elements)
        return template.page.substitute(self.page_parameter)

    def get_page_parameter(self, parameter_list: List[str]) -> Dict[str, str]:
        parameter = {}
        for elem in parameter_list:
            parameter[elem] = getattr(self, elem)
        return parameter

    def format_parameter(self):
        self.parameter = format_params(self.parameter)

    def set_candidate_results(self, params):
        num1_candidate = self.get_party_candidate_info(params['direct_num1_party'], 'num1_')
        num2_candidate = self.get_party_candidate_info(params['direct_num2_party'], 'num2_')
        return {**num1_candidate, **num2_candidate}

    def get_party_candidate_info(self, party, prefix):
        if party in self.candidates.keys():
            return {prefix + 'candidate': self.candidates[party].name,
                    prefix + 'gender': self.candidates[party].gender,
                    prefix + 'candidate_info': self.candidates[party].info}
        else:
            return {prefix + 'candidate': 'XXXX', prefix + 'gender': '', prefix + 'candidate_info': 'XXXX'}

    def update_candidate_results(self, info):
        self.candidates = info.get_candidates(self.constituency)
        self.parameter.update(self.set_candidate_results(self.parameter))

    def generate_timestamp(self, format='full'):
        '''generate a web time timestamp'''
        now = datetime.now(pytz.timezone('CET'))
        if format == 'time':
            return now.strftime('%H:%M')
        return now.strftime("%Y-%m-%dT%H:%M:%S.000+02:00")
