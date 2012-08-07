""" This module handles the conversion of fedmsg messages (dict-like json
objects) into internationalized human-readable strings:  strings like
"nirik voted on a tag in tagger" and "lmacken commented on a bodhi update."

The intent is to use the module 1) in the fedmsg-irc bot and 2) in the
gnome-shell desktop notification widget.  The sky's the limit, though.

Message processing is handled by a list of MessageProcessors defined in
submodules of this module.  Messages for which no MessageProcessor exists are
handled gracefully.
"""

# TODO - internationalization
_ = lambda s: s

from fedmsg.text.bodhi import BodhiProcessor
from fedmsg.text.tagger import TaggerProcessor
from fedmsg.text.default import DefaultProcessor

processors = [
    BodhiProcessor(_),
    TaggerProcessor(_),
    DefaultProcessor(_),
]


def msg2repr(msg, **config):
    fmt = "{title} -- {subtitle}"
    title = _msg2title(msg, **config)
    subtitle = _msg2subtitle(msg, **config)
    return fmt.format(**locals())


def _msg2title(msg, **config):
    for p in processors:
        if not p.handle_title(msg, **config):
            continue
        title = p.title(msg, **config)
        break

    suffix = _msg2suffix(msg, **config)
    if suffix:
        title = title + " " + suffix

    return title


def _msg2subtitle(msg, **config):
    for p in processors:
        if not p.handle_subtitle(msg, **config):
            continue
        return p.subtitle(msg, **config)

    # This should never happen.
    # DefaultProcessor should always catch messages.
    raise RuntimeError("No text processor caught the message.")


def _msg2suffix(msg, **config):
    if 'signature' not in msg:
        return _("(unsigned)")
    else:
        if not fedmsg.crypto.validate(msg, **config):
            return _("(invalid signature!)")

    return ""
