# Copyright (c) 2014, Menno Smits
# Released subject to the New BSD License
# Please see http://en.wikipedia.org/wiki/BSD_licenses

from collections import namedtuple
from email.utils import formataddr

import six


class Envelope(namedtuple("Envelope", "date subject from_ sender reply_to to " +
                          "cc bcc in_reply_to message_id")):
    """
    Represents envelope structures of messages. Returned when parsing
    ENVELOPE responses.

    :ivar date: A datetime instance that represents the "Date" header.
    :ivar subject: A string that contains the "Subject" header.
    :ivar from\_: A tuple of Address objects that represent on or more
      addresses from the "From" header, or None if header does not exist.
    :ivar sender: As for from\_ but represents the "Sender" header.
    :ivar reply_to: As for from\_ but represents the "Reply-To" header.
    :ivar to: As for from\_ but represents the "To" header.
    :ivar cc: As for from\_ but represents the "Cc" header.
    :ivar bcc: As for from\_ but represents the "Bcc" recipients.
    :ivar in_reply_to: A string that contains the "In-Reply-To" header.
    :ivar message_id: A string that contains the "Message-Id" header.
    """


class Address(namedtuple("Address", "name route mailbox host")):
    """
    Represents electronic mail addresses. Used to store addresses in
    :py:class:`Envelope`.

    :ivar name: The address "personal name".
    :ivar route: SMTP source route (rarely used).
    :ivar mailbox: Mailbox name (what comes just before the @ sign).
    :ivar host: The host/domain name.

    As an example, an address header that looks like::

        Mary Smith <mary@foo.com>

    would be represented as::

        Address(name=u'Mary Smith', route=None, mailbox=u'mary', host=u'foo.com')

    See :rfc:`2822` for more.
    """

    def __str__(self):
        return formataddr((self.name, self.mailbox + '@' + self.host))


class SearchIds(list):
    """
    Contains a list of message ids as returned by IMAPClient.search().

    The *modseq* attribute will contain the MODSEQ value returned by
    the server (only if the SEARCH command sent involved the MODSEQ
    criteria). See :rfc:`4551` for more details.
    """

    def __init__(self, *args):
        list.__init__(self, *args)
        self.modseq = None


class BodyData(tuple):
    """
    Returned when parsing BODY and BODYSTRUCTURE responses.
    """

    @classmethod
    def create(cls, response):
        # In case of multipart messages we will see at least 2 tuples
        # at the start. Nest these in to a list so that the returned
        # response tuple always has a consistent number of elements
        # regardless of whether the message is multipart or not.
        if isinstance(response[0], tuple):
            # Multipart, find where the message part tuples stop
            for i, part in enumerate(response):
                if isinstance(part, six.binary_type):
                    break
            return cls(([cls.create(part) for part in response[:i]],) + response[i:])
        else:
            return cls(response)

    @property
    def is_multipart(self):
        return isinstance(self[0], list)
