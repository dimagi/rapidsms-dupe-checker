from threadless_router.tests.scripted import TestScript
from rapidsms.conf import settings

DEFAULT = "default response"
DUPE = "that was a dupe!"
IGNORE = "duplicatable"

class TestDupeChecker(TestScript):
    """
    This test assumes threadless_router is running and the message log
    and default apps are enabled in addition to the dupechecker app.
    """
    
    def setUp(self):
        super(TestDupeChecker, self).setUp()
        settings.DEFAULT_RESPONSE = DEFAULT
        settings.DUPECHECKER_RESPONSE = DUPE
        settings.DUPECHECKER_IGNORE = IGNORE
        self.string_args = {"default": DEFAULT, 
                            "dupe": DUPE}
        
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

    