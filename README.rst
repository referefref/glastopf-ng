Glastopf-ng (Python3)
=======================

ABOUT
-----

Glastopf is a Python web application honeypot founded by Lukas Rist. This was deprecated by tanner and snare many years ago and left to rust in the python2 desert. As part of some research into deception technologies the codebase has been partially rewritten (leaving as much of the original intact as possible) to function with Python3. There are doubtless errors present still, however it is partially functional on MacOS 14.0 Sonoma for testing purposes.

General approach:

- Vulnerability *type* emulation instead of vulnerability emulation. Once a vulnerability type is emulated, Glastopf can handle unknown attacks of the same type. While implementation may be slower and more complicated, we remain ahead of the attackers until they come up with a new method or discover a new flaw in our implementation.
- Modular design to add new logging capabilities or attack type handlers. Various database capabilities are already in place. HPFeeds logging is supported for centralized data collection.
- Popular attack type emulation is already in place: Remote File Inclusion via a build-in PHP sandbox, Local File Inclusion providing files from a virtual file system and HTML injection via POST requests.
- Adversaries usually use search engines and special crafted search requests to find their victims. In order to attract them, Glastopf provides those keywords (AKA "dork") and additionally extracts them from requests, extending its attack surface automatically. As a result, the honeypot gets more and more attractive with each new attack attempted on it.
- We will make the SQL injection emulator public, provide IP profiling for crawler recognition and intelligent dork selection.

INSTALL
-------
Installation instructions can be found `here <https://github.com/mushorg/glastopf/tree/master/docs/source/installation>`_.

It is highly recommended to customize the default attack surface to avoid trivial detection of the honeypot.
