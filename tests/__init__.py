try:
    from nose.tools import assert_raises_regex
except ImportError:
    try:
        from nose.tools import assert_raises_regexp as assert_raises_regex
    except ImportError:
        import re
        import nose.tools
        
        # copied from python-2.7-src/Lib/unittest/case.py
        class AssertRaisesContext(object):
            def __init__(self, expected, expected_regexp=None):
                self.expected = expected
                self.expected_regexp = expected_regexp
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_value, tb):
                if exc_type is None:
                    try:
                        exc_name = self.expected.__name__
                    except AttributeError:
                        exc_name = str(self.expected)
                    nose.tools.fail('%s not raised' % exc_name)
                if not issubclass(exc_type, self.expected):
                    # let unexpected exceptions pass through
                    return False
                self.exception = exc_value  # store for later retrieval
                if self.expected_regexp is None:
                    return True
                expected_regexp = self.expected_regexp
                if isinstance(expected_regexp, basestring):
                    expected_regexp = re.compile(expected_regexp)
                if not expected_regexp.search(str(exc_value)):
                    nose.tools.fail('%s does not match' % (
                        expected_regexp.pattern, str(exc_value)))
                return True
        
        def assert_raises_regex(expected, regexp, callable_obj=None, *args, **kwargs):
            context = AssertRaisesContext(expected, regexp)
            if callable_obj is None:
                return context
            with context:
                callable_obj(*args, **kwargs)
        
        nose.tools.assert_raises_regex = assert_raises_regex
