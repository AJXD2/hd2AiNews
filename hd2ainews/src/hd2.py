import requests
import re
from hd2ainews.src.structures import News
from rich.markup import render as render_markup


class API:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers = {
            "X-Super-Contact": "aj@ajxd2.dev - DISCORD: ajxd2",
            "X-Super-Client": "AJXD2-HD2AINEWS(:D)",
            "User-Agent": "AJXD2-HD2AINEWS(:D)",
        }
        self.cache = {}

    def _check_status(self) -> bool:
        resp = self._make_request(f"https://api.diveharder.com/", return_json=False)
        if resp.status_code != 200 or resp.json().get("msg") is None:
            return False

        return True

    def _make_request(
        self, url: str, return_json: bool = True
    ) -> dict | requests.Response:
        resp = self.s.get(url)
        if resp.status_code != 200:
            raise Exception(resp.text)

        return resp.json() if return_json else resp

    def _get_update(self):

        return self._make_request(f"https://api.diveharder.com/v1/all")

    def news(self, raw: bool = False):
        resp = self._make_request(f"https://api.diveharder.com/v1/news_feed")

        if raw:

            return resp
        news = [News(**i) for i in resp]
        return news

    def latest_news(self):
        news = self.news(raw=True)

        return News(**news[-1])

    @property
    def major_order(self):
        resp = self._make_request(f"https://api.diveharder.com/v1/major_order")
        return resp[0].get("setting", {}).get("overrideBrief", "")

    @property
    def war_info(self):
        resp = self._make_request(f"https://api.diveharder.com/v1/war_info")

        return resp

    def get_war_status(self):
        pass

    @classmethod
    def fix_timestamp(cls, timestamp: float):
        # Epoch Start time + War Start Date + Time

        data = cls()._get_update()
        start_date = data.get("war_info").get("startDate", 0)
        now = data.get("status", {}).get("time", 0)

        return start_date + now + timestamp


def HDML_to_md(text: str) -> str:
    format_mapping = {
        "<i=3>": "[b]",  # Bold
        "</i=3>": "[b]",  # bold again?
        "<i=1>": "[yellow]",  # Yellow text
        "</i>": "[/]",  # Closing tag
    }

    for code, markup in format_mapping.items():

        text = text.replace(code, markup)

    return text


def main() -> None:
    api = API()

    for i in api.get_news():
        print(i)


if __name__ == "__main__":
    main()
