from typing import Dict
import pandas as pd
from dataclasses import dataclass
import collections


@dataclass
class Candidate:
    name: str
    surname: str
    gender: str
    party: str
    info: str


Info = collections.namedtuple('Info', 'text')


class BackgroundInfo:

    def __init__(self):
        self.load_data()

    def load_data(self, segmentation_path: str = './data/Einteilung.csv',
                  candidates_path: str = './data/Direktkandidaten.csv',
                  extras_path: str = './data/Besonderheiten.csv'):
        self.segmentation = pd.read_csv(segmentation_path, sep=',', index_col=0)
        self.candidates = pd.read_csv(candidates_path, header=[0, 1], index_col=1)
        del self.candidates[1]
        self.extras = pd.read_csv(extras_path)

    def transform_df(self, df):
        data = df.transpose()
        index = pd.MultiIndex.from_tuples(data.index)
        data = data.reindex(index)
        data = data.unstack()
        return data.droplevel(0, axis=1)

    def get_segmentation(self, constituency):
        return self.segmentation.loc[self.segmentation['Landtagswahlkreis'] == constituency, 'text'].values[0]

    def get_extra_info(self, constituency):
        data = self.extras[self.extras['Wahlkreis'] == constituency]
        text = self.get_value(data, 'template')
        return Info(text)

    def get_value(self, data, col):
        value = None
        if not data[col].isnull().any():
            value = data[col].values[0]
        return value

    def get_candidate_gender(self, data):
        gender = data['Geschlecht']
        if not gender:
            gender = 'm'
        return gender

    def get_candidate_info(self, data):
        info = None
        if str(data['Besonderheiten']) != 'nan':
            info = data['Besonderheiten']
        return info

    def get_default_candidate(self, row):
        party = row['Partei']
        return Candidate(name='XXXX', surname='XXXX', party=party, gender='XXXX', info='XXXX')

    def create_candidates(self, row):
        name = str(row['Name'])
        if name == 'nan' or name == 'None':
            return self.get_default_candidate(row)
        surname = name.split()[-1]
        gender = self.get_candidate_gender(row)
        info = self.get_candidate_info(row)
        return Candidate(name=name, surname=surname, party=row['Partei'], gender=gender, info=info)

    def get_candidates(self, constituency: str) -> Dict:
        constituency_candidates = self.candidates[self.candidates.index == constituency]
        constituency_candidates = self.transform_df(constituency_candidates)
        return constituency_candidates.apply(self.create_candidates, axis=1).to_dict()
