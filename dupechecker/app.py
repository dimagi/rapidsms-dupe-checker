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
    _ignore_re = []
    _include_re = []

    def start(self):
        self._ignore_re = []
        self._include_re = []
        if settings.DUPECHECKER_IGNORE and settings.DUPECHECKER_INCLUDE:
            raise Exception("only set one of the DUPECHECKER_IGNORE and DUPECHECKER_INCLUDE settings.")
        if settings.DUPECHECKER_IGNORE:
            for ignore in settings.DUPECHECKER_IGNORE:
                self._ignore_re.append(re.compile(ignore, re.I))
        if settings.DUPECHECKER_INCLUDE:
            for include in settings.DUPECHECKER_INCLUDE:
                self._include_re.append(re.compile(include, re.I))

    def handle(self, msg):
        # if we matched something to ignore don't deal with this
        for ignore in self._ignore_re:
            if ignore.match(msg.raw_text):
                return

        any_inclusions = any([include.match(msg.raw_text) for include in self._include_re])
        if self._include_re and not any_inclusions:
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
            if settings.DUPECHECKER_RESPONSE:
                msg.error(settings.DUPECHECKER_RESPONSE)
            return True

    def outgoing(self, msg):
        pass