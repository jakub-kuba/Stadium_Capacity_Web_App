from flask import Flask, render_template, request
import pandas as pd
import json
import sys

app = Flask(__name__)


def open_file(file_name, mode):
    """Check if the correct file exists"""
    try:
        with open(file_name, mode) as f:
            json.load(f)
    except FileNotFoundError:
        print("\nThe file not found. The program has quit.\n")
        sys.exit()


def get_countries(myfile):
    """Load the file and show the names of the countries
    in alphabetical order.
    """
    with open(myfile, "r") as f:
        mydict = json.load(f)
    keys = sorted(list(mydict.keys()))
    keys.insert(0, "-----  COUNTRY ")
    countries = mydict
    return countries, keys


MYFILE = "countries_dict.json"
ADDRESS = 'http://stadiony.net/stadiony/'

open_file(MYFILE, "r")
countries, keys = get_countries(MYFILE)


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/', methods=['GET'])
def capacity():
    return render_template('index.html', countries=keys)


@app.route('/cap', methods=['POST'])
def capacity_result():

    def create_df():
        """Creates dataframe with two columns"""
        column_names = ['League', 'Capacity']
        new_df = pd.DataFrame(columns=column_names)
        new_df['Capacity'] = new_df['Capacity'].astype('int32')
        return new_df
    

    def get_address(countries, selected, address):
        """Returns the address of the selected country."""
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
        """Modifies selected dataframe & calculates the avarage for a given league"""
        df.columns = ['Name', 'City', 'Club', 'Capacity']
        df['Capacity'] = df['Capacity'].str.replace(" ", "")
        df['Capacity'] = df['Capacity'].astype('int64')
        cap = round(df['Capacity'].mean())
        return cap

    df_list = []

    new_df = create_df()
    number = 0
    country1 = request.form.get("country1")
    country2 = request.form.get("country2")
    country3 = request.form.get("country3")
    country4 = request.form.get("country4")
    country5 = request.form.get("country5")

    countries_selected = [country1, country2, country3, country4, country5]

    if not all(elem in countries for elem in countries_selected):
        print("Not all countries selected!")
        error_message = "All five countries must be selected"
        return render_template('index.html', countries=keys, error_message=error_message)
    
    for n in countries_selected:
        selected = n
        try:
            myaddress = get_address(countries, selected, ADDRESS)
        except:
            country_error = "Source website error. Please try again or select a country other than " + n + "."
            return render_template('index.html', countries=keys,
                            country_error=country_error)
        
        division = league_level(myaddress)
        capacity = avg_capacity(division)
        dic = {'League': selected, 'Capacity': capacity}
        df_list.append(dic)
        number += 1

    new_df = pd.DataFrame.from_records(df_list)
    new_df = new_df.sort_values(by=['Capacity'], ascending=False).reset_index(drop=True)

    new_df['Rank'] = [1, 2, 3, 4, 5] 
    new_df = new_df[['Rank', 'League', 'Capacity']]
    highest = new_df.iloc[0]['League']

    print("new_df:", new_df)


    glob_df = new_df.copy()
    
    new_df['Capacity'] = new_df['Capacity'].astype(str)
    new_df["Capacity"] = new_df["Capacity"].str.slice(stop=-3) + " " + new_df["Capacity"].str.slice(start=-3)


    try:
        glob_df
    except:
        glob_error = "Server error. Please try again"
        return render_template('index.html', countries=keys,
                                        glob_error=glob_error)

    if len(countries_selected) != len(set(countries_selected)):
        error_statement = "You cannot select a country more than once!"
        print(error_statement)
        return render_template('index.html', countries=keys,
                            error_statement=error_statement)
    else:              
        return render_template('cap.html',
                               tables=[new_df.to_html(index=False)], highest=highest)


if __name__ == '__main__':
    app.run(debug=True)