rapidsms-dupe-checker
=====================

A very simple app to auto-respond to duplicate messages in RapidSMS. Duplicate messages are handled
with a configurable default response and not processed by other apps. In order to ensure that this
works as desired, it should be first in your list of apps so that it can short circuit the handle
phase of subsequent apps.

It relies on the following settings:

* `DUPECHECKER_TIME_WINDOW_SECONDS`: How far back to look for duplicates (default: 2 days)
* `DUPECHECKER_RESPONSE`: Default response to duplicate messages (default: "Thanks, that message has already been handled.").
  If not set no response will be sent for duplicate messages (they will be ignored).
* `DUPECHECKER_IGNORE`: (blacklist) if specified, a list  of regexes which, if it matches the beginning of the message, will cause this app to still not flag it as a duplicate
* `DUPECHECKER_INCLUDE`: (whitelist) if specified, a list  of regexes which, if it matches the beginning of the message, will cause this app to only flag it as a duplicate
