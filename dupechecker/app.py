from rapidsms.conf import settings
from rapidsms.apps.base import AppBase
from rapidsms.contrib.messagelog.models import Message
from datetime import datetime, timedelta
import re

class App(AppBase):
    """
    Check for duplicates and if we find them send a default response
    and say that we've handled the message, preventing further processing.
    """
    _ignore_re = None
    
    def start(self):
        if settings.DUPECHECKER_IGNORE:
            self._ignore_re = re.compile(settings.DUPECHECKER_IGNORE, re.I)
        
    def handle(self, msg):
        
        # if we matched something to ignore don't deal with this
        if self._ignore_re and self._ignore_re.match(msg.raw_text):
            return 

        msgs = Message.objects.filter(direction="I", 
                                      connection=msg.connection,
                                      text__iexact=msg.raw_text)
        
        # should always be true since this message has just been logged
        assert msgs.count() > 0
        if settings.DUPECHECKER_TIME_WINDOW_SECONDS:
            cutoff = datetime.utcnow() - \
                timedelta(seconds=settings.DUPECHECKER_TIME_WINDOW_SECONDS)
            msgs = msgs.filter(date__gt=cutoff)
        if msgs.count() > 1:
            msg.error(settings.DUPECHECKER_RESPONSE)
            return True