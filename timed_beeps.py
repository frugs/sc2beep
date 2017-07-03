import asyncio
import json

import aiohttp
import simpleaudio

SC2_CLIENT_GAME_ENDPOINT = "http://localhost:6119/game"
START_TIME = 150
BIG_BEEP_INTERVAL = 30
SMALL_BEEP_INTERVAL = 5

BIG_BEEP = simpleaudio.WaveObject.from_wave_file("big_alert.wav")
SMALL_BEEP = simpleaudio.WaveObject.from_wave_file("small_alert.wav")


def beep_big():
    BIG_BEEP.play()


def beep_small():
    SMALL_BEEP.play()


async def query_game_state() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(SC2_CLIENT_GAME_ENDPOINT) as response:
            content = await response.text()

    return json.loads(content)

async def poll_for_game_start():
    while True:
        game = await query_game_state()

        if not game["isReplay"] and game["players"]:
            return

        await asyncio.sleep(5)

async def poll_for_start_time():
    while True:
        game = await query_game_state()

        if game["displayTime"] >= START_TIME:
            return

        await asyncio.sleep(0.5)

async def beep_at_intervals():
    last_big_beep = 0
    last_small_beep = 0

    while True:
        game = await query_game_state()

        if not game["players"]:
            return

        display_time = game["displayTime"]

        play_big_beep = display_time - BIG_BEEP_INTERVAL >= last_big_beep
        if play_big_beep:
            last_big_beep = display_time
        
        play_small_beep = display_time - SMALL_BEEP_INTERVAL >= last_small_beep
        if play_small_beep:
            last_small_beep = display_time

        if play_big_beep:
            beep_big()
        elif play_small_beep:
            beep_small()

        await asyncio.sleep(0.5)


def main():
    event_loop = asyncio.get_event_loop()

    while True:
        event_loop.run_until_complete(poll_for_game_start())
        event_loop.run_until_complete(poll_for_start_time())
        event_loop.run_until_complete(beep_at_intervals())


if __name__ == "__main__":
    main()