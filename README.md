# TrackSaber

## Features:
  - ### Real-time gameplay tracking and notifications for discord.
    - Beatleader and ScoreSaber realtime tracking support.
    - When a foreign registered player plays message will be sent to your server

  - ### Challenge system.
    - Players can challenge each other to play specific songs.
    - The winner gets +2 points if they win.

  - ### Easy to implement for regional servers.
    - Add your bot token to the .env file.
    - Just edit the config.json file, translate the texts, set your country code and you're ready to go! 

## Configuration:
  - ### config.env:
    Create a new application from the [Discord Developer Portal](https://discord.com/developers/applications).
    When the application is created go to the Bot section, set a username for your bot and select all of the privileged gateway intents. 

    To get the token you have to regenerate your bot's token and copy it.

    paste your token after "=" in the file:
    ```bash
    token=MTUzNTY4NDAxNTg0MjAwNTAxMg.##########################
    ```

  - ### config.json:
    - **Country configuration:**
    Replace "(Your country code here)" with the country code you want to track. Ex

    ```json
      {
        "Country": "CO"
      }
    ```

    - **Updating locales:**
    Just change the text in the keys you want to change:
      Ex Old:
        ```json
          "Misc": {
            "AskUserToLink": "**It seems the user you are trying to challenge/stalk has not linked their account.**",
          }
        ```

      Ex New:
        ```json
          "Misc": {
              "AskUserToLink": "**The user you're quering hasn't linked their account yet.**",
            }
        ```
    
    - **Updating command names and descriptions:**
    Use the following table as reference:

    Where the key is of type command you can only use underscores and lowercase values.

| key | type | default value |
|---|---|---|
| FetchPersonBl |  command | bl_user |
| FetchPersonBlDescription | description | Check the BeatLeader statistics of another server member. |
| FetchOwnBl | command | bl_profile |
| FetchOwnBlDescription | description | Show your current BeatLeader profile statistics. |
| FetchOwnSs | command | ss_profile |
| FetchOwnSsDescription | description | Show your current ScoreSaber profile statistics. |
| FetchPersonSs | command | ss_user |
| FetchPersonSsDescription | description | Check the ScoreSaber statistics of another server member. |
| Unlink | command | unlink |
| UnlinkDescription | description | Unlink your Beat Saber account and remove your data from the bot. |
| Link | command | link |
| LinkDescription | description | Link your ScoreSaber or BeatLeader profile to your Discord account. |
| Cancel | command | cancel_challenge |
| CancelDescription | description | Cancel your current challenge (will grant victory to your opponent). |
| GetLeaderboard | command | challenge_leaderboard |
| GetLeaderboardDescription | description | Show the leaderboard of the top challengers in the server. |
| ChallengePlayer | command | challenge |
| ChallengePlayerDescription | description | Challenge a server player to beat a score on a map (BSR). |
| SetChallengeChannel | command | challenge_channel |
| SetChallengeChannelDescription | description | Set the current channel to receive challenge announcements. |
| SetFeedChannel | command | feed_channel |
| SetFeedChannelDescription | description | Set the current channel to display general player activity. |
| SetScoreChannel | command | score_channel |
| SetScoreChannelDescription | description | Set the current channel to display new scores. |
| RemoveChannel | command | disable_channel |
| RemoveChannelDescription | description | Remove the bot configuration in this channel to stop notifications. |

## Starting the bot:
  - ### Machine:
  1. Clone the repo

  ```bash
  git clone https://github.com/BrewTheFox/TrackSaber.git
  cd TrackSaber
  ```

  2. Configure your [environment files](./#configuration):

  3. Install the dependencies:
  ```bash
  python -m venv .venv (linux only)
  source .venv/bin/activate (linux only)
  pip install -r requirements.txt
  ```

  4. Run the bot:

  ```bash
  cd src
  python main.py
  ```

  - ### Docker Compose:
    ```yaml
    services:
      tracksaber:
        image: {built_image_name}
        restart: always

        volumes:
          - path/to/local/config.json: /app/config.json
          - path/to/local/db/notneeded/db.db: /app/database.db
          - path/to/local/logs.log: /app/logs.log
        
        environment:
          - token=MTUzNTY4NDAxNTg0MjAwNTAxMg.########################## (your discord bot token)
    
    ```

