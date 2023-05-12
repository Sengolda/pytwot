:orphan:

.. currentmodule:: pytwot

.. versionadded:: 1.2.0


Logging
===============

pytwot now provides **logging** support!
However, you will not see these logs since they are muted.

To make the logs show you can do:

.. code-block:: py

    import logging

    logging.basicConfig(level=logging.INFO)

This will log everything being logged my pytwot!

More advanced logging setups are possible by logging them to a file.
You can do this like this

.. code-block:: py

    import logging

    logging.basicConfig(
        level=logging.INFO, 
        filename="pytwot.log", 
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
        )

Why logs?
----------------

Logging might show you parts of pytwot that you are using wrong. This will make debugging a whole lot easier.
