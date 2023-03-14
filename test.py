# Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
#
# This file is part of ConsoleCapture.
#
# ConsoleCapture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ConsoleCapture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ConsoleCapture. If not, see <http://www.gnu.org/licenses/>

from selenium import webdriver
from selenium.common import exceptions as selenium
from selenium.webdriver.common.by import By

import os
import sys
import time
import unittest

sys.path.append(os.path.dirname(__file__))
print(os.path.dirname(__file__))

from PythonUtils.testdata import TestData
from console_capture import captureConsole

class TestCase(type):
    __testCaseList = []

    @classmethod
    def loadTests(metacls, loader, tests, pattern):
        suite = unittest.TestSuite()
        for cls in metacls.__testCaseList:
            tests = loader.loadTestsFromTestCase(cls)
            suite.addTests(tests)
        return suite

    def __new__(metacls, *args):
        cls = super().__new__(metacls, *args)
        metacls.__testCaseList += [cls]
        return cls

def load_tests(loader, tests, pattern):
    return TestCase.loadTests(loader, tests, pattern)

class BrowserTestCase(unittest.TestCase):
    index = '''<html>
    <head>
        <meta charset='utf-8' />
        <title>Test{}</title>
    </head>
    <body>
        <p id="test">Click</p>
        {}
    </body>
</html>'''

    @classmethod
    def setUpClass(cls):
        cls.baseDir = os.path.dirname(os.path.abspath(__file__))

        cls.browser = webdriver.Firefox()
        captureConsole(cls.browser, os.path.join(cls.baseDir, 'dist/console_capture.xpi'))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()

    def setUp(self):
        self.browser = self.__class__.browser

    def tearDown(self):
        os.remove(os.path.join(self.__class__.baseDir, 'test/test_index.html'))
        try:
            os.remove(os.path.join(self.__class__.baseDir, 'test/test_script.js'))
        except:
            pass

    def getIndex(self, script='', title=''):
        if len(title) != 0:
            title = ' <' + title + '>'

        indexFilePath = os.path.join(self.__class__.baseDir, 'test/test_index.html')
        with open(indexFilePath, 'w') as indexFile:
            indexFile.write(self.__class__.index.format(title, script))
        self.url = 'file://' + indexFilePath
        self.browser.get(self.url)

class BaseTest(BrowserTestCase):
    caller = ''
    fileName = None
    lineNumber = 1
    columnNumber = 1

    def checkArguments(self, capturedArguments, expectedArguments):
        self.assertEqual(len(capturedArguments), len(expectedArguments))
        for capturedArgument, expectedArgument in zip(capturedArguments, expectedArguments):
            self.assertEqual(type(capturedArgument), type(expectedArgument))
            if isinstance(expectedArgument, dict):
                for k in expectedArgument:
                    self.assertIn(k, capturedArgument)
                    self.assertEqual(capturedArgument[k], expectedArgument[k])
            else:
                self.assertEqual(capturedArgument, expectedArgument)

    def checkCapture(self, callee, beforeTime, afterTime):
        capture = self.browser.consoleCapture()
        self.assertEqual(len(capture), 1)

        self.assertEqual(capture[0]['callee'], callee)
        self.assertTrue((beforeTime - 0.001 <= capture[0]['time']/1000) and (capture[0]['time']/1000 <= afterTime + 0.001))
        self.assertEqual(capture[0]['caller'], self.__class__.caller)
        self.assertEqual(capture[0]['fileName'], 'file://' + os.path.join(self.__class__.baseDir, self.__class__.fileName) if self.__class__.fileName is not None else self.url)
        self.assertEqual(capture[0]['lineNumber'], str(self.__class__.lineNumber))
        self.assertEqual(capture[0]['columnNumber'], str(self.__class__.columnNumber))

        return capture[0]

    @TestData([
        {'title': 'log1',   'function': 'log',   'data': ['OK']                        },
        {'title': 'warn1',  'function': 'warn',  'data': ['OK']                        },
        {'title': 'error1', 'function': 'error', 'data': ['OK']                        },
        {'title': 'log2',   'function': 'log',   'data': ['log1', 'log2']              },
        {'title': 'warn2',  'function': 'warn',  'data': ['warn1', 'warn2']            },
        {'title': 'error2', 'function': 'error', 'data': ['error1', 'error2']          },
        {'title': 'log3',   'function': 'log',   'data': ['log1', 'log2', 'log3']      },
        {'title': 'warn3',  'function': 'warn',  'data': ['warn1', 'warn2', 'warn3']   },
        {'title': 'error3', 'function': 'error', 'data': ['error1', 'error2', 'error3']},
    ])
    def testTextMessages(self, function, data, title=''):
        result = data
        data = ['"' + datum + '"' for datum in data]

        self.init(data, function=function, title=title)

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(data, function=function)
        afterTime = time.time()

        capture = self.checkCapture(function, beforeTime, afterTime)
        self.checkArguments(capture['arguments'], result)

    def testNull(self):
        self.init(['null'], title='log null')

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(['null'])
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], ['null'])

    def testUndefined(self):
        self.init(['undefined'], title='log undefined')

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(['undefined'])
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], ['undefined'])

    @TestData([
        {'title': 'log 0',           'data': [0]      },
        {'title': 'log 1',           'data': [1]      },
        {'title': 'log -1',          'data': [-1]     },
        {'title': 'log 0.5',         'data': [0.5]    },
        {'title': 'log 1.5',         'data': [1.5]    },
        {'title': 'log 1000.5',      'data': [1000.5] },
        {'title': 'log -0.5',        'data': [-0.5]   },
        {'title': 'log -1.5',        'data': [-1.5]   },
        {'title': 'log -1000.5',     'data': [-1000.5]},
        {'title': 'log [1, 2]',      'data': [1, 2]   },
        {'title': 'log [1, 2, 3]',   'data': [1, 2, 3]},
    ])
    def testNumbers(self, data, title=''):
        result = data
        data = [str(datum) for datum in data]

        self.init(data, title=title)

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(data)
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], result)

    @TestData([
        {'title': 'log 1+1',                   'formula': ['1+1'],                     'result': [2]      },
        {'title': 'log 1-1',                   'formula': ['1-1'],                     'result': [0]      },
        {'title': 'log 1*1',                   'formula': ['1*1'],                     'result': [1]      },
        {'title': 'log 1/1',                   'formula': ['1/1'],                     'result': [1]      },
        # TODO {'title': 'log 1/0',                   'formula': ['1./0.'],                   'result': [1]      },
        # TODO {'title': 'log 0/0',                   'formula': ['0./0.'],                   'result': [1]      },
        {'title': 'log [0 + 1, 1 + 1]',        'formula': ['0 + 1', '1 + 1'],          'result': [1, 2]   },
        {'title': 'log [0 + 1, 1 + 1, 1 + 2]', 'formula': ['0 + 1', '1 + 1', '1 + 2'], 'result': [1, 2, 3]},
    ])
    def testFormulae(self, formula, result, title=''):
        self.init(formula, title=title)

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(formula)
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], result)

    @TestData([
        {'title': 'log []',                         'formula': ['[]'],                         'result': [[]]                        },
        {'title': 'log [1]',                        'formula': ['[1]'],                        'result': [[1]]                       },
        {'title': 'log [1, 2]',                     'formula': ['[1, 2]'],                     'result': [[1, 2]]                    },
        {'title': 'log [1], [2]',                   'formula': ['[1], [2]'],                   'result': [[1], [2]]                  },
        {'title': 'log [11, 12], [21, 22]',         'formula': ['[11, 12], [21, 22]'],         'result': [[11, 12], [21, 22]]        },
        {'title': 'log ["1"]',                      'formula': ['["1"]'],                      'result': [['1']]                     },
        {'title': 'log ["1", "2"]',                 'formula': ['["1", "2"]'],                 'result': [['1', '2']]                },
        {'title': 'log ["1"], ["2"]',               'formula': ['["1"], ["2"]'],               'result': [['1'], ['2']]              },
        {'title': 'log ["11", "12"], ["21", "22"]', 'formula': ['["11", "12"], ["21", "22"]'], 'result': [['11', '12'], ['21', '22']]},
    ])
    def testArrays(self, formula, result, title=''):
        self.init(formula, title=title)

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(formula)
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], result)

    @TestData([
        {'title': 'log {}',                                         'formula': ['{}'],                                         'result': [{}]                                                },
        {'title': 'log {a: 1}',                                     'formula': ['{a: 1}'],                                     'result': [{'a': 1}]                                          },
        {'title': 'log {a: 1, b: 2}',                               'formula': ['{a: 1, b: 2}'],                               'result': [{'a': 1, 'b': 2}]                                  },
        {'title': 'log {a: 1}, {b: 2}',                             'formula': ['{a: 1}, {b: 2}'],                             'result': [{'a' : 1}, {'b': 2}]                               },
        {'title': 'log {aa: 11, ab: 12}, {ba: 21, bb: 22}',         'formula': ['{aa: 11, ab: 12}, {ba: 21, bb: 22}'],         'result': [{'aa': 11, 'ab': 12}, {'ba': 21, 'bb': 22}]        },
        {'title': 'log {a: "1"}',                                   'formula': ['{a: "1"}'],                                   'result': [{'a': '1'}]                                        },
        {'title': 'log {a: "1", b: "2"}',                           'formula': ['{a: "1", b: "2"}'],                           'result': [{'a': '1', 'b': '2'}]                              },
        {'title': 'log {a: "1"}, {b: "2"}',                         'formula': ['{a: "1"}, {b: "2"}'],                         'result': [{'a' : '1'}, {'b': '2'}]                           },
        {'title': 'log {aa: "11", ab: "12"}, {ba: "21", bb: "22"}', 'formula': ['{aa: "11", ab: "12"}, {ba: "21", bb: "22"}'], 'result': [{'aa': '11', 'ab': '12'}, {'ba': '21', 'bb': '22'}]},
    ])
    def testObjects(self, formula, result, title=''):
        self.init(formula, title=title)

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(formula)
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], result)

    @TestData([
        {'title': 'log lambda()',              'formula': ['() => {return 0;}'],                            'result': ['function()']  },
        {'title': 'log lambda(x)',             'formula': ['(x) => {return x;}'],                           'result': ['function()']  },
        {'title': 'log function()',            'formula': ['function() {return 0;}'],                       'result': ['function()']  },
        {'title': 'log function(x)',           'formula': ['function(x) {return x;}'],                      'result': ['function()']  },
        {'title': 'log lambda(x), function()', 'formula': ['(x) => x', 'function() {return 0;}'],           'result': ['function()']*2},
        {'title': 'log function(x), lambda()', 'formula': ['function(x) {return x;}', '() => {return 0;}'], 'result': ['function()']*2},
    ])
    def testFunctions(self, formula, result, title=''):
        self.init(formula, title=title)

        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(formula)
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], result)

    @TestData([0, 1, 10])
    def testElement(self, depth):
        self.init(['document.body'], title='body')

        self.browser.consoleCapture.depth = depth
        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(['document.body'])
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], [self.browser.find_element(By.TAG_NAME, 'body')])

    @TestData([
        {'title': 'log keydown',        'depth': 0, 'data': ['new KeyboardEvent("keydown", {"key": "X"})'],                                             'result': ['[object KeyboardEvent]'                                                                                                ]},
        {'title': 'log keyup',          'depth': 0, 'data': ['new KeyboardEvent("keyup",   {"key": "X"})'],                                             'result': ['[object KeyboardEvent]'                                                                                                ]},
        {'title': 'log keydown, keyup', 'depth': 0, 'data': ['new KeyboardEvent("keydown", {"key": "X"})', 'new KeyboardEvent("keyup", {"key": "X"})'], 'result': ['[object KeyboardEvent]', '[object KeyboardEvent]'                                                                      ]},
        {'title': 'log keydown',        'depth': 1, 'data': ['new KeyboardEvent("keydown", {"key": "X"})'],                                             'result': [{'typeName': "KeyboardEvent", 'type': "keydown", 'key': "X"}                                                            ]},
        {'title': 'log keyup',          'depth': 1, 'data': ['new KeyboardEvent("keyup",   {"key": "X"})'],                                             'result': [{'typeName': "KeyboardEvent", 'type': "keyup",   'key': "X"}                                                            ]},
        {'title': 'log keydown, keyup', 'depth': 1, 'data': ['new KeyboardEvent("keydown", {"key": "X"})', 'new KeyboardEvent("keyup", {"key": "X"})'], 'result': [{'typeName': "KeyboardEvent", 'type': "keydown", 'key': "X"}, {'typeName': "KeyboardEvent", 'type': "keyup", 'key': "X"}]},
    ])
    def testComplexObjects(self, depth, data, result, title=''):
        self.init(data, title=title)

        self.browser.consoleCapture.depth = depth
        del self.browser.consoleCapture
        self.assertEqual(self.browser.consoleCapture(), [])

        beforeTime = time.time()
        self.action(data)
        afterTime = time.time()

        capture = self.checkCapture('log', beforeTime, afterTime)
        self.checkArguments(capture['arguments'], result)

class ExecuteScriptTest(BaseTest, metaclass=TestCase):
    lineNumber = 2
    columnNumber = 15

    def init(self, *args, **kwargs):
        title = kwargs['title'] if 'title' in kwargs.keys() else ''

        self.getIndex(title=title)

    def action(self, *args, **kwargs):
        data = args[0]
        function = kwargs['function'] if 'function' in kwargs.keys() else 'log'

        self.browser.execute_script('console.{}({});'.format(function, ', '.join(data)))

class ExecuteFunctionTest(BaseTest, metaclass=TestCase):
    javascript = """<script type="text/javascript">
        function fun() {{
            {}
        }}
    </script>"""
    caller = 'fun'
    lineNumber = 10
    columnNumber = 21

    def init(self, *args, **kwargs):
        data = args[0]
        function = kwargs['function'] if 'function' in kwargs.keys() else 'log'
        title = kwargs['title'] if 'title' in kwargs.keys() else ''

        self.getIndex(self.__class__.javascript.format('console.{}({});'.format(function, ', '.join(data))), title)

    def action(self, *args, **kwargs):
        self.browser.execute_script('fun();')

class ExecuteFileTest(BaseTest, metaclass=TestCase):
    caller = 'fun'
    fileName = 'test/test_script.js'
    lineNumber = 2
    columnNumber = 25

    def init(self, *args, **kwargs):
        data = args[0]
        function = kwargs['function'] if 'function' in kwargs.keys() else 'log'
        title = kwargs['title'] if 'title' in kwargs.keys() else ''

        javascriptFilePath = os.path.join(self.__class__.baseDir, self.__class__.fileName)
        with open(javascriptFilePath, 'w') as javascriptFile:
            javascriptFile.write("""function fun() {{
                {}
            }}""".format('console.{}({});'.format(function, ', '.join(data))))

        self.getIndex('<script src="test_script.js" type="text/javascript"></script>', title)

    def action(self, *args, **kwargs):
        self.browser.execute_script('fun();')

class ClickTest(BaseTest, metaclass=TestCase):
    javascript = """<script>
        document.getElementById('test').addEventListener('click', () => {{{}}});
    </script>"""
    lineNumber = 9
    columnNumber = 82

    def init(self, *args, **kwargs):
        data = args[0]
        function = kwargs['function'] if 'function' in kwargs.keys() else 'log'
        title = kwargs['title'] if 'title' in kwargs.keys() else ''

        self.getIndex(self.__class__.javascript.format('console.{}({});'.format(function, ', '.join(data))), title)

    def action(self, *args, **kwargs):
        self.browser.find_element(By.ID, 'test').click()

class ClickFunctionTest(BaseTest, metaclass=TestCase):
    javascript = """<script type="text/javascript">
        function clickEvent() {{
            {}
        }}
        document.getElementById('test').addEventListener('click', clickEvent);
    </script>"""
    caller = 'clickEvent'
    lineNumber = 10
    columnNumber = 21

    def init(self, *args, **kwargs):
        data = args[0]
        function = kwargs['function'] if 'function' in kwargs.keys() else 'log'
        title = kwargs['title'] if 'title' in kwargs.keys() else ''

        self.getIndex(self.__class__.javascript.format('console.{}({});'.format(function, ', '.join(data))), title)

    def action(self, *args, **kwargs):
        self.browser.find_element(By.ID, 'test').click()

class ClickFileTest(BaseTest, metaclass=TestCase):
    caller = 'clickEvent'
    fileName = 'test/test_script.js'
    lineNumber = 2
    columnNumber = 25

    def init(self, *args, **kwargs):
        data = args[0]
        function = kwargs['function'] if 'function' in kwargs.keys() else 'log'
        title = kwargs['title'] if 'title' in kwargs.keys() else ''

        javascriptFilePath = os.path.join(self.__class__.baseDir, self.__class__.fileName)
        with open(javascriptFilePath, 'w') as javascriptFile:
            javascriptFile.write("""function clickEvent() {{
                {}
            }}""".format('console.{}({});'.format(function, ', '.join(data))))

        self.getIndex("""<script src="test_script.js" type="text/javascript"></script>
        <script>
            document.getElementById('test').addEventListener('click', clickEvent);
        </script>""", title)

    def action(self, *args, **kwargs):
        self.browser.find_element(By.ID, 'test').click()

class DepthTest(BrowserTestCase, metaclass=TestCase):
    @TestData([1, 10])
    def testSetDepth(self, depth):
        self.getIndex()
        self.assertEqual(self.browser.consoleCapture.depth, 0)

        self.browser.consoleCapture.depth = depth
        self.assertEqual(self.browser.consoleCapture.depth, depth)

        self.browser.consoleCapture.depth = 0
        self.assertEqual(self.browser.consoleCapture.depth, 0)

    @unittest.skip("Marionnette does not decode well the javascript errors")
    @TestData(['v'])
    def testInvalid(self, depth):
        self.getIndex()

        with self.assertRaises(NameError) as e:
            self.browser.consoleCapture.depth = depth
        self.assertEqual(e.exception.args[0], f"{depth} is not defined")

    @unittest.skip("Marionnette does not decode well the javascript errors")
    @TestData(['true', 'false', 'null', 'undefined', '"str"', '[]', '{}'])
    def testInvalidType(self, depth):
        self.getIndex()
        #time.sleep(60)

        with self.assertRaises(TypeError) as e:
            self.browser.consoleCapture.depth = depth
        self.assertEqual(e.exception.args[0], "Capure depth must be an integer")

    @unittest.skip("Marionnette does not decode well the javascript errors")
    @TestData([-1, -10])
    def testInvalidRange(self, depth):
        self.getIndex()

        with self.assertRaises(ValueError) as e:
            self.browser.consoleCapture.depth = depth
        self.assertEqual(e.exception.args[0], "Capure depth must be non-negative")

if __name__ == '__main__':
    unittest.main(verbosity=2)
