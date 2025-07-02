"""Schedule-able tasks."""

import datetime
import time

from src import config
from src.connectors import nhl
from src.connectors import tarantula


class BaseTask(object):
    """Basic task run at local time."""

    def __init__(self, hour: int, minute: int):
        """Initialize task object.

        Args:
            hour (int): hour to run (local time)
            minute (int): minute to run (local time)
        """
        self.hour = hour
        self.minute = minute

    def future_executions(self) -> list[datetime.datetime]:
        """Calculate first next time in future.

        Returns:
            list: single item, datetime of next time
        """
        local_now = datetime.datetime.now(config.TIMEZONE_LOCAL)
        today = local_now.date()
        tomorrow = today + datetime.timedelta(days=1)

        # determine if time (local timezone) was today or tomorrow
        base_date = today
        if local_now.hour >= self.hour and local_now.minute >= self.minute:
            base_date = tomorrow

        # create UTC datetime of next time in future
        result = config.TIMEZONE_LOCAL.localize(
            datetime.datetime.combine(
                    base_date,
                    datetime.time(self.hour, self.minute)
            )
        )
        return [result]

    def execute(self) -> None:
        """Run function when schedule occurs."""
        raise NotImplementedError('execute()')


class SunriseTask(BaseTask):
    """Run task at sunrise."""

    def __init__(self, minute_offset: int = 0):
        """Initialize task.

        Args:
            minute_offset (int): minutes to move task schedule
        """
        self.offset = minute_offset

    def future_executions(self) -> list[datetime.datetime]:
        """Calculate first next sunset in future.

        Returns:
            list: single item, datetime of next sunrise

        """
        # get today's sunrise time
        today = datetime.date.today()
        today_sunrise = config.SUN.get_sunrise_time(today)

        # get tomorrow's sunrise time
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_sunrise = config.SUN.get_local_sunrise_time(tomorrow)

        # find next sunrise time
        now = datetime.datetime.now(config.TIMEZONE_UTC)
        next_sunrise = tomorrow_sunrise if now > today_sunrise else today_sunrise  # noqa:E501

        # adjust time offset
        offset_next_sunrise = \
            next_sunrise + datetime.timedelta(minutes=self.offset)

        return [offset_next_sunrise]

    def execute(self) -> None:
        """Turn off lights at sunrise."""
        for plug in tarantula.list_plugs():
            if 'porch lights' in plug['name'].lower():
                tarantula.update_plug(plug['id'], False)
            elif 'air conditioner' in plug['name'].lower():
                tarantula.update_plug(plug['id'], True)


class SunsetTask(BaseTask):
    """Run task at sunset."""

    def __init__(self, minute_offset: int = 0):
        """Initialize task.

        Args:
            minute_offset (int): minutes to move task schedule
        """
        self.offset = minute_offset

    def future_executions(self) -> list[datetime.datetime]:
        """Calculate first next sunset in future.

        Returns:
            list: single item, datetime of next sunset
        """
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
        offset_next_sunset = \
            next_sunset + datetime.timedelta(minutes=self.offset)

        return [offset_next_sunset]

    def execute(self) -> None:
        """Turn on lights."""
        match_names = ['christmas tree', 'porch lights']
        plugs = tarantula.list_plugs(name_filter=match_names)
        for plug in plugs:
            tarantula.update_plug(plug['id'], True)


class NhlGameStartTask(BaseTask):
    """Run task on NHL game start."""

    def __init__(self, team: str) -> None:
        """Initialize task object.

        Args:
            team (str): team 3-letter code to run task for
        """
        self.team = team

    def future_executions(self) -> list[datetime.datetime]:
        """Calculate game time(s) in next 24hr.

        Returns:
            list: datetimes of games in next 24hr
        """
        today = datetime.datetime.today().date()
        games = nhl.get_schedule(str(today), self.team)

        # filter games based on team and start time
        game_times = []
        for game in games:

            # calculate seconds in future from now
            game_start = datetime.datetime.strptime(game['startTimeUTC'], '%Y-%m-%dT%H:%M:%SZ').astimezone(config.TIMEZONE_UTC)  # noqa:E501
            start_diff = int((game_start - datetime.datetime.now(config.TIMEZONE_UTC)).total_seconds())  # noqa:E501

            # is game in next 24hr
            if start_diff >= 0 and start_diff <= 86400:
                game_times.append(game_start)

        return game_times

    def execute(self) -> None:
        """Burst goal lights."""
        plugs = tarantula.list_plugs(name_filter=['goal'])
        for plug in plugs:
            tarantula.update_plug(plug['id'], True)
        time.sleep(15)
        for plug in plugs:
            tarantula.update_plug(plug['id'], False)
