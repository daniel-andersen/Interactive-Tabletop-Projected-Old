Client
======

The client library of Interactive Tabletop Project:ed to be included in client projects.
Handles all communication with the server.

Building
--------

Build and run using:

`grunt run`

This will compile all submodules listed in _gruntfile.js_, copy everything into the _target_ directory and finally
run it.

Content
-------

To include new content, add the content to the _gruntfile.js_ following the MAZE example. In short, add the new content
as a submodule in _subgrunt_ and add a copy task to copy the necessary files into place.
