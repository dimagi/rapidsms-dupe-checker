from rapidsms.conf import settings
from rapidsms.apps.base import AppBase
from rapidsms.contrib.messagelog.models import Message
from datetime import datetime, timedelta

class App(AppBase):
    """
    Check for duplicates and if we find them send a default response
    and say that we've handled the message, preventing further processing.
    """
    
    def handle(self, msg):
        msgs = Message.objects.filter(direction="I", 
                                      connection=msg.connection,
                                      text__iexact=msg.raw_text)
        
        # should always be true since this message has just been log
        assert msgs.count() > 0
        if settings.DUPECHECKER_TIME_WINDOW_SECONDS:
            cutoff = datetime.utcnow() - \
                timedelta(seconds=settings.DUPECHECKER_TIME_WINDOW_SECONDS)
            msgs = msgs.filter(date__gt=cutoff)
        if msgs.count() > 1:
            msg.error(settings.DUPECHECKER_RESPONSE)
            return True