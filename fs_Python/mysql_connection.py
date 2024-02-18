import mysql.connector
import mysql_details


def get_database_connection():
    host = mysql_details.host
    user = mysql_details.user
    password = mysql_details.password
    database = mysql_details.database

    # Establish a connection to the MySQL server
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    return connection


def initialize_db():
    # Establish a connection to the MySQL server
    connection = get_database_connection()

    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    
    # Commit the changes and close the cursor and connection
    connection.commit()
    cursor.close()
    connection.close()

create_sp_getages = '''
CREATE PROCEDURE GetCustomersByAgeRangeAndSaintStatus
    @min_age INT,
    @max_age INT,
    @saint_status NVARCHAR(50)
AS
BEGIN
    SELECT c.id, c.name, c.age, o.name AS occupation_name, o.isSaint
    FROM customers c
    JOIN occupations o ON c.occupation_id = o.id
    WHERE
        (c.age BETWEEN @min_age AND @max_age)
        AND
        (
            (@saint_status = 'saint' AND o.isSaint = 1)
            OR
            (@saint_status = 'notsaint' AND o.isSaint = 0)
        );
END;
'''







        # create_customers_table = """
    # CREATE TABLE customers (
    #     id INT AUTO_INCREMENT PRIMARY KEY,
    #     name VARCHAR(255) NOT NULL,
    #     age INT NOT NULL,
    #     occupation_id INT,
    #     FOREIGN KEY (occupation_id) REFERENCES occupations(id)
    # );
    # """

    # create_occupations_table = """
    # CREATE TABLE occupations (
    #     id INT AUTO_INCREMENT PRIMARY KEY,
    #     name VARCHAR(255) NOT NULL,
    #     isSaint BOOLEAN NOT NULL
    # );
    # """

    # Execute the SQL statements
    # cursor.execute(create_occupations_table)
    # cursor.execute(create_customers_table)
