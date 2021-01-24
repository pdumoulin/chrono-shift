"""Schedule-able tasks."""

import datetime

from blinky import Wemo

import config

from connectors.nhl import get_schedule as get_nhl_schedule


class BaseTask(object):
    """Basic task run at local time."""

    def __init__(self, hour, minute):
        """Initialize task object.

        Args:
            hour (int): hour to run (local time)
            minute (int): minute to run (local time)
        """
        self.hour = hour
        self.minute = minute

    def future_executions(self):
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

    def execute(self):
        """Run function when schedule occurs."""
        raise NotImplementedError('execute()')


class BedtimeTask(BaseTask):
    """Run task at bedtime."""

    def execute(self):
        """Turn off balcony lights."""
        switch = Wemo(config.BALCONY_IP)
        switch.off()


class SunsetTask(BaseTask):
    """Run task at sunset."""

    def __init__(self):
        """Override base, no inputs needed."""
        pass

    def future_executions(self):
        """Calculate first next sunset in future.

        Returns:
            list: single item, datetime of next sunset
        """
        # get today's sunset time
        today = datetime.date.today()
        today_sunset = config.SUN.get_sunset_time(today)

        # get tomorrow's sun set time
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_sunset = config.SUN.get_local_sunset_time(tomorrow)

        # find next sunset time
        now = datetime.datetime.now(config.TIMEZONE_UTC)
        next_sunset = tomorrow_sunset if now > today_sunset else today_sunset
        return [next_sunset]

    def execute(self):
        """Turn on balcony lights."""
        switch = Wemo(config.BALCONY_IP)
        switch.on()


class NhlGameStartTask(BaseTask):
    """Run task on NHL game start."""

    def __init__(self, team):
        """Initialize task object.

        Args:
            team (str): team name to run task for
        """
        self.team = team

    def future_executions(self):
        """Calculate game time(s) in next 24hr.

        Returns:
            list: datetimes of games in next 24hr
        """
        # fetch 3 day window to prevent time zone problems
        today = datetime.datetime.today().date()
        yesterday = today + datetime.timedelta(days=-1)
        tomorrow = today + datetime.timedelta(days=1)
        games = get_nhl_schedule(str(yesterday), str(tomorrow))

        # filter games based on team and start time
        game_times = []
        for game in games:

            # is game for relevant team
            home_team = game['teams']['home']['team']['name'].lower()
            away_team = game['teams']['away']['team']['name'].lower()

            if self.team.lower() == home_team or self.team.lower() == away_team:  # noqa:E501

                # calculate seconds in future from now
                game_start = datetime.datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ').astimezone(config.TIMEZONE_UTC)  # noqa:E501
                start_diff = int((game_start - datetime.datetime.now(config.TIMEZONE_UTC)).total_seconds())  # noqa:E501

                # is game in next 24hr
                if start_diff >= 0 and start_diff <= 86400:
                    game_times.append(game_start)

        return game_times

    def execute(self):
        """Burst goal lights."""
        switch = Wemo(config.GOAL_IP)
        switch.burst(15)
