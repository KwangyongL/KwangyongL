import yelpapi
import requests
import json
from binarytree import build
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from flask import Flask, render_template, request

CACHE_FILENAME = "yelp_cache.json"
CACHE_DICT = {}

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key

def make_request(baseurl, params, headers):
    '''Make a request to the Web API using the baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    headers:

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    response = requests.get(baseurl, params=params, headers=headers)
    return response.json()

def make_request_with_cache(baseurl, params, headers):
    '''Check the cache for a saved result for this baseurl+params
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    headers: 

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("\ncache hit!", request_key)
        return CACHE_DICT[request_key]
    else:
        print("\ncache miss!", request_key)
        CACHE_DICT[request_key] = make_request(baseurl, params, headers)
        save_cache(CACHE_DICT)
        return CACHE_DICT[request_key]

def weather(city):
    city = city.replace(" ", "+")
    res = requests.get(
        f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8', headers=headers_weather)
    print("Weather information\n")
    soup = BeautifulSoup(res.text, 'html.parser')
    time = soup.select('#wob_dts')[0].getText().strip()
    info = soup.select('#wob_dc')[0].getText().strip()
    weather = soup.select('#wob_tm')[0].getText().strip()
    print("Today :", time)
    print(info)
    print(weather+"°C\n")
    return info

# building flask

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('results_final3.html',
        weather=info, flask_data=flask_data, term=term, location=location)



if __name__ == "__main__":

    # yelp api

    client_id = '8CqOeUyFiRdgTq_MRsD8aQ'
    api_key = 'rpiT2_1iCm7J__UGDFyvPGnd0HUN31X_RaOjXyBb9omp1EHHRmZussAxGFJn_GXXZgA9-4FqCvD7BpPuLXEBYMvleq1wLzBq9bbRcTUDhhWlPshMIXm9KFO1SFCkYXYx'
    headers = {'Authorization': 'Bearer %s' % api_key}
    base_url = 'https://api.yelp.com/v3/businesses/search'
    location = input("which city do you want to eat? or 'exit' to quit: ")
    if location == 'exit':
        print("\nBye!")
    else:
        term = input("what kind of food you want to eat? or 'exit' to quit: ")
        if term == 'exit':
            print("\nBye!")

    while True:
        if location == "exit" or term == "exit": # if user enters exit, the program terminates
            break
        else: # enter a search term
            params = {"location": location, "term": term}
            CACHE_DICT = open_cache()
            results = make_request_with_cache(base_url, params, headers)
            businesses = results["businesses"]
            nodes = []
            name = []
            rating = []
            address = []
            phone_num = []
            flask_data = []
            price = []
            for business in businesses:
                flask_tem = []
                name.append(business["name"])
                rating.append(business["rating"])
                address.append(" ".join(business["location"]["display_address"]))
                phone_num.append(business["phone"])
                if "price" in business:
                        price.append(len(business["price"]))
                else:
                    price.append('none')
                flask_tem.append(business["name"])
                flask_tem.append(business["rating"])
                flask_tem.append(" ".join(business["location"]["display_address"]))
                flask_tem.append(business["phone"])
                flask_data.append(flask_tem)
                nodes.append(business["rating"])
                id = business["id"]
                url="https://api.yelp.com/v3/businesses/" + id + "/reviews"
                response = requests.get(url, headers=headers)
                result = response.json()
                reviews = result["reviews"]
                print("--- Reviews ---")
                for review in reviews:
                    print("User:", review["user"]["name"], "Rating:", review["rating"], "Review:", review["text"], "\n")


            # creating Bar chart
            bar_data = go.Bar(x=name, y=rating)
            basic_layout = go.Layout(title=f"Restaurant rating in {location}")
            fig = go.Figure(data=bar_data, layout=basic_layout)
            fig.update_yaxes(tick0=1, dtick=0.5)

            fig.show()
            fig.write_html("bar.html", auto_open = True)

            # creating Scatter plot

            rating_sc = []
            for r in rating:
                if float(r) >=4.5:
                    r = "excellent"
                elif float(r) >=4.0:
                    r = "great"
                elif float(r) >=3.5:
                    r = "good"
                elif float(r) >=3.0:
                    r = "average"
                else: r = "don't go"

                rating_sc.append(r)
 
            scatter_data = go.Scatter(
                x=price, 
                y=rating_sc,
                text=name, 
                marker={'symbol':'square', 'size':30, 'color': 'green'},
                mode='markers+text', 
                textposition=["top center", "top right", "top left", "middle left", "middle right", "bottom center",
                  "bottom right", "bottom left"])
            basic_layout_2 = go.Layout(title="Rating(y) and Price(x) of restaurant in your search area")
            fig2 = go.Figure(data=scatter_data, layout=basic_layout_2)
            fig2.update_xaxes(tick0=1, dtick=1)

            fig2.write_html("scatter.html", auto_open=True)

            # Openweather API

            api_key_weather = 'bb332876ea96f7ec113dc1c70985eab0'
            headers_weather = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            city = location+" weather"
            weather(city)
            info = weather(city)


            # Building the binary tree
            binary_tree = build(nodes)
            print('Binary tree from list :\n',
                binary_tree)

            # Getting list of nodes from
            # binarytree
            print('\nList from binary tree :',
                binary_tree.values)

            # creating flask
            app.run(debug=False)

        while True: # After the first query is run, user can enter another search term or exiting
            user_input = input("another search term? then 'yes' or exit:")
            if user_input == "exit":
                location = "exit"
                print("\nBye!")
                break
            else: # starting a new search query
                location = input("which city do you want to eat? or 'exit' to quit: ")
                if location == 'exit':
                    print("\nBye!")
                else:
                    term = input("what kind of food you want to eat? or 'exit' to quit: ")
                    if term == 'exit':
                        print("\nBye!")

                params = {"location": location, "term": term}
                CACHE_DICT = open_cache()
                results = make_request_with_cache(base_url, params, headers)
                businesses = results["businesses"]
                nodes = []
                name = []
                rating = []
                address = []
                phone_num = []
                flask_data = []
                price = []
                for business in businesses:
                    flask_tem = []
                    name.append(business["name"])
                    rating.append(business["rating"])
                    address.append(" ".join(business["location"]["display_address"]))
                    phone_num.append(business["phone"])
                    if "price" in business:
                        price.append(len(business["price"]))
                    else:
                        price.append('none')
                    flask_tem.append(business["name"])
                    flask_tem.append(business["rating"])
                    flask_tem.append(" ".join(business["location"]["display_address"]))
                    flask_tem.append(business["phone"])
                    flask_data.append(flask_tem)
                    nodes.append(business["rating"])
                    id = business["id"]
                    url="https://api.yelp.com/v3/businesses/" + id + "/reviews"
                    response = requests.get(url, headers=headers)
                    result = response.json()
                    reviews = result["reviews"]
                    print("--- Reviews ---")
                    for review in reviews:
                        print("User:", review["user"]["name"], "Rating:", review["rating"], "Review:", review["text"], "\n")
                # creating Bar chart
                bar_data = go.Bar(x=name, y=rating)
                basic_layout = go.Layout(title=f"Restaurant rating in {location}")
                fig = go.Figure(data=bar_data, layout=basic_layout)
                fig.update_yaxes(tick0=1, dtick=0.5)

                fig.show()
                fig.write_html("bar.html", auto_open = True)

                # creating Scatter plot

                rating_sc = []
                for r in rating:
                    if float(r) >=4.5:
                        r = "excellent"
                    elif float(r) >=4.0:
                        r = "great"
                    elif float(r) >=3.5:
                        r = "good"
                    elif float(r) >=3.0:
                        r = "average"
                    else: r = "don't go"

                    rating_sc.append(r)
    
                scatter_data = go.Scatter(
                    x=price, 
                    y=rating_sc,
                    text=name, 
                    marker={'symbol':'square', 'size':30, 'color': 'green'},
                    mode='markers+text', 
                    textposition=["top center", "top right", "top left", "middle left", "middle right", "bottom center",
                  "bottom right", "bottom left"])
                basic_layout_2 = go.Layout(title="Rating(y) and Price(x) of restaurant in your search area")
                fig2 = go.Figure(data=scatter_data, layout=basic_layout_2)
                fig2.update_xaxes(tick0=1, dtick=1)
                
                fig2.write_html("scatter.html", auto_open=True)

                # Openweather API

                api_key_weather = 'bb332876ea96f7ec113dc1c70985eab0'
                headers_weather = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                city = location+" weather"
                weather(city)
                info = weather(city)

                # Building the binary tree
                binary_tree = build(nodes)
                print('Binary tree from list :\n',
                    binary_tree)

                # Getting list of nodes from
                # binarytree
                print('\nList from binary tree :',
                    binary_tree.values)

                # creating flask
                app.run(debug=False)