# -*- coding: utf-8 -*-
import logging
from color import ColorizingStreamHandler

from copydog.watcher import Watch
from tests.config import CopyDogConfig

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='[%d.%m.%Y %H:%M:%S]')
logging.getLogger('copydog.api').setLevel(logging.DEBUG)
logging.getLogger('copydog.watcher').setLevel(logging.DEBUG)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.DEBUG)
logging.getLogger('copydog.api').addHandler(ColorizingStreamHandler())

watch = Watch(config=CopyDogConfig)
watch.run()