from io import BytesIO
import json
from pathlib import Path
from tempfile import gettempdir
from typing import List, Literal, Union
from openai import OpenAI
import os
import dotenv
from rich import print_json
from elevenlabs.client import ElevenLabs
from elevenlabs import play, save
from hd2ainews.src.hd2 import API
from hd2ainews.src.structures import News
from pydub import AudioSegment

dotenv.load_dotenv()


client = OpenAI(base_url=os.getenv("AI_BASE_URL"), api_key=os.getenv("AI_API_KEY"))
MODEL = os.getenv("AI_MODEL")


SYS_PROMPT = """
Info: This is for a game named Helldivers 2. Here is some info about it
Do you believe in freedom? Can you stand in the face of oppression – and defend the defenceless? Can you keep democracy away from these cretins? Wage war for peace. Die for democracy.

Join forces with up to three friends and wreak havoc on an alien scourge threatening the safety of your home planet, Super Earth, in this multiplayer co-op shooter for PS5 and PC from Arrowhead Game Studios.

Step into the boots of the Helldivers, an elite class of soldiers whose mission is to spread freedom, liberty and managed democracy to the galaxy once and for all!

Helldivers don't go planet side without proper backup, but it’s up to you to decide how and when to call it in. Not only do you have a host of superpowered primary weapons and customizable loadouts, you also have the ability to call on stratagems during play.

Helldivers 2 features Arrowhead's best cooperative gameplay yet. Collaboration will be vital: Teams will synergize on loadouts, strategize their approach for each mission and complete objectives together Enlist in Super Earth’s premier military peacekeeping force today. We are heroes… we are legends… WE ARE HELLDIVERS.

Plot
Helldivers 2 is set a century after the triumph of Super Earth, and managed democracy, over the Cyborgs, Terminids, and The Illuminate during the events of the first game. It is discovered that, upon death, the Terminids produce a unique and highly valuable resource E-710. Farms are established on human-colonized worlds, but containment is eventually breached, releasing the bugs and causing chaos and destruction. Simultaneously, a new threat emerges in the form of the Automatons, a mechanical army intent on destroying humanity. The game begins with a recruitment video for the Helldivers[2], who are elite shock troops dropped from orbit to reclaim the colonized lands. Environmental storytelling is prevalent throughout the game, with various logs, notes, and propaganda messages available for players to find during gameplay. The story and progress of the war is told via major orders, timed main objectives within the game.

Only make a script for the news that is provided.

Make a script for the headline listed below news with the following rules:

1. You must have up to 2 news anchors. One named Dave and the other named Joel.
2. No cutaways or extra information.
3. Make the script as short as possible.
4. Be as objective as possible.
5. Try to add some humor to the script.
6. If a major order is included then make a section in the script for it.
7. Dont reply with and markdown format.
8. Only reply in a format like this:

DAVE: {what dave says}
JOEL: {what joel says}
DAVE: {what dave says}
JOEL: {what joel says}
...

9. Do not add any extra information.

You will recieve data like this:
HEADLINe: "Headline"

MAJOR ORDER: "Major order" if there is one
"""

PROMPT = """
Headline: {news}
Major order: {major_order}
"""


def generate_script(news: News | str, major_order: str = None) -> list[dict]:
    if isinstance(news, News):
        news = news.message

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYS_PROMPT,
            },
            {
                "role": "user",
                "content": PROMPT.format(news=news, major_order=major_order),
            },
        ],
    )

    script = resp.choices[0].message.content
    parts = script.strip().splitlines()
    # print_json(data=parts)
    json_parts = []
    for i in parts:
        if i.startswith("JOEL:"):
            json_parts.append({"role": "joel", "content": i.removeprefix("JOEL: ")})

        if i.startswith("DAVE:"):
            json_parts.append({"role": "dave", "content": i.removeprefix("DAVE: ")})

    return json_parts


class Audio:
    def __init__(
        self, raw: bytes, role: Union[Literal["joel"], Literal["dave"]]
    ) -> None:
        self.raw = raw
        self.role = role


def generate_audio(script: list[dict]) -> List[Audio]:
    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    audios: list[dict] = []

    for i in script:
        # print_json(data=i)
        if i["role"] == "joel":
            audio = elevenlabs.generate(
                text=i["content"],
                voice="5Q0t7uMcjvnagumLfvZi",
                model="eleven_monolingual_v1",
            )
            audios.append(Audio(audio, "joel"))
        if i["role"] == "dave":
            audio = elevenlabs.generate(
                text=i["content"],
                voice="Dave",
                model="eleven_monolingual_v1",
            )
            audios.append(Audio(audio, "dave"))

    return audios


def concatenate_audios(audios: List[Audio], output_file: str) -> bytes:
    tempdir = Path(gettempdir())

    for index, item in enumerate(audios):
        save(item.raw, tempdir / f"{index}.mp3")
    segments = []
    for i in tempdir.glob("*.mp3"):
        segments.append(AudioSegment.from_mp3(i))

    merged_audio = sum(segments)
    merged_audio.export(output_file, format="mp3")


def main() -> None:
    api = API()

    news = api.latest_news()
    major_order = api.major_order

    script = generate_script(news, major_order)
    generate_audio(script)
    print_json(data=script)


if __name__ == "__main__":
    main()
