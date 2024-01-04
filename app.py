from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from urllib.error import HTTPError

app = Flask(__name__)

dialect_driver = 'postgresql'
username = 'postgres'
password = "p23a"
host = 'localhost'
dbname = 'capacity'

db_credentials = f"{dialect_driver}://{username}:{password}@{host}/{dbname}"

app.config['SQLALCHEMY_DATABASE_URI'] = db_credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def create_table():
    db.create_all()


def send_to_db(df):
    """Updates database"""
    for index, row in df.iterrows():
        new_entry = Countries(country=row['country'],
                              capacity=row['capacity'],
                              date=row['date'])
        db.session.add(new_entry)
    db.session.commit()


def open_file(file_name, mode):
    """Checks if the correct file exists"""
    try:
        with open(file_name, mode) as f:
            mydict = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_name} was not found.")
    return mydict


def get_countries(mydict):
    """Loads the file and shows the names of the countries
    in alphabetical order.
    """
    keys = sorted(list(mydict.keys()))
    keys.insert(0, "-----  COUNTRY ")
    countries = mydict
    return countries, keys


MYFILE = "countries_dict.json"
ADDRESS = 'http://stadiony.net/stadiony/'

mydict = open_file(MYFILE, "r")
countries, keys = get_countries(mydict)


@app.route('/', methods=['GET'])
def capacity():
    create_table()
    return render_template('index.html', countries=keys)


@app.route('/cap', methods=['POST'])
def capacity_result():

    def get_address(countries, selected, address):
        """Returns the address of the selected country"""
        code = countries.get(selected)
        cou = pd.read_html(address+code)
        return cou

    def league_level(country):
        """Determines which table relates to the best league"""
        if len(country[0]) < 3:
            std = country[1]
        else:
            std = country[0]
        return std

    def avg_capacity(df):
        """
        Modifies selected dataframe &
        calculates the average for a given league.
        """
        df.columns = ['Name', 'City', 'Club', 'Capacity']
        df['Capacity'] = df['Capacity'].str.replace(" ", "")
        df['Capacity'] = df['Capacity'].astype('int64')
        cap = round(df['Capacity'].mean())
        return cap

    def format_capacity(capacity):
        """Formats the Capacity column"""
        return f"{capacity // 1000:,} {capacity % 1000:03d}"

    country1 = request.form.get("country1")
    country2 = request.form.get("country2")
    country3 = request.form.get("country3")
    country4 = request.form.get("country4")
    country5 = request.form.get("country5")

    countries_selected = [country1, country2, country3, country4, country5]

    if not all(elem in countries for elem in countries_selected):
        print("Not all countries selected!")
        error_message = "All five countries must be selected"
        return render_template('index.html', countries=keys,
                               error_message=error_message)

    df_list = []
    number = 0

    for n in countries_selected:
        selected = n
        try:
            myaddress = get_address(countries, selected, ADDRESS)
        except (HTTPError, ImportError):
            country_error = (
                "Source website error. "
                "Please try again later or select a country other than "
                + n + "."
                )
            return render_template('index.html', countries=keys,
                                   country_error=country_error)

        division = league_level(myaddress)
        capacity = avg_capacity(division)
        dic = {'League': selected, 'Capacity': capacity}
        df_list.append(dic)
        number += 1

    new_df = pd.DataFrame.from_records(df_list)
    new_df = new_df.sort_values(by=['Capacity'],
                                ascending=False).reset_index(drop=True)
    new_df['Rank'] = [1, 2, 3, 4, 5]
    new_df = new_df[['Rank', 'League', 'Capacity']]
    highest = new_df.iloc[0]['League']

    db_df = new_df.copy()
    db_df['date'] = datetime.now()
    db_df['date'] = pd.to_datetime(db_df["date"].dt.strftime('%Y-%m-%d'))
    db_df = db_df.rename(columns={'League': 'country', 'Capacity': 'capacity'})
    db_df = db_df.drop('Rank', axis=1)

    new_df['Capacity'] = new_df['Capacity'].apply(format_capacity)

    if len(countries_selected) != len(set(countries_selected)):
        error_statement = "You cannot select a country more than once!"
        print(error_statement)
        return render_template('index.html',
                               countries=keys, error_statement=error_statement)
    else:
        send_to_db(db_df)
        return render_template('cap.html',
                               tables=[new_df.to_html(index=False)],
                               highest=highest)


if __name__ == '__main__':
    app.run(debug=True)
