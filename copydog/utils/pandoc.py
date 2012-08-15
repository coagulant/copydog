# -*- coding: utf-8 -*-
import logging
import subprocess
log = logging.getLogger('copydog')


PANDOC_PATH = '/usr/bin/pandoc'


def convert(text, from_format, to_format):
    """ Convert markups using pandoc
        Inspired by https://github.com/kennethreitz/pyandoc

        In case of error returns input text as output.
    """
    try:
        p = subprocess.Popen(
            [PANDOC_PATH, '--from=%s' % from_format, '--to=%s' % to_format],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        return p.communicate(text.encode('utf-8'))[0].decode('utf-8')
    except OSError as e:
        log.warn('Pandoc is misconfigured, %s', str(e))
        return text
    except Exception:
        return text

