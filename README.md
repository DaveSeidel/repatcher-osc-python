# repatcher-osc-python
Reads rePatcher (Arduino shield) data and publishes it as OSC. Requires Python 3.

## Notes
Reads data from a rePatcher device (http://www.openmusiclabs.com/projects/repatcher/) and publishes it as an OSC stream. Inspired by J. Siemasko's Processing program of the same name (http://schemawound.com/post/93125359548/repatcher-to-osc).

This program requires Python 3.x (because python-osc required it).

Quoting from Siemasko's original article:

> The knobs will send a message in the format of /repatcher/knobN where N is a number between 0 and 5 representing the current knob. The knobs will send a single argument of a float between 0 and 1 for the current value.

> The patchbay will send a message in the format of /repatcher/outputN where N is a number between 0 and 5 representing the current output. The patchbay will send six integers with a value of 0 or 1 to represent which inputs are patched to the current output.

Regarding the rePatcher Arduino sketch, Siemasko provides the following advice:

> Download the rePatcher Arduino code from the Open Music Labs Wiki and delete the following line before loading the code to your arduino:

    while (Serial.read() != 0xab); // wait for turn on signal

> In the PD patch that Open Music Labs provided they had a functionality where you could start and stop the rePatcher serial stream. It was not a bad idea but without a hardware button for the function it just seems like an extra step in trying to get the rePatcher set up properly.

The rePatcher Arduino sketch (and further technical details regarding the rePatcher, including plans from which you can build your own) can be retrieved from http://wiki.openmusiclabs.com/wiki/Repatcher.

## Author
Dave Seidel
- http://githib.com/DaveSeidel
- http://mysterybear.net

## License
Released under GPL 3.0

Original publishing date: 2015-03-22
