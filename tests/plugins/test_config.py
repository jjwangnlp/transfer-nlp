import unittest

from transfer_nlp.plugins.config import register_plugin, ExperimentConfig, UnconfiguredItemsException


@register_plugin
class Demo2:

    def __init__(self, simple_str: str):
        self.val = simple_str


@register_plugin
class Demo3:

    def __init__(self, simple_int: str):
        self.val = simple_int


@register_plugin
class Demo4:

    def __init__(self, simple_int: str, optional: int = None, optional2: int = 1):
        self.val = simple_int
        self.optional = optional
        self.optional2 = optional2


@register_plugin
class DemoDefaults:

    def __init__(self, simple_int: str, foo: int = 5, bar=10):
        self.val = simple_int
        self.foo = foo
        self.bar = bar


@register_plugin
class DemoComplexDefaults:

    def __init__(self, simple_int: str, demod: DemoDefaults = None):
        self.val = simple_int
        self.dd = demod


@register_plugin
class Demo:

    def __init__(self, demo2, demo3: Demo3):
        self.demo2 = demo2
        self.demo3 = demo3


@register_plugin
class DemoWithConfig:

    def __init__(self, demo2, simple_int: str, experiment_config):
        self.demo2 = demo2
        self.simple_int = simple_int
        self.experiment_config = experiment_config


class RegistryTest(unittest.TestCase):

    def test_child_injection(self):
        experiment = {
            'demo': {
                '_name': 'Demo',
            },
            'demo2': {
                '_name': 'Demo2'
            },
            'demo3': {
                '_name': 'Demo3'
            },
            'simple_str': 'dummy',
            'simple_int': 5
        }
        e = ExperimentConfig(experiment)

        self.assertTrue(isinstance(e['demo'], Demo))
        self.assertTrue(isinstance(e['demo2'], Demo2))
        self.assertTrue(isinstance(e['demo3'], Demo3))

        self.assertEqual(e['demo2'].val, 'dummy')
        self.assertEqual(e['demo3'].val, e['demo3'].val, 5)

    def test_child_named_injection(self):
        experiment = {
            'demo': {
                '_name': 'Demo',
                'demo3': '$demo3a'

            },
            'demo2': {
                '_name': 'Demo2'
            },
            'demo3': {
                '_name': 'Demo3'
            },
            'demo3a': {
                '_name': 'Demo3',
                'simple_int': '$simple_inta'
            },
            'simple_str': 'dummy',
            'simple_int': 5,
            'simple_inta': 6,
        }
        e = ExperimentConfig(experiment)

        self.assertTrue(isinstance(e['demo'], Demo))
        self.assertTrue(isinstance(e['demo2'], Demo2))
        self.assertTrue(isinstance(e['demo3'], Demo3))
        self.assertTrue(isinstance(e['demo3a'], Demo3))

        self.assertEqual(e['demo2'].val, 'dummy')
        self.assertEqual(e['demo3'].val, 5)
        self.assertEqual(e['demo3a'].val, 6)
        self.assertEqual(e['demo'].demo3.val, 6)

    def test_env(self):
        experiment = {
            'path': "$HOME/foo/bar",
            'data': {
                '_name': "Demo2",
                'simple_str': "$HOME/foo/bar/bis"
            }
        }
        e = ExperimentConfig(experiment, HOME='/tmp')
        self.assertEqual(e['path'], '/tmp/foo/bar')
        self.assertEqual(e['data'].val, '/tmp/foo/bar/bis')

    def test_literal_injection(self):
        experiment = {
            'demo2': {
                '_name': 'Demo2',
                'simple_str': 'dummy'
            },
            'demo3': {
                '_name': 'Demo3',
                'simple_int': 5
            }
        }
        e = ExperimentConfig(experiment)

        self.assertTrue(isinstance(e['demo2'], Demo2))
        self.assertTrue(isinstance(e['demo3'], Demo3))

        self.assertEqual(e['demo2'].val, 'dummy')
        self.assertEqual(e['demo3'].val, 5)

    def test_unconfigured(self):
        experiment = {
            'demo': {
                '_name': 'Demo',
            },
            'demo2': {
                '_name': 'Demo2',
            },
            'demo3': {
                '_name': 'Demo3',
            }
        }

        try:
            ExperimentConfig(experiment)
            self.fail()
        except UnconfiguredItemsException as e:
            self.assertEqual(3, len(e.items))
            self.assertEqual({'demo2', 'demo3'}, e.items['demo'])
            self.assertEqual({'simple_str'}, e.items['demo2'])
            self.assertEqual({'simple_int'}, e.items['demo3'])

    def test_defaults(self):
        experiment = {
            'demoa': {
                '_name': 'DemoDefaults',
                'simple_int': 0
            },
            'demob': {
                '_name': 'DemoDefaults',
                'simple_int': 1,
                'foo': 6
            },
            'democ': {
                '_name': 'DemoDefaults',
                'simple_int': 2,
                'bar': 6
            }
        }
        e = ExperimentConfig(experiment)

        self.assertTrue(isinstance(e['demoa'], DemoDefaults))
        self.assertTrue(isinstance(e['demob'], DemoDefaults))

        self.assertEqual(e['demoa'].val, 0)
        self.assertEqual(e['demoa'].foo, 5)
        self.assertEqual(e['demoa'].bar, 10)

        self.assertEqual(e['demob'].val, 1)
        self.assertEqual(e['demob'].foo, 6)
        self.assertEqual(e['demob'].bar, 10)

        self.assertEqual(e['democ'].val, 2)
        self.assertEqual(e['democ'].foo, 5)
        self.assertEqual(e['democ'].bar, 6)

    def test_complex_defaults(self):
        ### test that demod gets created first and then is used to create demo instead of the None default
        experiment = {
            'demo': {
                '_name': 'DemoComplexDefaults',
                'simple_int': 0
            },
            'demod': {
                '_name': 'DemoDefaults',
                'simple_int': 1,
                'foo': 6
            }
        }
        e = ExperimentConfig(experiment)

        self.assertTrue(isinstance(e['demo'], DemoComplexDefaults))
        self.assertTrue(isinstance(e['demod'], DemoDefaults))

        self.assertEqual(e['demod'].val, 1)
        self.assertEqual(e['demod'].foo, 6)
        self.assertEqual(e['demod'].bar, 10)

        self.assertEqual(e['demo'].val, 0)
        self.assertEqual(e['demo'].dd.val, 1)
        self.assertEqual(e['demo'].dd.foo, 6)
        self.assertEqual(e['demo'].dd.bar, 10)

    def test_none_default(self):
        experiment = {
            'demo4': {
                '_name': 'Demo4',
                'simple_int': 0
            },
            'demo4a': {
                '_name': 'Demo4',
                'simple_int': 0,
                'optional': 1
            },
            'demo4b': {
                '_name': 'Demo4',
                'simple_int': 0,
                'optional2': None
            }

        }

        e = ExperimentConfig(experiment)

        self.assertTrue(isinstance(e['demo4'], Demo4))
        self.assertTrue(isinstance(e['demo4a'], Demo4))

        self.assertEqual(e['demo4'].val, 0)
        self.assertEqual(e['demo4'].optional, None)
        self.assertEqual(e['demo4'].optional2, 1)
        self.assertEqual(e['demo4a'].val, 0)
        self.assertEqual(e['demo4b'].optional, None)
        self.assertEqual(e['demo4b'].optional2, None)

    def test_with_config(self):
        experiment = {
            'demo2': {
                '_name': 'Demo2'
            },
            'with_config': {
                '_name': 'DemoWithConfig'
            },
            'simple_str': 'dummy',
            'simple_int': 5
        }

        e = ExperimentConfig(experiment)

        d = e['with_config']
        self.assertEqual(5, d.simple_int)
        self.assertEqual('dummy', d.demo2.val)
        self.assertTrue(d.experiment_config is e)
        self.assertEqual({'demo2', 'with_config', 'simple_str', 'simple_int'}, e.factories.keys())
        self.assertEqual(5, e.factories['simple_int'].create())
        self.assertEqual('dummy', e.factories['simple_str'].create())

        d2 = e.factories['with_config'].create()
        self.assertEqual(5, d2.simple_int)
        self.assertEqual('dummy', d2.demo2.val)
        self.assertTrue(d2.experiment_config is e)
