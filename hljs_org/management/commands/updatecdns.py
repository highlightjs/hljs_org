from optparse import make_option
import logging

from django.core.management.base import NoArgsCommand, CommandError
from django.core.cache import cache
from django.conf import settings

from hljs_org import lib


log = logging.getLogger('hljs_org.updatecdns')

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (make_option(
        '--expire',
        action='store', type='int', dest='expire',
        default=86400,
        help='Cache expiration time in seconds',
    ),)
    help = 'Update the site cache with availability of CDNs for the current version'

    requires_model_validation = False

    def handle(self, **options):
        version = lib.version(settings.HLJS_SOURCE)
        for title, script_url, style_url in settings.HLJS_CDNS:
            script_url = script_url % version
            result = lib.check_cdn(script_url)
            if result:
                cache.set(script_url, script_url, options['expire'])
            else:
                cache.delete(script_url)
            log.info('%s: %s' % (str(bool(result)).upper(), script_url))
