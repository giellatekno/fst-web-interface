# What is this?

A way to run forrest in a docker container, for development on gtuit.
Why docker? Because it relies on ancient versions of java to run, and also
makes modifications to forrest sources to be able to compile properly, and
it's really nice to have that all happen in isolation from the rest of your
system.

Also, this readme explains how to use this image to 

# Prerequisites

The beautiful thing about docker, is that as long as you have docker,
that's all you need. As long as all resources that the image needs stays
online and does not change, the image should build nicely every time,
on every system.

# Make the image

just run `make image`

# Use the image to build gtuit

Navigate to root of the svn directory (1), `main`, and run:
```bash
docker run --rm -it -v `pwd`:/home/main forrest
```

Now, inside the image, navigate to the gtuit folder, and build:

```bash
cd /home/main/xtdoc/gtuit
forrest site
```

After that is complete (it takes a good while), you'll see some errors in
the console. That's expected; the site has still been built, and
you can quit the container. Now navigate to the gtuit-folder, and you should
see a `build/site/` folder, containing the statically built site.
If you want to just check it out quickly, navigate to the folder and start
a simple http server, using your favorite tools, as for example:

```bash
cd build/site
python -m http.server
```

(1): Why mount the root of the svn directory to the docker image,
instead of in `xtdoc/gtuit`?
A: Because a folder inside `gtuit` has a symlink to `main/tools/forrest-plugins`.
