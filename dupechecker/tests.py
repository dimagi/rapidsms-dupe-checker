try:
    from threadless_router.tests.scripted import TestScript
except ImportError:
    from rapidsms.tests.scripted import TestScript

from rapidsms.contrib.messagelog.models import Message
from rapidsms.conf import settings

DEFAULT = "default response"
DUPE = "that was a dupe!"
IGNORE = "duplicatable"
INCLUDE = "include"

class TestDupeChecker(TestScript):
    """
    This test assumes threadless_router is running and the message log
    and default apps are enabled in addition to the dupechecker app.
    """
    
    def setUp(self):
        super(TestDupeChecker, self).setUp()
        settings.DEFAULT_RESPONSE = DEFAULT
        settings.DUPECHECKER_RESPONSE = DUPE
        settings.DUPECHECKER_IGNORE = []
        settings.DUPECHECKER_INCLUDE = []
        self.string_args = {"default": DEFAULT,
                            "dupe": DUPE}
        Message.objects.all().delete()
        
    def testBasic(self):
        self.assertInteraction("""
          8005551212 > first dupe message
          8005551212 < %(default)s
          8005551212 > second dupe message
          8005551212 < %(default)s
          8005551212 > second dupe message
          8005551212 < %(dupe)s
          8005551212 > third dupe message
          8005551212 < %(default)s
          8005551212 > third dupe message
          8005551212 < %(dupe)s
          8005551212 > first dupe message
          8005551212 < %(dupe)s
        """ % self.string_args)

    def testPhoneNumberDupes(self):
        self.assertEqual(0, Message.objects.count())
        self.assertInteraction("""
          8005551212 > first dupe message
          8005551212 < %(default)s
          8005551213 > first dupe message
          8005551213 < %(default)s
          8005551214 > first dupe message
          8005551214 < %(default)s
          8005551212 > first dupe message
          8005551212 < %(dupe)s
          8005551213 > first dupe message
          8005551213 < %(dupe)s
          8005551214 > first dupe message
          8005551214 < %(dupe)s
        """ % self.string_args)

    def testCaseInsensitivity(self):
        self.assertInteraction("""
          8005551212 > first dupe message
          8005551212 < %(default)s
          8005551212 > fIrST DuPE mESsAGe
          8005551212 < %(dupe)s
          8005551212 > FIRST DUPE MESSAGE
          8005551212 < %(dupe)s
        """ % self.string_args)

    def testIgnoreSetting(self):
        settings.DUPECHECKER_IGNORE = [IGNORE]
        self.assertInteraction("""
          8005551212 > duplicatable message
          8005551212 < %(default)s
          8005551212 > duplicatable message
          8005551212 < %(default)s
          8005551212 > DUPLICATABLE message
          8005551212 < %(default)s
          8005551212 > not duplicatable message
          8005551212 < %(default)s
          8005551212 > not duplicatable message
          8005551212 < %(dupe)s
        """ % self.string_args)

    def testIncludeSetting(self):
        settings.DUPECHECKER_INCLUDE = [INCLUDE]
        self.assertInteraction("""
          8005551212 > include message
          8005551212 < %(default)s
          8005551212 > include message
          8005551212 < %(dupe)s
          8005551212 > INCLUDE message
          8005551212 < %(dupe)s
          8005551212 > InClUdE mEsSaGe
          8005551212 < %(dupe)s
          8005551212 > not included
          8005551212 < %(default)s
          8005551212 > not included
          8005551212 < %(default)s
          8005551212 > anything else
          8005551212 < %(default)s
          8005551212 > anything else
          8005551212 < %(default)s
        """ % self.string_args)
