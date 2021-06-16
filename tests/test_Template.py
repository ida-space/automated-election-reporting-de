from wahlbot.Template import Template
import unittest
import string


class TestTemplate(unittest.TestCase):

    def setUp(self):
        self.template = Template()

    def test_get_unique_variables(self):
        self.template.page = string.Template("""<Text>Test 1 ${test1}:</Text>
                                                <Text>Test 2 ${test2}</Text>
                                                <Text>Test 1 ${test1}</Text>""")
        variables = ['test1', 'test2']
        self.assertCountEqual(variables, self.template.get_unique_variables())
