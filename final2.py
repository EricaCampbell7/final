import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk


# read in the file
def read_data():
    return pd.read_csv("Skyscrapers2021.csv").set_index("RANK")


# filter the data
def filter_data(selected_city_list, max_floors, oldest_building):
    df = read_data()
    df = df.loc[df['CITY'].isin(selected_city_list)]
    df = df.loc[df['FLOORS'] < max_floors]
    df = df.loc[df['COMPLETION'] > oldest_building]
    return df

# take all of the cities in the data and put them into a list
def all_cities():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['CITY'] not in lst:
            lst.append(row['CITY'])

    return lst

'''Python demonstration based on skyscrapers.csv file'''
# count all of the cities in the list using a dataframe
def count_cities(cities, df):
    lst = []
    if df.shape[0] > 0:
        lst = [df.loc[df['CITY'].isin([city])].shape[0] for city in cities]

    return lst

# use a function to create a pie chart based on the amount of skyscrapers in each city
def create_piechart(counts, selected_cities):
    explodes = [0 for i in range(len(counts))]
    maximum = counts.index(np.max(counts))
    explodes[maximum] = 0.2
    plt.pie(counts, explode=explodes, labels=selected_cities, autopct="%.2f")
    # st.pyplot(plt)
    return plt

# create a function that puts all of the cities into a dictionary and then append the height of each building
def city_height(df):
    cities = [row['CITY'] for ind, row in df.iterrows()]
    feet = [row['Feet'] for ind, row in df.iterrows()]
    dict = {}
    for city in cities:
        dict[city] = []

    for i in range(len(cities)):
        dict[cities[i]].append(int(feet[i].split(" ")[0].replace(",", "")))

    return dict

# use a function to calculate the height averages
def height_averages(dict_feet):
    dict = {}
    for key in dict_feet.keys():
        dict[key] = np.mean(dict_feet[key])

    return dict

# create a bar chart using the average height and the selected cities
def create_barchart(dict_averages, color):
    plt.figure()

    x = dict_averages.keys()
    y = dict_averages.values()
    plt.bar(x, y, color=color)
    plt.xticks(rotation=45)
    plt.ylabel("Feet")
    plt.xlabel("City")
    plt.title(f"Average Skyscraper Height for Cities: {','.join(dict_averages.keys())}")

    return plt

# create a function to display a map based on the location and the amount of floors in each skyscraper
def generate_map(df, view):
    map_df = df.filter(['NAME', 'MATERIAL', 'Meters', 'COMPLETION', 'Latitude', 'Longitude'])

    view_state = pdk.ViewState(latitude=map_df["Latitude"].mean(), longitude=map_df["Longitude"].mean(), zoom=6)
    layer1 = pdk.Layer('ScatterplotLayer', data=map_df, get_position='[Longitude, Latitude]', get_radius=300,
                       get_color=[200, 30, 24], pickable=True)

    layer2 = pdk.Layer("HexagonLayer",
                       data=df,
                       get_position="[Longitude, Latitude]",
                       radius=100000,
                       elevation_scale=1000,
                       pickable=True,
                       extruded=True,
                       auto_highlight=True,
                       coverage=0.9)

    tool_tip = {""}

    if view == "locations":
        tool_tip = {'html': '{COMPLETION}<br/><b>{NAME}</b><br>Height: {Meters}<br>Material: {MATERIAL}',
                    'style': {'backgroundColor': 'red', 'color': 'white'}}

        layer = layer1

    if view == "density":
        tool_tip = tool_tip = {"html": "Buildings: {elevationValue}<br/>", "style": {"backgroundColor": "steelblue", "color": "white"}}

        layer = layer2

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', initial_view_state=view_state, layers=[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)

# put all functions together into the main function and display all inputs, texts and sliders
def main():
    st.title("Skyscraper Data Visualization")
    st.write("Welcome to this Skyscrapers data! Open the side by to begin")
    st.sidebar.write("Please choose your options to display data")

    selected_cities = st.sidebar.multiselect("Pick cities: Select at least two", all_cities())
    view_choice = st.sidebar.radio("Pick a map view", ['locations', 'density'])
    min_floors = st.sidebar.slider("Pick a floor", 1, 200, 50)
    min_year = st.sidebar.slider("Pick a date", 1920, 2021, 1950)
    sel_color = st.sidebar.radio("Pick a bar chart color", ['red', 'pink', 'orange', 'purple'])

    data = filter_data(selected_cities, min_floors, min_year)
    st.dataframe(data.filter(['NAME', 'CITY', 'COMPLETION', 'Height']).sort_values(by=['CITY', 'COMPLETION']))
    series = count_cities(selected_cities, data)

    if data.shape[0] > 0:
        st.write("View map of Skyscrapers")
        st.write("This map allows for users to view the location and density for the cities they select, based on their longitude and latitude")
        generate_map(data, view_choice)
        st.write("View a pie chart")
        st.write("This chart allows the user to view the percentage of the amount of skyscrapers in each city")
        st.write("The pie chart then explodes the city with the largest number of skyscrapers")
        st.pyplot(create_piechart(series, selected_cities))
        st.write("View a bar chart")
        st.write("This bar chart allows for the user to view the average height for all the skyscrapers in each city")
        st.write("Compares the average height for each city")
        st.pyplot(create_barchart(height_averages(city_height(data)), sel_color))


main()

# data = filter_data(default_cities, default_floors, default_age)
# counts = count_cities(default_cities, data)

# feet = city_height(data)
# averages = height_averages(feet)

# st.pyplot(create_barchart(averages))

# generate_map(data)
