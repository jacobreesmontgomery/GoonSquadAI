from datetime import timedelta, time
from typing import Tuple  # Keep only what's necessary

from .simple_logger import SimpleLogger

logger = SimpleLogger(class_name=__name__).logger


class Formatter:
    def get_index_of_key(self, dictionary: dict, key_to_find: any) -> int:
        """
        Finds the index of a specific key in a dictionary.

        :param dictionary: The dictionary to search through.
        :param key_to_find: The key to find in the dictionary.

        :return: The index of the key if found, -1 otherwise.
        """
        logger.debug(
            f"START of get_index_of_key() w/ arg(s)...\n\tdictionary: {dictionary}\n\tkey_to_find: {key_to_find}"
        )
        index = 0
        for key in dictionary:
            if int(key) == int(key_to_find):
                logger.debug(
                    f"END of get_index_of_key() w/ return(s)...\n\tindex: {index}\n"
                )
                return index
            index += 1
        logger.debug(f"END of get_index_of_key() w/ return(s)...\n\tindex: -1\n")
        return -1  # Key not found in the dictionary

    def format_seconds(self, seconds: timedelta) -> Tuple[str, time]:
        """
        Formats seconds to the format of HH:MM:SS and returns a tuple of the formatted string and a time object.

        :param seconds: A timedelta object representing a duration in seconds.

        :return: A tuple containing the formatted time string (HH:MM:SS) and a time object.
        """
        logger.debug(f"\nSTART of format_seconds() w/ arg(s)...\n\tseconds: {seconds}")

        # Calculate hours, minutes, and remaining seconds
        hours, remainder = divmod(seconds.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        # Create the formatted string
        str_formatted_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

        # Create a time object
        time_obj = time(hour=int(hours), minute=int(minutes), second=int(seconds))

        logger.debug(
            f"\nEND of format_seconds() w/ return(s)...\n\tformatted_time: {str_formatted_time}\n\ttime_obj: {time_obj}\n"
        )
        return str_formatted_time, time_obj

    def calculate_pace(
        self, total_seconds: float, distance_miles: float
    ) -> Tuple[str, time]:
        """
        Calculates pace (MM:SS) using the total seconds and distance of the run (mi).

        :param total_seconds: The total duration of the activity in seconds.
        :param distance_miles: The distance of the activity in miles.

        :return: A tuple containing the formatted pace string (MM:SS) and a time object.
        """
        logger.debug(
            f"\nSTART of calculate_pace() w/ arg(s)...\n\ttotal_seconds: {total_seconds}\n\tdistance_miles: {distance_miles}"
        )
        # Convert total seconds to minutes
        total_minutes = total_seconds / 60

        # Calculate pace in minutes per mile
        pace_minutes_per_mile = total_minutes / distance_miles

        # Convert pace to MM:SS format
        pace_seconds = int(pace_minutes_per_mile * 60)
        minutes, seconds = divmod(pace_seconds, 60)

        str_formatted_moving_time = f"{minutes:02d}:{seconds:02d}"
        moving_time_obj = time(minute=minutes, second=seconds)

        logger.debug(
            f"\nEND of calculate_pace() w/ return(s)...\n\t{minutes:02d}:{seconds:02d}\n"
        )
        return str_formatted_moving_time, moving_time_obj

    def format_to_hhmmss(self, time_str: str) -> str:
        """
        Format a string to HH:MM:SS ensuring each part has two digits.

        :param time_str: A string representing time in the format H:M:S or similar.

        :return: A formatted string in the format HH:MM:SS.
        """
        logger.debug(
            f"\nSTART of format_to_hhmmss() w/ arg(s)...\n\ttime_str: {time_str}"
        )
        # Split the time string by colon
        parts = time_str.split(":")

        if len(parts) != 3:
            raise ValueError(f"Incorrect time format: {time_str}")

        # Pad each part with leading zeros to ensure two digits
        hours = parts[0].zfill(2)
        minutes = parts[1].zfill(2)
        seconds = parts[2].zfill(2)

        # Join the parts back together with colons
        formatted_time = f"{hours}:{minutes}:{seconds}"
        logger.debug(
            f"END of format_to_hhmmss() w/ return(s)...\n\tformatted_time: {formatted_time}\n"
        )
        return formatted_time

    def time_str_to_seconds(self, time_str: str) -> int:
        """
        Converts a time string in the format HH:MM:SS to total seconds.

        :param time_str: A string representing time in the format HH:MM:SS.

        :return: Total seconds as an integer.
        """
        hours, minutes, seconds = map(int, time_str.split(":"))
        return hours * 3600 + minutes * 60 + seconds

    def divide_time_by_number(self, time_str: str, divisor: float) -> float:
        """
        Divides a time string by a number and returns the result in seconds.

        :param time_str: A string representing time in the format HH:MM:SS.
        :param divisor: The number to divide the time by.

        :return: The result in seconds as a float.
        """
        total_seconds = self.time_str_to_seconds(time_str)
        divided_seconds = total_seconds / divisor
        return divided_seconds

    def seconds_to_time_str(self, total_seconds: float) -> str:
        """
        Converts total seconds to a time string in the format HH:MM:SS.

        :param total_seconds: The total number of seconds to convert.

        :return: A formatted time string in the format HH:MM:SS.
        """
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds % 3600) / 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def divide_time_str_by_number(self, time_str: str, divisor: float) -> str:
        """
        Divides a time string by a number and returns the result as a time string.

        :param time_str: A string representing time in the format HH:MM:SS.
        :param divisor: The number to divide the time by.

        :return: A formatted time string in the format HH:MM:SS.
        """
        total_seconds = self.time_str_to_seconds(time_str)
        divided_seconds = total_seconds / divisor
        return self.seconds_to_time_str(divided_seconds)

    def tally_time(self, run_times: list[str]) -> Tuple[timedelta, str]:
        """
        Tallies up all of the incoming run's times to calculate total duration.

        :param run_times: A list of time strings in the format H:M:S or similar.

        :return: A tuple containing a timedelta object of the total duration and its string representation.
        """
        logger.debug(
            f"\nSTART of tally_time() w/ argument(s): \n\trun_times: {run_times}"
        )
        total_duration = timedelta(hours=0, minutes=0, seconds=0)
        for time in run_times:
            time = self.format_to_hhmmss(time_str=time)
            if len(time) != 8 or time[2] != ":" or time[5] != ":":
                raise ValueError(f"Incorrect time format: {time}")
            total_duration = total_duration + timedelta(
                hours=int(time[:2]), minutes=int(time[3:5]), seconds=int(time[6:])
            )
        logger.debug(
            f"END of tally_time() w/ return(s)... \n\ttotal_duration: {total_duration}\n\tstr(total_duration): {str(total_duration)}\n"
        )
        return total_duration, str(total_duration)
