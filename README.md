# LSEG Log Monitoring Application

This is a Python application that reads a log file, tracks job durations between their `START` and `END` timestamps, and generates a report classifying each job as:

- OK (≤ 5 minutes)
- WARNING (> 5 and ≤ 10 minutes)
- ERROR (> 10 minutes)

The results are logged to a `job_report.log` file.

---

## Files

- `main.py` – Main application logic
- `logs.log` – Input log file (provided)
- `job_report.log` – Generated output report (created on run)
- `tests/test_main.py` – Unit tests for key functions

---

## How to Run

```
python main.py
```
## How to Run Tests

```
python -m unittest discover tests

```

