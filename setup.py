import sys
from setuptools import setup

if sys.platform == 'darwin':
    extra_options = {
        'app': ['main.py'],
        'options': {
            'py2app': {
                'argv_emulation': True,
                'iconfile': 'assets/icons/logo.icns'
            }
        },
        'setup_requires': ['py2app'],
    }
else:
    extra_options = {}

setup(
    name='NetDiag',
    **extra_options
)