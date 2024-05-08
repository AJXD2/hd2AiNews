from os import path
from tempfile import gettempdir
from dotenv import load_dotenv
from elevenlabs import save

from hd2ainews.src.hd2 import API, News, HDML_to_md
from rich import print as pprint
from hd2ainews.src.aiscript import generate_script, generate_audio, concatenate_audios
from rich.status import Status

load_dotenv()


def main() -> None:
    api = API()
    latest = api.latest_news()
    pprint(HDML_to_md(latest.message))
    pprint(f"Major Order: {api.major_order}")
    with Status(f"Generating script... "):
        script = generate_script(latest)
    with Status("Generating audio..."):
        audios = generate_audio(script)
    with Status("Saving audio..."):
        concatenate_audios(audios, "merged_audio.mp3")


if __name__ == "__main__":
    main()
