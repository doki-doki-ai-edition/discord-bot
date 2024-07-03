This is the source code for the Doki Doki AI Edition discord bot.
If you're interested in setting it up for yourself, the process is down below.


# Getting Started

- in the directory of the project type this in a terminal `pip install -r requirements.txt`

Setup a `config.json` file like this:

```js
{
    "BOT_TOKEN": "Enter your token here",
    "GROQ": "Enter your token here",
    "GPT_TOKEN": "Enter your token here"
}
```
And obviously replace "Enter your token here" with your actual tokens.

## Channel 

In your server create a log channel that only the DDAE bot and the other club member bots will have access to.

<img src="github_assets\logs.png" alt="discord log channel">


## Monika

- Make a bot and name it Monika
- Use the code from https://github.com/doki-doki-ai-edition/Monika-bot
- Set `bot.monika_thread_id` to a thread ID that only the Monika bot will have access to in your #doki-logs channel



## Sayori

- Make a bot and name it Monika
- Use the code from https://github.com/doki-doki-ai-edition/Sayori-bot
- Set `bot.sayori_thread_id` to a thread ID that only the Sayori bot will have access to in your #doki-logs channel

## Natsuki

- Make a bot and name it Monika
- Use the code from https://github.com/doki-doki-ai-edition/Natsuki-bot
- Set `bot.natsuki_thread_id` to a thread ID that only the Natsuki bot will have access to in your #doki-logs channel

## Yuri

- Make a bot and name it Monika
- Use the code from https://github.com/doki-doki-ai-edition/Yuri-bot
- Set `bot.yuri_thread_id` to a thread ID that only the Yuri bot will have access to in your #doki-logs channel


