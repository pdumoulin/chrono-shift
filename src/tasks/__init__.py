import datetime
import time
from abc import ABC, abstractmethod

from src import config
from src.connectors import nhl, tarantula


class BaseTask(ABC):
    def __init__(self, hour: int, minute: int) -> None:
        self.hour = hour
        self.minute = minute

    def future_executions(self) -> list[datetime.datetime]:
        local_now = datetime.datetime.now(config.TIMEZONE_LOCAL)
        today = local_now.date()
        tomorrow = today + datetime.timedelta(days=1)

        # determine if time (local timezone) was today or tomorrow
        base_date = today
        if local_now.hour >= self.hour and local_now.minute >= self.minute:
            base_date = tomorrow

        # create UTC datetime of next time in future
        result = config.TIMEZONE_LOCAL.localize(
            datetime.datetime.combine(base_date, datetime.time(self.hour, self.minute))
        )
        return [result]

    @abstractmethod
    def execute(self) -> None:
        pass


class PlugsTask(BaseTask):
    def __init__(self, hour: int, minute: int, actions: list[tuple[str, bool]]):
        self.actions = actions
        super().__init__(hour, minute)

    def execute(self) -> None:
        all_plugs = tarantula.list_plugs()
        for action in self.actions:
            action_name = action[0].lower()
            action_bool = action[1]
            plugs = [x for x in all_plugs if action_name in x["name"].lower()]
            for plug in plugs:
                tarantula.update_plug(plug["id"], action_bool)


class SunriseTask(PlugsTask):
    def __init__(self, actions: list[tuple[str, bool]], minute_offset: int = 0) -> None:
        self.offset = minute_offset
        self.actions = actions

    def future_executions(self) -> list[datetime.datetime]:
        # get today's sunrise time
        today = datetime.date.today()
        today_sunrise = config.SUN.get_sunrise_time(today)

        # get tomorrow's sunrise time
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_sunrise = config.SUN.get_local_sunrise_time(tomorrow)

        # find next sunrise time
        now = datetime.datetime.now(config.TIMEZONE_UTC)
        next_sunrise = tomorrow_sunrise if now > today_sunrise else today_sunrise

        # adjust time offset
        offset_next_sunrise = next_sunrise + datetime.timedelta(minutes=self.offset)

        return [offset_next_sunrise]


class SunsetTask(PlugsTask):
    def __init__(self, actions: list[tuple[str, bool]], minute_offset: int = 0) -> None:
        self.offset = minute_offset
        self.actions = actions

    def future_executions(self) -> list[datetime.datetime]:
        # get today's sunset time
        today = datetime.date.today()
        today_sunset = config.SUN.get_sunset_time(today)

        # get tomorrow's sunset time
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_sunset = config.SUN.get_local_sunset_time(tomorrow)

        # find next sunset time
        now = datetime.datetime.now(config.TIMEZONE_UTC)
        next_sunset = tomorrow_sunset if now > today_sunset else today_sunset

        # adjust time offset
        offset_next_sunset = next_sunset + datetime.timedelta(minutes=self.offset)

        return [offset_next_sunset]


class NhlGameStartTask(BaseTask):
    def __init__(self, team: str) -> None:
        self.team = team

    def future_executions(self) -> list[datetime.datetime]:
        today = datetime.datetime.today().date()
        games = nhl.get_schedule(today, self.team)

        # filter games based on team and start time
        game_times = []
        for game in games:
            # calculate seconds in future from now
            game_start = datetime.datetime.strptime(
                game["startTimeUTC"], "%Y-%m-%dT%H:%M:%SZ"
            ).astimezone(config.TIMEZONE_UTC)
            start_diff = int(
                (
                    game_start - datetime.datetime.now(config.TIMEZONE_UTC)
                ).total_seconds()
            )

            # is game in next 24hr
            if start_diff >= 0 and start_diff <= 86400:
                game_times.append(game_start)

        return game_times

    def execute(self) -> None:
        plugs = tarantula.list_plugs(name_filter=["goal"])
        for plug in plugs:
            tarantula.update_plug(plug["id"], True)
        time.sleep(15)
        for plug in plugs:
            tarantula.update_plug(plug["id"], False)
