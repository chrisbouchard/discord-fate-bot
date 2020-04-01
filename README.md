# Discord Fate Bot

A [Discord][discordapp] bot to help play the [Fate roleplaying game][fate-rpg].

[discordapp]: https://discordapp.com/
[fate-rpg]: https://www.evilhat.com/home/fate-core/


## Commands

Once this bot is invited to a server, it will listen in text channels for
commands and reply. All commands start with `!`.

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
      disappears when it runs out of invokes.
    * `invokes=COUNT` &mdash; Tag this aspect with some number of free
      invokes attached.
* `!aspect remove ID...` &mdash; Remove one or more aspects from the scene.
* `!aspect modify ID NAME` &mdash; Rename an existing aspect. The rest of the
  line will be used as the new aspect name.
    * **TODO:** It will eventually be possible to update tags as well.
* **TODO:** `!aspect invoke ID` &mdash; Decrease the number of remaining free
  invokes for the specified aspect.

### Future Commands

I plan to add commands to manage a turn order, and possibly to track fate
points. Beyond that, we may add facilities to track PCs and NPCs, though
Discord text channels may not be the most convenient interface to manage those.


## Installing

There project is available on Docker Hub at
[chrisbouchard/discord-fate-bot][docker-discord-fate-bot]. Images are
automatically built and published based on our `Dockerfile`. There is also a
`docker-compose.yml` file to deploy the app in Docker Swarm as a Stack,
including a Mongo DB service.

[docker-discord-fate-bot]: https://hub.docker.com/repository/docker/chrisbouchard/discord-fate-bot

### Installing in Docker Swarm as a Stack

To install as a Stack, simply deploy our `docker-compose.yml` file. To install
without having to check anything out, you can pipe it directly from GitHub.

```
$ curl https://raw.githubusercontent.com/chrisbouchard/discord-fate-bot/master/docker-compose.yml | \
      docker stack deploy --compose-file - discord-fate-bot
```

### Installing Other Ways

More to be written&hellip;


## Configuring

The bot looks for the following environment variables on start-up.

* `DFB_BOT_TOKEN` &mdash; The Discord authentication token for the bot account.
    * Mutually exclusive with `DFB_BOT_TOKEN_FILE`.
* `DFB_BOT_TOKEN_FILE` &mdash; The path to a file _containing_ the
  authentication token.
    * Mutually exclusive with `DFB_BOT_TOKEN`.
* `DFB_LOG_CONFIG_FILE` &mdash; _(Optional)_ The path to a Python log config
  file. See the [Python documentation][python-logging-config-file-format] for a
  description of the file format.
* `DFB_MONGO_CONNECTION_URL` &mdash; The MongoDB connection URL.
* `DFB_MONGO_PASSWORD` &mdash; The password for the Mongo DB connection.
    * Mutually exclusive with `DFB_MONGO_PASSWORD_FILE`.
* `DFB_MONGO_PASSWORD_FILE` &mdash; The path to a file _containing_ the
  password for the Mongo DB connection.
    * Mutually exclusive with `DFB_MONGO_PASSWORD`.

[python-logging-config-file-format]: https://docs.python.org/3/library/logging.config.html#configuration-file-format

**Note:** For variables that have a `*_FILE` pair, the direct version is
provided as a convenience, e.g., for development. We subscribe to the school of
thought that it's best not to store production secrets in environment variables
if at all avoidable. Our Docker Stack definition uses Secrets to share the
token and Mongo password into the services.


## Architecture

This bot is written in Python, mostly based on the awesome
[Discord.py][discord-py] library. We use [MongoDB][mongo-db] for long-term
storage when necessary (e.g., for scenes and aspects).

[discord-py]: https://github.com/Rapptz/discord.py
[mongo-db]: https://www.mongodb.com/

