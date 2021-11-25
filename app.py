from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)


@app.route("/")
def index():
    return "hello"


@app.route("/post", methods=["POST", "GET"])
def t():
    if request.method == 'POST':
        print(request.args)
        print(request.values)
        print(request.json)
        print(request.args.get("data"))
        return 'test'
    else:
        return 'test'


@app.route("/save_scraped_city", methods=["POST"])
def save_scraped_city():
    """
    function to save scraped city name
    :return: dict
    """
    if request.method == 'POST':
        data = request.json
        city = data['city'].lower()
        state = data['state'].lower()
        # executing query
        query = f"""UPDATE cities SET scraped = True WHERE city_name = {city}, state_name = {state}"""
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

        return jsonify({'success': True})


@app.route("/update_result_range", methods=["POST"])
def update_result_range():
    if request.method == 'POST':
        data = request.json
        city = data['json']
        state = data['state']
        result_range = data['last_result_range']
        # executing query
        query = f"""UPDATE cities SET last_result_range = {result_range} WHERE city_name = {city}, state_name = {state}"""
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

        return jsonify({'success': True})

@app.route("/save_scraped_data", methods=["POST"])
def save_scraped_data():
    if request.method == "POST":
        data = request.json
        # converting json data to suitable form so we can save it in db
        data = data['data']
        shop_name = data['name'][0]
        address = data['address']
        located_in = data['located in']
        phone = data['phone number']
        n_of_reviews = data['total number of reviews']
        website = data['website']
        plus_code = data['plus code']
        shop_url = data['shop url']

        get_data = lambda x: ", ".join(list(set([i.strip() for i in ", ".join(x).split(",")])))

        # for social contacts
        facebook = get_data(data['social_contacts']['facebook'])
        instagram = get_data(data['social_contacts']['instagram'])
        twitter = get_data(data['social_contacts']['twitter'])
        linkedin = get_data(data['social_contacts']['twitter'])
        email = get_data(data['social_contacts']['email'])

        # saving data in db
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        # query to save data to db
        query = f"""
        INSERT INTO scraped_data(shop_name, address, located_in, phone,
         n_of_reviews, website, plus_code, shop_url, facebook, instagram, twitter, linkedin, email) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
         """
        values = [shop_name, address, located_in, phone,
          n_of_reviews, website, plus_code, shop_url, facebook,
           instagram, twitter, linkedin, email]
        for i in range(len(values)):
            values[i] = str(values[i])
        try:
            cursor.execute(query, values)
            response = {'success': True, 'message': "Data saved successfully."}
        except Exception as ex:
            response = {'success': False, 'message': f'An error occurred: {ex}'}
        conn.commit()
        conn.close()

        return jsonify(response)


def create_tables():
    """
    function to create tables in db
    :return: None
    """
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraped_data (
        id INTEGER PRIMARY KEY,
        shop_name TEXT,
        address TEXT,
        located_in TEXT,
        phone TEXT,
        n_of_reviews TEXT,
        website TEXT,
        plus_code TEXT,
        shop_url TEXT,
        facebook TEXT,
        instagram TEXT,
        twitter TEXT,
        linkedin TEXT,
        email TEXT
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY,
        city_name TEXT,
        state_name TEXT,
        country_name TEXT,
        scraped boolean,
        last_result_range TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/get_city", methods=["GET"])
def get_city():
    """
    function to get city name from database
    :return: dict
    """
    if request.method == 'GET':
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cities WHERE scraped=False LIMIT 1")
        data = cursor.fetchall()
        conn.close()
        if not len(data) > 0:
            return jsonify({'success': False, 'message': 'No city found.'})
        # converting data to dict
        if isinstance(data, list):
            data = data[0]
        data_dict = {
            'id': data[0],
            'city_name': data[1],
            'state_name': data[2],
            'country_name': data[3],
            'scraped': True if int(data[4]) == 1 else False,
            'last_result_range': data[5]
        }
        return jsonify({'success': True, 'data': data_dict})


def run_app():
    """ function to execute flask app """
    app.run(debug=False)


if __name__ == '__main__':
    run_app()
