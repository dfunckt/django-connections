#!/usr/bin/env python

import sys
from os import environ
from os.path import abspath, dirname

import nose


def main():
    environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    
    # setup path
    test_dir = dirname(dirname(abspath(__file__)))
    sys.path.insert(0, test_dir)
    
    try:
        # django >= 1.7
        from django import setup
    except ImportError:
        pass
    else:
        setup()
    
    # setup test env
    from django.test.utils import setup_test_environment
    setup_test_environment()
    
    # setup db
    from django.core.management import call_command, CommandError
    options = {
        'interactive': False,
        'verbosity': 1,
    }
    try:
        call_command('migrate', **options)
    except CommandError:  # Django < 1.7
        call_command('syncdb', **options)
    
    # run tests
    return nose.main()


if __name__ == '__main__':
    main()
