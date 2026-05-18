# Python SQL Call Center Backend

A small Python backend that models a call center: load user and call data from CSV files, store it in an in-memory SQLite database, run analytics with SQL, and export results back to CSV.

## Overview

Full-stack applications split work between a **frontend** (what users see) and a **backend** (data storage and business logic). This project focuses on the backend.

You will:

1. Read and clean data from CSV files
2. Insert valid records into SQLite tables
3. Query the database for analytics and sorted exports
4. Write results to new CSV files

**Technologies:** Python, SQLite, CSV file I/O

## Project structure

```
├── resources/
│   ├── users.csv              # Input: call center agents
│   ├── callLogs.csv           # Input: call records
│   ├── userAnalytics.csv      # Output: per-user call stats
│   └── orderedCalls.csv       # Output: calls sorted by user and time
├── src/
│   ├── main/
│   │   └── main.py            # Application entry point and core logic
│   └── test/
│       ├── lab_test.py        # Unit tests
│       └── test*.csv          # Test fixtures
└── README.md
```

## Database schema

Tables are created in memory when the application starts (`sqlite3.connect(':memory:')`). Primary keys auto-increment when you insert rows without specifying an ID.

### `users`

| Column      | Type    | Notes                    |
|-------------|---------|--------------------------|
| `userId`    | INTEGER | Primary key, auto-increment |
| `firstName` | TEXT    |                          |
| `lastName`  | TEXT    |                          |

### `callLogs`

| Column        | Type    | Notes                              |
|---------------|---------|------------------------------------|
| `callId`      | INTEGER | Primary key, auto-increment        |
| `phoneNumber` | TEXT    |                                    |
| `startTime`   | INTEGER | Unix epoch (seconds)               |
| `endTime`     | INTEGER | Unix epoch (seconds)               |
| `direction`   | TEXT    | e.g. `inbound`, `outbound`         |
| `userId`      | INTEGER | Foreign key → `users.userId`       |

## Features

### 1. Load and clean users (`load_and_clean_users`)

- **Input:** `resources/users.csv` (columns: `firstName`, `lastName`)
- **Action:** Insert rows into `users`, skipping invalid records
- **Validation:** Each row must have exactly 2 fields, and neither field may be empty or whitespace-only

### 2. Load and clean call logs (`load_and_clean_call_logs`)

- **Input:** `resources/callLogs.csv` (columns: `phoneNumber`, `startTime`, `endTime`, `direction`, `userId`)
- **Action:** Insert rows into `callLogs`, skipping invalid records
- **Validation:** Each row must have exactly 5 non-empty fields; `startTime`, `endTime`, and `userId` must be valid integers

### 3. User analytics (`write_user_analytics`)

- **Output:** `resources/userAnalytics.csv`
- **Content:** One row per user with calls in the database

| Column        | Description                                      |
|---------------|--------------------------------------------------|
| `userId`      | User identifier                                  |
| `avgDuration` | Average call length in seconds (`endTime - startTime`) |
| `numCalls`    | Total number of calls                            |

Example:

```csv
userId,avgDuration,numCalls
1,105.0,4
```

### 4. Ordered call logs (`write_ordered_calls`)

- **Output:** `resources/orderedCalls.csv`
- **Content:** All call logs sorted by `userId`, then `startTime` (ascending)
- **Columns:** `callId`, `phoneNumber`, `startTime`, `endTime`, `direction`, `userId`

## Getting started

### Prerequisites

- Python 3.8 or newer

### Run the application

From the `src/main` directory (paths in `main()` are relative to that folder):

```bash
cd src/main
python3 main.py
```

This loads `resources/users.csv` and `resources/callLogs.csv`, then writes `userAnalytics.csv` and `orderedCalls.csv`.

To inspect database contents after a run, uncomment `select_from_users_and_call_logs()` in `main()`.

### Run tests

From the project root:

```bash
# All tests
python3 -m unittest src.test.lab_test -v

# One test at a time
python3 -m unittest src.test.lab_test.ProjectTests.test_users_table_has_clean_data -v
python3 -m unittest src.test.lab_test.ProjectTests.test_calllogs_table_has_clean_data -v
python3 -m unittest src.test.lab_test.ProjectTests.test_user_analytics_are_correct -v
python3 -m unittest src.test.lab_test.ProjectTests.test_call_logs_are_ordered -v
```

## Implementation notes

- Each core function accepts a `file_path` argument so the same code works with `resources/` files in production and `src/test/` fixtures in tests.
- Use parameterized SQL (`?` placeholders) when inserting or querying—do not build SQL strings from raw CSV values.
- Call `conn.commit()` after inserts so data is visible to subsequent queries and tests.
- SQL `ORDER BY` and aggregate functions (`AVG`, `COUNT`, `GROUP BY`) keep export logic simple and reliable.

## Data flow

```
users.csv ──────────► load_and_clean_users ──► users table
                                                    │
callLogs.csv ───────► load_and_clean_call_logs ──► callLogs table
                                                    │
                    ┌───────────────────────────────┤
                    ▼                               ▼
         write_user_analytics              write_ordered_calls
                    │                               │
                    ▼                               ▼
         userAnalytics.csv                 orderedCalls.csv
```
