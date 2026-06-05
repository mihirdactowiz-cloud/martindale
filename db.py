import json
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="actowiz",
        database="martindale_new",
    )

def fetch_firmlinks_batch(start, end):
    conn = get_connection()
    mycursor = conn.cursor(dictionary=True)

    query = """
        SELECT id,link, city, state, category
        FROM unique_oranization_link
        WHERE status = 0
          AND id BETWEEN %s AND %s
    """

    mycursor.execute(query, (start, end))
    rows = mycursor.fetchall()

    mycursor.close()
    conn.close()

    return rows

def update_firmlink_status(id):
    conn = get_connection()
    mycursor = conn.cursor(dictionary=True)

    query = """
    UPDATE unique_oranization_link
    SET status = 1
    WHERE id = %s
    """

    mycursor.execute(query, (id,))
    conn.commit()
    mycursor.close()
    conn.close()


def create_state_table():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS DATA_final (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url TEXT,
        title VARCHAR(255),
        address TEXT,
        city VARCHAR(50),
        state VARCHAR(50),
        category VARCHAR(255),
        rating_value VARCHAR(10),
        review_count VARCHAR(10),
        worst_rating VARCHAR(10),
        best_rating VARCHAR(10),
        contact VARCHAR(255),
        website_url TEXT,
        details TEXT,
        areas_of_practice JSON,
        total_people_count INT,
        attorneys JSON
    )
    """

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    print("DATA table verified/created successfully.")


def insert_scraped_data(data, city, state, category):
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO DATA_final (
        url, title, address, city, state, category, rating_value, 
        review_count, worst_rating, best_rating, contact, website_url, 
        details, areas_of_practice, total_people_count, attorneys
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data.get("url"),
        data.get("title"),
        json.dumps(data.get("address", [])),
        city,
        state,
        category,
        data.get("rating_value"),
        data.get("review_count"),
        data.get("worst_rating"),
        data.get("best_rating"),
        data.get("contact"),
        data.get("website_url"),
        data.get("details"),
        json.dumps(data.get("areas_of_practice", [])),
        data.get("total_people_count"),
        json.dumps(data.get("attorneys", [])),
    )

    try:
        cursor.execute(insert_query, values)
        conn.commit()
        print(f"Successfully saved data to database for: {data.get('title')}")
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_state_table()