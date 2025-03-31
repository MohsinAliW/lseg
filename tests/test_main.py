import unittest
import datetime
from unittest.mock import patch
from main import parse_line, time_to_seconds, process_log_line

class TestLogMonitor(unittest.TestCase):
    def test_parse_line_valid(self):
        line = "12:15:09,scheduled task 531, END,62922"
        result = parse_line(line)
        self.assertIsNotNone(result)
        dt_time, description, event, pid = result
        self.assertEqual(dt_time, datetime.time(12, 15, 9))
        self.assertEqual(description, "scheduled task 531")
        self.assertEqual(event, "END")
        self.assertEqual(pid, "62922")

    def test_parse_line_invalid(self):
        malformed_line = "bad_line_without_commas"
        result = parse_line(malformed_line)
        self.assertIsNone(result)

    def test_time_to_seconds(self):
        t = datetime.time(1, 1, 1)  # 1 hour, 1 minute, 1 second
        self.assertEqual(time_to_seconds(t), 3661)

    @patch("main.logging")
    def test_duration_logic_warning(self, mock_logging):
        jobs = {
            "12345": (datetime.time(10, 0, 0), "test task")
        }
        end_time = datetime.time(10, 6, 0)  # 6 minutes later

        process_log_line(jobs, end_time, "test task", "END", "12345")

        mock_logging.warning.assert_called_with(
            "Job (PID=12345, 'test task') took 6min 0s"
        )

    @patch("main.logging")
    def test_duration_logic_error(self, mock_logging):
        jobs = {
            "67890": (datetime.time(10, 0, 0), "long task")
        }
        end_time = datetime.time(10, 11, 0)  # 11 minutes later

        process_log_line(jobs, end_time, "long task", "END", "67890")

        mock_logging.error.assert_called_with(
            "Job (PID=67890, 'long task') took 11min 0s"
        )

    @patch("main.logging")
    def test_duration_logic_info(self, mock_logging):
        jobs = {
            "54321": (datetime.time(10, 0, 0), "quick task")
        }
        end_time = datetime.time(10, 2, 0)  # 2 minutes later

        process_log_line(jobs, end_time, "quick task", "END", "54321")

        mock_logging.info.assert_called_with(
            "Job (PID=54321, 'quick task') took 2min 0s"
        )

if __name__ == '__main__':
    unittest.main()
