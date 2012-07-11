EJTP-lib-python
===============

Encrypted JSON Transport Protocol library for Python 2.x.

EJTP is a data transfer protocol that allows JSON exchange over a
very wide and infinitely extensible set of underlying transports.
UDP, TCP, IRC, email, XMPP, HTTP, Telnet, Carrier pigeons, web
forums, Twitter, Socket.IO... almost any protocol you could name
can be engineered to carry EJTP frames.


Installation
============

Download, clone, or transmodulate the source code to your computer,
go into the uncompressed directory, and run "./setup.py install" as
an administrator account. This is standard procedure for most
Python libraries, and is how this one works as well.

The latest stable version (really, really recommended you don't try
to use anything development-y, since I have a tendency for code
demolition and reconstruction) is [Version 0.8.1](
https://github.com/campadrenalin/EJTP-lib-python/tree/stable-0.8.x),
which is fairly lean and debuggable, and has the new TCP Jack. If
you have issues, be sure to [submit the issue](
https://github.com/campadrenalin/EJTP-lib-python/issues/new) and,
ideally, send patches. These don't have to fix the underlying problem,
as long as they expose it to the unit testing mechanism, which allows
me to hammer at the code until it works again.


Dependencies
============

 * The latest version of [PyCrypto](https://www.dlitz.net/software/pycrypto/).
 * For testing, install [DoctestAll](https://github.com/campadrenalin/DoctestAll).


Usage
=====

You can try out the EJTP demo client by running ```./ejtp/interactive.py```.
For demo code you can look inside that file, but basically, all you
need is a Router object, and to create Clients as necessary, setting
their rcv_callback property to your own preferred callback.


Testing
=======

The "install_and_test.sh" script is a one-liner that I use to quickly
install updated code and run it through the test suite while I work.
It depends on having [DoctestAll](https://github.com/campadrenalin/DoctestAll)
installed, so you want to do that first of all, before testing EJTP.
If you want to know whether this EJTP implementation has any problems
on your system, run this script, and it should spit out something like

    name@machine$ ./install_and_test.sh
    0 failures, 32 tests.

at the end. If there are failures, be sure to copy the entire output
of the command and put that in a [Github Issue](
https://github.com/campadrenalin/EJTP-lib-python/issues/new) so I can
have a look at it. I may reply with questions in response to that, but
filing a test failure takes less than 5 minutes of your time and is
really appreciated.


EJTP Theory
===========

### Program structure

An EJTP program is composed of a few parts at minimum. At its heart
is the Router, which takes addressed messages from any source and tries
to pass them off to the appropriate jack or client.

Jacks are the Router's connections to the outside world, allowing EJTP 
frames to run on top of other protocols. Each of these needs a thread
or a greenlet or some way to poll its network mechanics for incoming
messages.

Finally, clients are objects that have properties like encryption
prototype, EJTP address with callsign, and methods to send and receive
encrypted frames through the Router. When created, they register
themselves with the Router so that messages to their location will be
forwarded properly.

Generally an application will consist of a Router, one or more clients,
a jack for every transport, with a thread for every jack plus one or
two for the GUI. The jack threads drive incoming events, the GUI thread
drives any outbound ones that aren't called from a jack thread
syncronously (such as asyncronous responses or user-driven events).

### How EJTP works

An EJTP address is a JSON list with 2 or 3 elements.

    [ addrtype, addrdetails, callsign (optional) ]

Clients have callsigns, jacks do not. The addrtype determines which jack
type to use to send frames to this address (for example "udp4" or "smtp"),
addrdetails provide the protocol-specific parameters necessary to send
frames across the network (such as IP address and port). The callsign is
used to indicate a specific client listening on that jack.

Different transport protocols will have their own standards on how to
carry EJTP frames (also, the addrtype for the protocol, and the structure
of the addrdetails for that addrtype). Generally this is pretty straight-
forward in connectionless protocols, or any protocol that provides a
built-in way to distinguish datagrams.

For two remote clients to communicate, Client A must be able to send frames
to Client B's jack, and vice versa. But that's not as limiting as it sounds,
you don't have to support every obscure jack type. You can set up the Router
with a default route function for undeliverable messages, so that the frame
is wrapped in a bigger frame addressed to your default route. In other words,
you can configure so that your simplistic program pipes its undeliverable
frames to a more capable server, which in turn can bounce the message around
according to its default routes, et cetera, until the message is delivered.
The default route feature is not yet built in, and will require safeguards to
drop frames when a routing loop occurs.

EJTP is an "unreliable" protocol, that is to say, no guarantees are made
that your frame will reach its destination in a timely fashion, if at all.
With certain jacks and network conditions that's not much of a worry, since
the probabilities are vastly in your favor, but any protocol built on EJTP
has to consider that, much like UDP, verifying delivery is left up to you,
and not inherently provided by EJTP.

### Frame format

A frame is composed of a single-character "typecode", an address (as JSON),
a nullbyte for a separator, and the message body. It's left up to the
underlying transport to specify the frame size.

A frame type of "j" should have a blank address (any address given will be
ignored, and is thus a waste of bandwidth), and a payload of unencrypted
JSON data, such that deserializing the payload results in exactly one JSON
object of any type (hash, list, bool, even null). All other frame types
are "nesting frames", and their payloads should be processed as frames.

To get across the network, a J frame has to be wrapped inside an S frame,
to indicate the Sender, which is then wrapped in an R frame, which indicates
the Recipient (or, in the case of nested R frames, "Relay"). S frames have
an encrypted payload that can be decrypted by anyone who knows the sender's
public key (essentially functioning as a signature and obfuscation). Its 
address is that of the sending client. An R frame's payload is encrypted
such that only the client given in the address can open it. 

If you decrypt a frame only to find that its payload is another R frame,
you must send that frame back out to the Router for further processing.
This nesting feature allows a client to securely bounce a message around
across the network with onion encryption, as only the final recipient will
even know they ARE the final recipient. For everyone else in the chain,
all they know is who sent it to them (not necessarily the original sender),
and that its final destination is probably elsewhere, unless the chain
loops back to them.

There are further complexities involving maximum frame size (which is the
same across all underlying transports), but I'm going to hold off on
formalizing those rules for awhile. Currently, frame splitting has been
removed from the codebase since it was not being used (or rather, split
messages could be sent but not decoded) and it seemed better to temporarily
remove the functionality entirely, rather than have it break in edge
cases where you send a message long enough to split.


EJTP Ecosystem
==============

EJTP boasts a fair number of projects that are based on it. Many of these
are micro-libraries and micro-protocols that serve higher-level systems,
following the maxim "Do one thing and do it well."

The following is an attempt to graph those relationships:

    EJTP
    |
    |- EJIdent   \
    |- EJForward --|- EJMail
                   |- DEJE
                   |- MCP
