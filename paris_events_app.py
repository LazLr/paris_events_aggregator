# Paris Events Aggregator

# 1. Import libraries
import requests
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_lottie import st_lottie
import pydeck as pdk
from datetime import datetime

# 2. Create functions
def get_paris_data(rows = 5_000):
    sort = '&sort=-date_start'
    refine = '&refine.address_city=Paris'
    exclude = '&exclude.tags=Enfants'
    url_paris_data = f"https://opendata.paris.fr/api/records/1.0/search/?dataset=que-faire-a-paris-&q=&rows={rows}{sort}&facet=date_start&facet=date_end&facet=tags&facet=address_name&facet=address_zipcode&facet=address_city&facet=transport&facet=price_type&facet=updated_at&facet=programs{refine}{exclude}"
    paris_data = requests.get(url_paris_data).json()
    columns = ['title','tags', 'date_start', 'date_end', 'updated_at', 'date_description', 'lead_text', 'url', 'address_zipcode', 'address_name', 'address_street', 'lat_lon', 'price_type','price_detail']
    df = (pd.DataFrame(paris_data['records'])
        .fields.apply(pd.Series)
        .loc[:,columns]
        .assign(title = lambda df_: df_.title.astype(str))
        .pipe(lambda df_: pd.concat([df_, df_.tags.str.split(';', expand=True).astype('category')], axis=1))
        .pipe(lambda df_: pd.concat([df_, pd.DataFrame(df_.lat_lon.to_list(), columns=['latitude', 'longitude'])], axis=1))
        .rename(columns={'lead_text':'description', 0: 'tag1', 1: 'tag2', 2: 'tag3', 3: 'tag4', 4:'tag5'})
        .drop(columns=['tags', 'tag3', 'tag4'])
        .assign(date_start = lambda df_: pd.to_datetime(df_.date_start))
        .assign(date_end = lambda df_: pd.to_datetime(df_.date_end))
        .assign(updated_at = lambda df_: pd.to_datetime(df_.updated_at))
        .assign(address_zipcode = lambda df_: df_.address_zipcode.str.replace(" ", "").str.extract(r'(75[0-9][0-9][0-9])', expand=False))
        .assign(address_zipcode = lambda df_: df_.address_zipcode.astype('category'))
        .assign(price_type = lambda df_: np.where((df_.price_type.isna()) & (df_.price_detail.notna()), 'payant', df_.price_type))
        .assign(price_type = lambda df_: df_.price_type.astype('category'))
        .dropna(subset= ['tag1', 'date_start', 'address_zipcode'])
        )
    return df

def load_lottieurl(url:str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def df_filtering(df):
    if tags_selected:
        df = df[df.tag1.isin(tags_selected) | df.tag2.isin(tags_selected)]
    else:
        df = df
    if postcode_selected:
        df = df[df.address_zipcode.isin(postcode_selected)]
    else:
        df = df
    if one_date:
        df = df[(df.date_start.dt.date <= date_selected) & (df.date_end.dt.date >= date_selected)]
    if venue_selected:
        df = df.loc[df['address_name'].str.contains(venue_selected, case=False, na=False)]
    return df

def df_displaying(df):
    final_columns = ['title', 'address_name','address_zipcode', 'date_start', 'date_end', 'description','price_type','url']
    df = (df[final_columns]
            .assign(date_start = lambda df_: pd.to_datetime(df_.date_start).dt.date)
            .assign(date_end = lambda df_: pd.to_datetime(df_.date_end).dt.date)
            .rename(columns={'title':'Event name'
                            , 'address_name':'Address'
                            , 'address_zipcode':'Arrondissement'
                            , 'date_start':'Start date'
                            , 'date_end':'End date'
                            , 'description':'Description'
                            , 'price_type':'Pricing'
                            , 'url':'Link'
                            })
            .set_index('Event name')
            .sort_values(by='End date', ascending=True)
        )
    return df

def geo_plotting(df):
    column = ['title', 'address_name','date_start','latitude', 'longitude']
    view_state = pdk.ViewState(longitude = 2.349014
                              ,latitude = 48.864716
                              ,zoom = 12
                              , pitch = 30)
    icon_data = {"url": "https://img.icons8.com/color/48/null/marker--v1.png",
                "width": 200,
                "height": 200,
                "anchorY": 200}
    filtered_df = (df[column]
                     .dropna()
                     .assign(icon_data = None)
                     )
    for i in filtered_df.index:
        filtered_df['icon_data'][i] = icon_data

    icon_layer = pdk.Layer(
        type = "IconLayer",
        data = filtered_df,
        get_icon = "icon_data",
        get_size = 4,
        size_scale = 15,
        get_position = ["longitude", "latitude"],
        pickable = True)

    tooltip = {"html": "<b>Adress:</b> {address_name}<br/> <b>Event:</b> {title}",
              "style": {"backgroundColor": "steelblue", "color": "white"}}
    # compile the map and set up the chart
    geoplot = pdk.Deck(layers = icon_layer
                , initial_view_state = view_state
                , tooltip = tooltip)
    return geoplot

# 3. Create the Initial DataFrame
paris_data = get_paris_data()

# 4. Streamlit App
st.set_page_config(
    page_title="Paris Events Calendar",
    page_icon="🇫🇷",
    layout="wide")

## Presentation Part
col1, col2 = st.columns([2,1])

with col1:
   st.title('Paris Events Calendar 🇫🇷 ')
   st.info('This tool will help you look for upcoming events in Paris. You can select an event category, a location and a date in the filters below. A table will be displayed with all the events that match your criteria as well as a map of Paris with all the venues mentioned.')

with col2:
    lottie_1 = load_lottieurl('https://assets5.lottiefiles.com/packages/lf20_7D0uqz.json')
    st_lottie(lottie_1, height = 200)

## User inputs
tags_selected = st.multiselect(
    'What kind of events do you want to attend?',
    sorted(paris_data['tag1'].unique()))

postcode_selected = st.multiselect(
    'Do you have a Parisian arrondissement in mind?',
    sorted(paris_data['address_zipcode'].unique().tolist()))

venue_selected = st.text_input('You can also search for a specific venue below (few of my favs: Centre Pompidou, Musée d\'Orsay, Le Hasard Ludique ...)')

col1, col2 = st.columns([2,2])

with col1:
    one_date = st.checkbox('I want to go out on a specific day (if you want to see all upcoming events, leave this box empty!)')

with col2:
    date_selected = st.date_input(
                "When do you want to go out?",
                datetime.today())

## Filter based on user's input and display the DataFrame
paris_data_filtered = df_filtering(paris_data)
paris_data_displayed  = df_displaying(paris_data_filtered)

## Events List
st.subheader('Upcoming events (matching your criteria):')
st.dataframe(paris_data_displayed)

## Events Map
if len(paris_data_filtered) == 0:
    st.info('There are no event that meet the current selection.')
else:
    geoplot = geo_plotting(paris_data_filtered)
    st.pydeck_chart(geoplot)

## Credits
col1, col2 = st.columns([2,2])

with col1:
    st.write('Built by [Etienne Leauthier](https://www.linkedin.com/in/etienne-leauthier-70530a61/) ✌️')

with col2:
    st.write('Fueled with [Paris Open Data](https://opendata.paris.fr/pages/home/)')

# See you later, aggregator!