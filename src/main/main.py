import csv
import sqlite3

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    load_and_clean_users('../../resources/users.csv')
    load_and_clean_call_logs('../../resources/callLogs.csv')
    write_user_analytics('../../resources/userAnalytics.csv')
    write_ordered_calls('../../resources/orderedCalls.csv')

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if len(row) != 2:
                continue
            if any(not col.strip() for col in row):
                continue
            cursor.execute(
                'INSERT INTO users (firstName, lastName) VALUES (?, ?)',
                (row[0].strip(), row[1].strip())
            )
    conn.commit()


# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if len(row) != 5:
                continue
            if any(not col.strip() for col in row):
                continue
            try:
                start_time = int(row[1].strip())
                end_time = int(row[2].strip())
                user_id = int(row[4].strip())
            except ValueError:
                continue
            cursor.execute(
                '''INSERT INTO callLogs (phoneNumber, startTime, endTime, direction, userId)
                   VALUES (?, ?, ?, ?, ?)''',
                (row[0].strip(), start_time, end_time, row[3].strip(), user_id)
            )
    conn.commit()


# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):
    cursor.execute('''
        SELECT userId,
               AVG(endTime - startTime) AS avgDuration,
               COUNT(*) AS numCalls
        FROM callLogs
        GROUP BY userId
        ORDER BY userId
    ''')
    rows = cursor.fetchall()

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['userId', 'avgDuration', 'numCalls'])
        for user_id, avg_duration, num_calls in rows:
            writer.writerow([user_id, float(avg_duration), num_calls])


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):
    cursor.execute('''
        SELECT callId, phoneNumber, startTime, endTime, direction, userId
        FROM callLogs
        ORDER BY userId, startTime
    ''')
    rows = cursor.fetchall()

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['callId', 'phoneNumber', 'startTime', 'endTime', 'direction', 'userId'])
        writer.writerows(rows)



# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()
