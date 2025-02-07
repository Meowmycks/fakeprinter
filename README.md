# fakeprinter
Bunch of Python scripts made to host fake printer-like services.

The idea I had was to turn a Kali box into a more convincing "innocent printer on the network", so I made this to add on top of using a spoofed MAC address and a generic HP printer's hostname.

Includes some common HP printer services like JetDirect, IPP, and a web port that always throws a 401 Unauthorized.

Still a work-in-progress. Need to add more ports and fix up some stuff, but it's difficult when you don't have a real network printer to compare against.
