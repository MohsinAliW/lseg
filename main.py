import datetime
import logging
from typing import Dict, Tuple

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("job_report.log"),
    ]
)

def parse_line(line: str):
    """
    Given a single log line (CSV-style),
    split it into timestamp, description, event_type, pid.
    Returns a datetime.time object, description string, event string, pid string.
    """
    parts = line.strip().split(',')
    if len(parts) < 4:
        # In case there's a malformed line, handle or skip it
        logging.warning(f"Malformed line (skipping): {line}")
        return None

    timestamp_str = parts[0].strip()
    description = parts[1].strip()
    event_type = parts[2].strip().upper()  # "START" or "END"
    pid = parts[3].strip()

    # Convert "HH:MM:SS" -> datetime.time
    hours_str, minutes_str, seconds_str = timestamp_str.split(':')
    hours = int(hours_str)
    minutes = int(minutes_str)
    seconds = int(seconds_str)

    dt_time = datetime.time(hours, minutes, seconds)

    return dt_time, description, event_type, pid

def time_to_seconds(t: datetime.time) -> int:
    """Converts a datetime.time to the number of seconds past midnight."""
    return t.hour * 3600 + t.minute * 60 + t.second

def process_log_line(jobs_in_progress: Dict[str, Tuple[datetime.time, str]],
                     dt_time: datetime.time,
                     description: str,
                     event_type: str,
                     pid: str):
    """
    Handles a single parsed log line. If it's a START event, store it;
    if it's an END, compute duration and log result.
    """
    if event_type == "START":
        # Store the start time and description
        jobs_in_progress[pid] = (dt_time, description)
    elif event_type == "END":
        start_time, job_description = jobs_in_progress[pid]
        duration_seconds = time_to_seconds(dt_time) - time_to_seconds(start_time)
        
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60

        # Determine whether it's an error, warning, or OK
        if duration_seconds > 600:
            logging.error(f"Job (PID={pid}, '{job_description}') took {minutes}min {seconds}s")
        elif duration_seconds > 300:
            logging.warning(f"Job (PID={pid}, '{job_description}') took {minutes}min {seconds}s")
        else:
            logging.info(f"Job (PID={pid}, '{job_description}') took {minutes}min {seconds}s")

        del jobs_in_progress[pid]

def main(log_file_path: str):
    """Reads the log file, processes each line, and logs the results."""
    jobs_in_progress = {}  # PID -> (start_time, description)
    
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            parsed = parse_line(line)
            if not parsed:
                # The line was invalid or malformed
                continue
            dt_time, description, event_type, pid = parsed
            process_log_line(jobs_in_progress, dt_time, description, event_type, pid)

    # If a job never ended, we log it here
    for pid, (start_time, description) in jobs_in_progress.items():
        logging.warning(f"PID={pid}, '{description}' has no END record in the log file")

if __name__ == "__main__":
    log_path = "logs.log" 
    main(log_path)
