import sqlite3

# Connect to the database
eins_connection = sqlite3.connect('Eins.db')
ibs_connection = sqlite3.connect('Ibs.db')


# Retrieve data from the database
eins_cursor = eins_connection.cursor()
ibs_cursor = eins_connection.cursor()

# Test run querying of data from a table
eins_cursor.execute("SELECT * FROM Request_Criteria")

# Fetch all the rows and print them
rows = eins_cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
eins_connection.close()
