
import unittest
from validate import Validate
from webob.multidict import MultiDict
from webob.exc import HTTPPreconditionFailed


class TestValidate(unittest.TestCase):

    def setUp(self):
        self.post = MultiDict([(u'check', u'a'), (u'foo', u'b'),
                (u'name', u'Bob')])

    def testAllowed(self):
        val = Validate(self.post)
        # Values 'a' or 'b' are allowed
        val.allowed('check', ['a', 'b'])
        # Value 'd' is not allowed
        self.assertRaises(HTTPPreconditionFailed, val.allowed, 'check', ['d'])

    def testOnly(self):
        val = Validate(self.post)
        # Only these parameters are acceptable
        val.only(['check', 'foo', 'name'])
        # 'name' is not acceptable
        self.assertRaises(HTTPPreconditionFailed, val.only, ['check', 'foo', 'last'])

    def testRequired(self):
        val = Validate(self.post)
        # These parameters are required
        val.required(['check', 'foo', 'name'])
        # 'last' is missing, so we fail the required check
        self.assertRaises(HTTPPreconditionFailed, val.required, ['check', 'foo', 'last'])

    def testValidate(self):
        val = Validate(MultiDict([(u'size', u'0')]))
        size_cond = [
            ["%(name)s must be an integer", lambda i: not isinstance(int(i), int)],
            ["%(name)s cannot be negative", lambda i: int(i) < 0 ],
            ["%(name)s cannot exceed max value", lambda i: int(i) > 1024 ]
        ]

        # size is valid
        val.validate('size', size_cond)

        val = Validate(MultiDict([(u'size', u'foo')]))
        self.assertRaises(HTTPPreconditionFailed, val.validate, 'size', size_cond)

