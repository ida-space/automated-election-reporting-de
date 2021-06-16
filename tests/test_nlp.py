from textblob_de import TextBlobDE as TextBlob
from wahlbot import nlp
import unittest


class TestNLP(unittest.TestCase):

    def setUp(self):
        pass

    def test_list2enumeration(self):
        l1 = ['apple', 'banana', 'orange']
        target1 = 'apple, banana und orange'
        self.assertEqual(nlp.list2enumeration(l1), target1)

        l2 = ['1', '2']
        target2 = '1 und 2'
        self.assertEqual(nlp.list2enumeration(l2), target2)

    def test_list2enumeration_error(self):
        self.assertRaises(AssertionError, nlp.list2enumeration, [])
        self.assertRaises(AssertionError, nlp.list2enumeration, ['1'])

    def test_create_link(self):
        target = '&lt;a href="" externalId="artikel-wahlkreis-10"&gt;Wahlkreis 10 Magdeburg I&lt;/a&gt;'
        self.assertEqual(nlp.create_link('Wahlkreis 10 Magdeburg I', 'artikel-wahlkreis-10'), target)

    def test_list2link_enumeration(self):
        word_list = ['Wahlkreis 1', 'Wahlkreis 2', 'Wahlkreis 3']
        link_list = ['wk-1', 'wk-2', 'wk-3']
        target = '&lt;a href="" externalId="wk-1"&gt;Wahlkreis 1&lt;/a&gt;, '\
                 '&lt;a href="" externalId="wk-2"&gt;Wahlkreis 2&lt;/a&gt; '\
                 'und &lt;a href="" externalId="wk-3"&gt;Wahlkreis 3&lt;/a&gt;'
        self.assertEqual(nlp.list2link_enumeration(word_list, link_list), target)

    def test_list2link_enumeration_error(self):
        self.assertRaises(AssertionError, nlp.list2link_enumeration, ['elem1', 'elem2'], ['link 1'])

    def test_singularize_word_after_1(self):
        text = TextBlob('Die Partei verbessert ihr Ergebnis um 4 Prozentpunkte.')
        self.assertEqual(nlp.singularize_noun_after_1(text), text)

        text2 = TextBlob('und ein Prozent der Stimmen sind ungültig.')
        self.assertEqual(nlp.singularize_noun_after_1(text2), text2)

        text3 = TextBlob('Ein knapper Verlust von ein Prozentpunkten.')
        target3 = TextBlob('Ein knapper Verlust von einem Prozentpunkt.')
        self.assertEqual(nlp.singularize_noun_after_1(text3), target3)

        text4 = TextBlob('legt um einen Prozentpunkte zu.')
        target4 = TextBlob('legt um einen Prozentpunkt zu.')
        self.assertEqual(nlp.singularize_noun_after_1(text4), target4)

    def test_pluralize_verb_dependent_on_party(self):
        text = TextBlob('Auf Platz zwei folgt die CDU.')
        self.assertEqual(nlp.pluralize_verb_dependent_on_party(text), text)

        text2 = TextBlob('Auf Platz zwei folgt die Grüne.')
        target2 = TextBlob('Auf Platz zwei folgen die Grünen.')
        self.assertEqual(nlp.pluralize_verb_dependent_on_party(text2), target2)

        text3 = TextBlob('Die Freie Wähler holt 17 Prozent und besiegt die FDP. Grüne kommt auf Platz 2.')
        target3 = TextBlob('Die Freien Wähler holen 17 Prozent und besiegen die FDP. Grüne kommen auf Platz 2.')
        self.assertEqual(nlp.pluralize_verb_dependent_on_party(text3), target3)

        text4 = TextBlob('Grüne kommt auf Platz 2')
        target4 = TextBlob('Grüne kommen auf Platz 2')
        self.assertEqual(nlp.pluralize_verb_dependent_on_party(text4), target4)

        text5 = TextBlob('Damit ist die Freie Wähler zugleich größter Wahlgewinner.')
        target5 = TextBlob('Damit sind die Freien Wähler zugleich größter Wahlgewinner.')
        self.assertEqual(nlp.pluralize_verb_dependent_on_party(text5), target5)

    def test_get_previous_word(self):
        text = 'test text to get The previous word.'
        self.assertEqual(nlp.get_previous_word(text, 'text'), 'test')
        self.assertEqual(nlp.get_previous_word(text, 'previous'), 'the')
        self.assertEqual(nlp.get_previous_word(text, 'word'), 'previous')
        self.assertEqual(nlp.get_previous_word(text, 'test'), '')

    def test_format_parameter(self):
        parameter = {'str': 'do not change', 'num1': 27.0, 'float': 23.9, 'num2': 1.0, 'num3': 9}
        target = {'str': 'do not change', 'num1': '27', 'float': '23,9', 'num2': 'einen', 'num3': 'neun'}
        self.assertEqual(nlp.format_params(parameter), target)

    def test_format_number(self):
        self.assertEqual(nlp.format_number(21.5), '21,5')
        self.assertEqual(nlp.format_number(0.9), '0,9')
        self.assertEqual(nlp.format_number(37.0), '37')
        self.assertEqual(nlp.format_number(3.0), 'drei')

    def test_pluralize_party(self):
        text = 'Die CDU (23,5 Prozent) führt vor der AfD.'
        self.assertEqual(nlp.pluralize_party(text), text)

        text = 'Die Grüne gewinnen.'
        target = 'Die Grünen gewinnen.'
        self.assertEqual(nlp.pluralize_party(text), target)

        text = 'Die Freie Wähler verlieren gegen die Linke.'
        target = 'Die Freien Wähler verlieren gegen die Linken.'
        self.assertEqual(nlp.pluralize_party(text), target)

    def test_pluralize_party_arg(self):
        text = 'Die Linke führen.'
        self.assertEqual(nlp.pluralize_party(text, 'CDU'), text)
        self.assertEqual(nlp.pluralize_party(text, 'Grüne'), text)
        self.assertEqual(nlp.pluralize_party(text, 'Linke'), 'Die Linken führen.')

    def test_capitalize_first_word(self):
        text = 'zwei Prozent der Stimmen sind ungültig.'
        target = 'Zwei Prozent der Stimmen sind ungültig.'
        self.assertEqual(nlp.capitalize_first_word(text), target)
        self.assertEqual(nlp.capitalize_first_word(target), target)
