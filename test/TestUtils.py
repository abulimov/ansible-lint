import unittest

import ansiblelint.utils as utils


class TestUtils(unittest.TestCase):

    def test_tokenize_blank(self):
        (cmd, args, kwargs) = utils.tokenize("")
        self.assertEquals(cmd, '')
        self.assertEquals(args, [])
        self.assertEquals(kwargs, {})


    def test_tokenize_single_word(self):
        (cmd, args, kwargs) = utils.tokenize("vars:")
        self.assertEquals(cmd, "vars")

    def test_tokenize_string_module_and_arg(self):
        (cmd, args, kwargs) = utils.tokenize("hello: a=1")
        self.assertEquals(cmd, "hello")
        self.assertEquals(kwargs, {"a": "1"})

    def test_tokenize_strips_action(self):
        (cmd, args, kwargs) = utils.tokenize("action: hello a=1")
        self.assertEquals(cmd, "hello")
        self.assertEquals(args, [])
        self.assertEquals(kwargs, {"a": "1"})

    def test_tokenize_more_than_one_arg(self):
        (cmd, args, kwargs) = utils.tokenize("action: whatever bobbins x=y z=x c=3")
        self.assertEquals(cmd, "whatever")
        self.assertEquals(args[0], "bobbins")
        self.assertEquals(kwargs, {'x': 'y', 'z': 'x', 'c': '3'})

    def test_tokenize_command_with_args(self):
        (cmd, args, kwargs) = utils.tokenize("action: command chdir=wxy creates=zyx tar xzf zyx.tgz")
        self.assertEquals(cmd, "command")
        self.assertEquals(args[0], "tar")
        self.assertEquals(args[1], "xzf")
        self.assertEquals(args[2], "zyx.tgz")
        self.assertEquals(kwargs, {'chdir': 'wxy', 'creates': 'zyx'})

    def test_normalize_simple_command(self):
        task1 = dict(name="hello", action="command chdir=abc echo hello world")
        task2 = dict(name="hello", command="chdir=abc echo hello world")
        self.assertEquals(utils.normalize_task(task1), utils.normalize_task(task2))

    def test_normalize_complex_command(self):
        task1 = dict(name="hello", action={'module': 'ec2', 'region': 'us-east1', 'etc': 'whatever'})
        task2 = dict(name="hello", ec2={'region': 'us-east1', 'etc': 'whatever'})
        task3 = dict(name="hello", ec2="region=us-east1 etc=whatever")
        task4 = dict(name="hello", action="ec2 region=us-east1 etc=whatever")
        self.assertEquals(utils.normalize_task(task1), utils.normalize_task(task2))
        self.assertEquals(utils.normalize_task(task2), utils.normalize_task(task3))
        self.assertEquals(utils.normalize_task(task3), utils.normalize_task(task4))

    def test_normalize_task_is_idempotent(self):
        tasks = list()
        tasks.append(dict(name="hello", action={'module': 'ec2', 'region': 'us-east1', 'etc': 'whatever'}))
        tasks.append(dict(name="hello", ec2={'region': 'us-east1', 'etc': 'whatever'}))
        tasks.append(dict(name="hello", ec2="region=us-east1 etc=whatever"))
        tasks.append(dict(name="hello", action="ec2 region=us-east1 etc=whatever"))
        for task in tasks:
            normalized_task = utils.normalize_task(task)
            self.assertEquals(normalized_task, utils.normalize_task(normalized_task))
