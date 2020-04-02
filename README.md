# Discord Fate Bot

[![CircleCI][circleci-dfb-svg]][circleci-dfb]
[![PyPI Version][shieldsio-pypi-dfb]][pypi-dfb]
[![PyPI Python][shieldsio-python-dfb]][pypi-dfb]
[![Docker][shieldsio-docker-dfb]][docker-dfb]

A [Discord][discordapp] bot to help play the [Fate roleplaying game][fate-rpg].

[discordapp]: https://discordapp.com/
[fate-rpg]: https://www.evilhat.com/home/fate-core/

[circleci-dfb]: https://circleci.com/gh/chrisbouchard/discord-fate-bot
[circleci-dfb-svg]: https://circleci.com/gh/chrisbouchard/discord-fate-bot.svg?style=svg
[docker-dfb]: https://hub.docker.com/repository/docker/chrisbouchard/discord-fate-bot
[pypi-dfb]: https://pypi.org/project/discord-fate-bot/
[shieldsio-docker-dfb]: https://img.shields.io/docker/v/chrisbouchard/discord-fate-bot?sort=semver&label=docker
[shieldsio-pypi-dfb]: https://img.shields.io/pypi/v/discord-fate-bot
[shieldsio-python-dfb]: https://img.shields.io/pypi/pyversions/discord-fate-bot


## Commands

Once Discord Fate Bot is invited to a server, it will listen in text channels
for commands and reply. All commands start with `!`.

### `!roll`

Roll four Fate dice, with modifiers, optionally against a static opposition.
This command has the following forms.

* `!roll` &mdash; Simply roll four Fate dice and see the result
* `!roll [+|-]MOD...` &mdash; Roll with a modifier. The `+` or `-` is required.
  Multiple modifiers may be given, separated by spaces.
    * Example: `!roll +5 -2` to roll with an effective +3 modifier.
* `!roll MODIFIERS vs OPPOSITION` &mdash; Roll against a static opposition
  amount. The result will be one of: fail, tie, succeed, or succeed with style.
    * Example: `!roll +2 vs 3`

### `!scene`

Start a scene in the current channel. Each channel can have one scene active,
which can be used to track situation aspects. The message describing the
current scene will automatically be pinned (and unpinned when the scene ends).

* `!scene [DESCRIPTION]` &mdash; Start a new scene in the current channel. The
  entire rest of the message will be used as the description. If a scene is
  already active, it will be ended automatically.
    * Example: `!scene Warehouse Five`

* `!scene end` &mdash; End the current scene.

### `!aspect`

Add or manage aspects in the current scene. There must be an active scene in
the current channel to use these commands. Aspects are automatically added to
the pinned scene message.

Every aspect is given an ID &mdash; a unique number within the scene &mdash;
which is used to refer to the aspect after creation (for example, to remove
it).

* `!aspect [TAGS]... NAME` &mdash; Add a new aspect to the current scene.
  Tags may be included, separated by spaces. After tags, the rest of the line
  will be used the aspect name.
    * `boost` &mdash; Tag this aspect as a boost, which means it automatically
      disappears when it runs out of invokes. **TODO:** A boost should
      implicitly add one free invoke if the `invokes` tag is not specified.
    * `invokes=COUNT` &mdash; Tag this aspect with some number of free
      invokes attached.
    * Example: `!aspect Darkness of night`
    * Example: `!aspect boost invokes=2 Really awesome aspect name`
* `!aspect remove ID...` &mdash; Remove one or more aspects from the scene.
* `!aspect modify ID NAME` &mdash; Rename an existing aspect. The rest of the
  line will be used as the new aspect name.
    * **TODO:** It will eventually be possible to update tags as well.
* **TODO:** `!aspect invoke ID` &mdash; Decrease the number of remaining free
  invokes for the specified aspect.

### Future Commands

I plan to add commands to manage a turn order, and possibly to track fate
points. Beyond that, I may add facilities to track PCs and NPCs, though Discord
text channels may not be the most convenient interface to manage those.


## Inviting the Bot

There isn't currently a public instance of Discord Fate Bot available for
invite. If you host your own copy, the bot will log an invite URL when it
connects to Discord. Currently, the bot will ask for the following Discord
permissions.

* Add reactions
    * To leave a :+1: once it has processed a message.
* Manage messages
    * To pin and unpin the scene message.
* Read message history
    * Not currently used, but I have a half-thought that there could be a
      feature to recover scenes from message history if the database is
      out-of-sync with the channel.
* Read messages
    * To read commands.
* Send messages
    * To reply with results.

This list may grow and change while the bot is in development, but I'll try to
freeze it once I release a stable public version.


## Installing

Discord Fate Bot is available [on Docker Hub][docker-dfb]. Images are
automatically built and published based on our `Dockerfile`. There is also a
`docker-compose.yml` file to deploy the app in Docker Swarm as a Stack,
including a Mongo DB service.

### Installing in Docker Swarm as a Stack

To install as a Stack, simply deploy our `docker-compose.yml` file. To install
without having to check anything out, you can pipe it directly from GitHub.

```
$ curl https://raw.githubusercontent.com/chrisbouchard/discord-fate-bot/master/docker-compose.yml | \
      docker stack deploy --compose-file - discord-fate-bot
```

### Installing from PyPI

Discord Fate Bot is also available [on PyPI][pypi-dfb].

```
$ pip install discord-fate-bot
$ discord-fate-bot
```

Make sure to configure your environment variables to hook up to Discord and
your Mongo database (see below).

### Installing from Source

I don't necessarily recommend this for production, but you can check out the
project locally and install in a virtual environment.

Make sure you have at least Python 3.7 installed. You'll also need to
[install Poetry][install-poetry], which we use for dependency management
and packaging.

```
$ git checkout https://github.com/chrisbouchard/discord-fate-bot.git
$ cd discord-fate-bot
$ poetry install
$ poetry run discord-fate-bot
```

Make sure to configure your environment variables to hook up to Discord and
your Mongo database (see below).

[install-poetry]: https://python-poetry.org/docs/#installation


## Configuring

Discord Fate Bot looks for the following environment variables on start-up.

* `DFB_BOT_TOKEN` &mdash; The Discord authentication token for the bot account.
    * Mutually exclusive with `DFB_BOT_TOKEN_FILE`.
* `DFB_BOT_TOKEN_FILE` &mdash; The path to a file _containing_ the
  authentication token.
    * Mutually exclusive with `DFB_BOT_TOKEN`.
* `DFB_LOG_CONFIG_FILE` &mdash; _(Optional)_ The path to a Python log config
  file. See the [Python documentation][python-logging-config] for a description
  of the file format.
* `DFB_MONGO_CONNECTION_URL` &mdash; The MongoDB connection URL.
* `DFB_MONGO_PASSWORD` &mdash; The password for the Mongo DB connection.
    * Mutually exclusive with `DFB_MONGO_PASSWORD_FILE`.
* `DFB_MONGO_PASSWORD_FILE` &mdash; The path to a file _containing_ the
  password for the Mongo DB connection.
    * Mutually exclusive with `DFB_MONGO_PASSWORD`.

[python-logging-config]: https://docs.python.org/3/library/logging.config.html#configuration-file-format

**Note:** For variables that have a `*_FILE` pair, the direct version is
provided as a convenience, e.g., for development. I subscribe to the school of
thought that it's best not to store production secrets in environment variables
if at all avoidable. Our Docker Stack definition uses Secrets to share the
Discord token and Mongo password into the services.


## Architecture

Discord Fate Bot is written in Python, mostly based on the awesome
[Discord.py][discord-py] library. We use [MongoDB][mongo-db] for long-term
storage when necessary (e.g., for scenes and aspects).

[discord-py]: https://github.com/Rapptz/discord.py
[mongo-db]: https://www.mongodb.com/

