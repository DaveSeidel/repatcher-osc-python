"""
Reads data from a rePatcher device (http://www.openmusiclabs.com/projects/repatcher/)
and publishes it as an OSC stream. Inspired by J. Siemasko's Processing program
of the same name (http://schemawound.com/post/93125359548/repatcher-to-osc).

This program requires Python 3.x (because python-osc required it).

Quoting from Siemasko's original article:

  The knobs will send a message in the format of /repatcher/knobN where N is a number
  between 0 and 5 representing the current knob. The knobs will send a single argument
  of a float between 0 and 1 for the current value.

  The patchbay will send a message in the format of /repatcher/outputN where N is a
  number between 0 and 5 representing the current output. The patchbay will send six
  integers with a value of 0 or 1 to represent which inputs are patched to the current output.

Regarding the rePatcher Arduino sketch, Siemasko provides the following advice:

  Download the rePatcher Arduino code from the Open Music Labs Wiki and delete the following
  line before loading the code to your arduino:
    while (Serial.read() != 0xab); // wait for turn on signal
  In the PD patch that Open Music Labs provided they had a functionality where you could start
  and stop the rePatcher serial stream. It was not a bad idea but without a hardware button for
  the function it just seems like an extra step in trying to get the rePatcher set up properly.

The rePatcher Arduino sketch (and further technical details regarding the rePatcher, including plans
from which you can build your own) can be retrieved from http://wiki.openmusiclabs.com/wiki/Repatcher.

Dave Seidel
http://githib.com/DaveSeidel
http://mysterybear.net

Released under GPL 3.0
Original publishing date: 2015-03-22
"""

VERSION = "1.0.0"

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient
from serial import Serial


class Scaler(object):
  """
  Scales a number in a specified source range to a specified destination range.
  """

  def __init__(self, src, dst):
    self.srcBeg = src[0]
    self.dstBeg = dst[0]
    self.srcRng = src[1] - src[0]
    self.dstRng = dst[1] - dst[0]

  def __call__(self, val):
    return ((val - self.srcBeg) / self.srcRng) * self.dstRng + self.dstBeg


class RepatcherReader(object):
  """
  Reads data from a rePatcher and sends the output to a "sender" class instance.
  """

  MESSAGE_BUFFER_START = b'\xc0'
  BUFFER_LEN = 18

  def __init__(self, sender, port='/dev/ttyACM0', rate=38400):
    self.sender = sender
    self.scaler = Scaler((0.0, 1024.0), (0.0, 1.0))

    print("Opening rePatcher connection at %s (%d baud)" % (port, rate))
    try:
      self.ser = Serial(port, rate)
    except IOError as e:
      print(e)
      exit(1)

  def _read_patch_bay(self, buffer):
    for i in range(12, 18):
      # bays are in reverse order
      out_pin = int(5 - (i - 12))
      # bitflags, one per connection point
      values = [
        1 if (buffer[i] & j) == j else 0
        for j in [32, 16, 8, 4, 2, 1]
      ]
      self.sender.send_patch_bay(out_pin, values)

  def _read_knobs(self, buffer):
    for i in range(0, 12, 2):
      # knob are in reverse order
      knob_num = int(5 - (i / 2))
      # we'e really reading words
      raw_val = (buffer[i+1] << 7) | buffer[i]
      # scale 0-1024 values to 0.0000-0.999 values
      knob_val = self.scaler(raw_val)
      self.sender.send_knob(knob_num, knob_val)

  def read(self):
    while True:
      byte = self.ser.read(1)
      if byte == self.MESSAGE_BUFFER_START:
        buffer = bytearray(self.ser.read(self.BUFFER_LEN))
        self.ser.flushInput()
        self._read_knobs(buffer)
        self._read_patch_bay(buffer)


class OscSender(object):
  """
  Publishes rePatcher data as OSC.
  """

  def __init__(self, ipaddr="127.0.0.1", port=12000, verbose=False):
    print("Publishing OSC at %s:%d" % (ipaddr, port))
    self.client = UDPClient(ipaddr, port)
    self.verbose = verbose

  def send_knob(self, knob_num, knob_val):
    if self.verbose:
      print("knob %d: %f" % (knob_num, knob_val))
    builder = OscMessageBuilder(address="/repatcher/knob" + str(knob_num))
    builder.add_arg(knob_val)
    msg = builder.build()
    self.client.send(msg)

  def send_patch_bay(self, output_num, values):
    if self.verbose:
      print("bay %d: %s" % (output_num, str(values)))
    builder = OscMessageBuilder(address="/repatcher/output" + str(output_num))
    for v in values:
      builder.add_arg(v)
    msg = builder.build()
    self.client.send(msg)


def main():
  parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version=VERSION)
  parser.add_argument("-a", "--addr", default="127.0.0.1",
      help="The IP address for publishing OSC messages")
  parser.add_argument("-p", "--port", type=int, default=12000,
      help="The port for publishing OSC messages")
  parser.add_argument("-u", "--usb_port", default="/dev/ttyACM0",
      help="rePatcher USB port")
  parser.add_argument("-r", "--usb_rate", type=int, default=38400,
      help="rePatcher baud rate")
  parser.add_argument("-v", "--verbose", action="store_true",
      help="print parsed rePatcher data as it is read in")
  args = parser.parse_args()

  sender = OscSender(args.addr, args.port, args.verbose)
  reader = RepatcherReader(sender, args.usb_port, args.usb_rate)
  reader.read()


# TODO: commandline args
if __name__ == '__main__':
  main()
