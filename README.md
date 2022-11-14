<div align="center">
  <h1> 🇫🇷 <br>Today in Paris</h1>
  <i>A Streamlit app to look for upcoming events in Paris
  </i>
</div>

___

## 👀 What

I created a Streamlit app that lists all the upcoming events in Paris. The user can filter results by topics of interest, Parisian districts and/or can enter a specific date.

## 🤷‍♂️ Why

For two main reasons:
1. I started a new job and Streamlit is part of the data stack. I heard about it before, but wanted to get up to speed quickly and there's not better way to learn than building something.
2. Monitoring cultural events in Paris has always been a pain to me. Either you have to scroll a infinite list of events, without any filteting options or you have to read a selection made by someone else (who sometimes received money to add events).

## 🛠 How
#### 1) Finding Data:
After considering scrapping multiple websites, I came across Paris Open Data, which contains an open source calendar of all the future events in Paris. This is the source for the _Que Faire à Paris ?_ part of city website.

#### 2) Creating the Python Script:
There were several elements that I wanted to include in my script:
- **An API call**: Super easy with the `requests` package, and found the link to the dataset I was interested in directly on Paris Opend Data website.
- **Pandas Chaining**: To make the code as clean as possible in the fuctions defined in the beginning of the script. For those interested in chaining, I recommend [this great video](https://www.youtube.com/watch?v=zgbUk90aQ6A) by Matt Harrison.
- **Streamlit features**: I soon discovered that this package is super easy and fun to use! I tried to find use cases to cover different features: interactive user inputs, plotting, lottie import, app formatting, ... The website [documentation](https://docs.streamlit.io) is great and was enough for me to achieve what I wanted.
- **Geovisualization**: I used `Pydeck` to include advanced mapping plotting capabilities (well, mostly a beautiful and interactive map). As I want a bit further than `Streamlit` st.map, I had to put some extra work.

#### 3) Making it live:

I used `pipreqs` to create a `requirements.txt` file Streamlit could use, created a Streamlit account, clicked on New App and copy/paste the link to this repo. Less than the time needed for my tea to infuse.

## ⏭ Potential Next Steps:

- Include other data sources to offer more options (e.g. more events, restaurants, movie releases, ...).
- Go into details to improve data cleaning and surface the dataframe.
- Improve the functions logic.
- Conduct an EDA to create high level insights on the events scene.