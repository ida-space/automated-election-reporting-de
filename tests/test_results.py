import wahlbot.results as results
import pandas as pd
import unittest


class TestResults(unittest.TestCase):

    def setUp(self):
        data = pd.read_csv('./tests/testdata.csv', sep=',', index_col=None, encoding='latin')
        self.data = results.clean_data(data)
        self.listShare, self.directShare = results.split_data_by_votetype(self.data)

    def test_text_overview(self):
        target = 'CDU (36,1 Prozent), Linke (14,2 Prozent), SPD (9,5 Prozent) und Grüne (3,9 Prozent)'
        self.assertEqual(target, results.text_overview(self.listShare))

    def test_text_overview_exclude(self):
        target = 'CDU (36,1 Prozent), Linke (14,2 Prozent) und Grüne (3,9 Prozent)'
        self.assertEqual(target, results.text_overview(self.listShare, exclude=['SPD']))

        target = 'CDU (36,1 Prozent) und Linke (14,2 Prozent)'
        self.assertEqual(target, results.text_overview(self.listShare, exclude=['SPD', 'Grüne']))

    def test_result2parameter(self):
        position = results.Position('CDU', 31, -2)
        target = {'direct_num1_party': 'CDU', 'direct_num1_percent': 31, 'direct_num1_diff': -2}
        self.assertEqual(target, results.result2parameter(position, 1, 'direct_'))

        position = results.Position('FDP', 4.2, 0.9)
        target = {'list_num5_party': 'FDP', 'list_num5_percent': 4.2, 'list_num5_diff': 0.9}
        self.assertEqual(target, results.result2parameter(position, 5, 'list_'))

    def test_results2parameter(self):
        positions = [results.Position('CDU', 24.9, -6), results.Position('SPD', 22.0, 9)]
        target = {'direct_num1_party': 'CDU', 'direct_num1_percent': 24.9, 'direct_num1_diff': -6,
                  'direct_num2_party': 'SPD', 'direct_num2_percent': 22.0, 'direct_num2_diff': 9}
        self.assertEqual(target, results.results2parameter(positions, 'direct_'), target)

    def test_get_constituency(self):
        self.assertEqual('Testwahlkreis', results.get_constituency(self.data))

    def test_get_turnout(self):
        self.assertEqual(64.8, results.get_turnout(self.data))

    def test_get_no_voter(self):
        self.assertEqual('29.091', results.get_no_voter(self.data))

    def test_clean_data(self):
        parties = self.data['Partei'].unique()
        self.assertTrue('CDU' in parties)
        self.assertTrue('Linke' in parties)
        self.assertTrue('Grüne' in parties)
        self.assertTrue('Sonstige' not in parties)
        self.assertTrue('Tierschutzpartei' not in parties)
