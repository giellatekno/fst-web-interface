## Forrest

The old web framework used on [giellatekno.uit.no](https://giellatekno.uit.no)
is something called Apache [Forrest](https://forrest.apache.org).

Development on it is tricky, due to requiring an old version of java.
Therefore, in the folder
`forrest_in_docker` in the root of the project folder, contains a `Dockerfile`
for building an image capable of compiling and running forrest correctly.
The accompanying `Makefile` makes it easy to build it, and run it to do
development on the giellatekno pages, which are located in
`svn/main/xtdoc/gtuit`.

### docker crash course

The only requirement of this setup, is [docker](https://docker.com). If you
are unfamiliar with it, think of it as small virtual machines. A docker *image*
is a binary file which contains the system, and anything that is installed into
it. A running instance of an image is called a *container*.

What goes into the image is determined by the `Dockerfile` that made it. It
is a textual file of commands to run, which will be run when the image is built,
using the command `docker build`. Any command that installs or changes something
on the system, is recorded and kept in the image.

To run an image, use `docker run`.

### The Makefile targets

#### image

`make image` will create the image. It takes some seconds to run. As long as
all the resources (packages downloaded from various sources on the internet)
the `Dockerfile` uses is still available, it will complete
succesfully every time, on every system.

#### gtuit-run

`make gtuit-run` will run the image. It will `mount` the `GTHOME` dictionary
inside the container, on the path `/home/main`. It will also expose port `8888`
to the host system, so that if you do `forrest run` inside the container, the
open port `8888` inside the container can be reached on port `8888` on the
host system.

If you do `forrest site` inside the container, to build the *giellatekno*
(or any other) site, the resulting `build/` dictionary is present in the host
system as well, because the directory had been mounted from outside.

Refer to the Dockerfile, and [docker documentation](https://docs.docker.com)
for more, if you want to do something different, like mount a different directory,
for example.
