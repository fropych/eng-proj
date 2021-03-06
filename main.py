import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import os

def get_unique_df(df):
    columns = {vac_id: 'first' for vac_id in df.columns[1:]}
    columns["Text"] = '|'.join
    unique_df = df.groupby('Id').agg(columns).reset_index()
    return unique_df
def plot_income(fig, name, mean, deviaton, line_color):
    fillcolor = line_color[:-2] + '0.2)' 
    fig.add_traces([go.Scatter(x=mean.index,
                            y=mean+deviaton, 
                            showlegend=False,
                            line_color='rgba(255,255,255,0)',
                            name=name),
                    go.Scatter(x=mean.index, 
                            y=mean-deviaton, 
                            showlegend=False,
                            line_color='rgba(255,255,255,0)',
                            fillcolor=fillcolor, 
                            fill='tonexty',
                            name=name)])
    fig.add_trace(go.Scatter(x=mean.index,
                            y=mean,
                            line_color=line_color,
                            mode='lines+markers',
                            name=name))
    
path = os.path.abspath(r'./vacancies.csv')
cities = pd.read_csv('https://raw.githubusercontent.com/hflabs/city/master/city.csv')
df = pd.read_csv(path, sep=';', parse_dates=['PublishedAt',])

margin=go.layout.Margin(
        l=5,
        r=5,
        b=5,
        t=5,
        pad=4)
st.sidebar.header('Settings')

#SELECT REQUESTS
selected_texts = st.sidebar.multiselect("Select Requests",
                                        df['Text'].unique(),
                                        df['Text'].unique())
selected_df = df[df["Text"].str.\
                        contains('|'.join(selected_texts),
                                          case=False)]

selected_df = selected_df[selected_df['Currency'] == 'RUR']
unique_df = get_unique_df(selected_df)


#ROW DATA
st.sidebar.subheader('Raw Data')
show_data = st.sidebar.checkbox('Show raw data')
if show_data == True:
    show_unique = st.sidebar.checkbox('Show only unique vacancies')
    cur_df = {True: unique_df,
              False: selected_df} 
    
    st.header('Raw data')
    st.markdown("#### Job data for the last month from HeadHunter")
    salary_col = ['SalaryFrom', 'SalaryTo']
    df_to_show = cur_df[show_unique].copy()
    df_to_show[salary_col]=df_to_show[salary_col].convert_dtypes()
    st.write(df_to_show)
unique_df.set_index('PublishedAt', inplace=True)
selected_df.set_index('PublishedAt', inplace=True)

#MAP
st.header('Map of Vacancies')

text = unique_df['Text']+'<br>'+\
       'Salary: ' +\
       unique_df['SalaryFrom'].fillna(0).astype(str)+' - '+\
       unique_df['SalaryTo'].fillna('???').astype(str)
color = pd.Categorical(unique_df.Text).codes
fig = go.Figure(go.Scattermapbox(lat=unique_df['Lat'], lon=unique_df['Lon'],
                                 text=text,
                                 marker=dict(color=color,
                                             opacity=0.5,
                                             size=10)
                                ))
map_center = go.layout.mapbox.Center(lat = 55.76,
                                     lon= 37.63)
fig.update_layout(mapbox_style="open-street-map",
                  mapbox=dict(center=map_center, zoom=9),
                  margin=margin)
st.plotly_chart(fig)

#DISTRIBUTION
st.header('Distribution of Vacancies')
show = st.radio('Distribution by:', ['Employer', 'Request', 'Experience', 'Schedule'])
if show != 'Request':
    cur_df = unique_df
else:
    cur_df = selected_df
show = "Text" if show == 'Request' else show
top_x=None
if show == 'Employer':
    top_x=st.slider('Top:',
                    min_value=5,
                    max_value=50,
                    value=10)
    
sum_counts = cur_df[show].value_counts()[:top_x]
fig = go.Figure()
fig.add_trace(go.Pie(values=sum_counts,
                     labels=sum_counts.index,
                     opacity=0.75))
fig.update_layout(margin=margin)
st.plotly_chart(fig)

#NUMBER OF VACANCIES BY DAY
st.header('Number of Vacancies by Day')
show = st.radio('Show with:', ['None', 'Experience', 'Schedule'])
if show=='None':
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=unique_df.index,
                            opacity=0.5,
                            marker_color='rgba(0,176,246,1)'))
else:
    fig = px.histogram(x=unique_df.index, color=unique_df[show], opacity=0.65)
fig.update_layout(margin=margin,
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                xaxis_title=None,
                yaxis_title=None)
st.plotly_chart(fig)

#SALARY
st.header('Average Salary')
show = st.radio('Average by:', ['Request','Experience', 'Schedule', 'Day'])
if show != 'Request':
    cur_df = unique_df
else:
    cur_df = selected_df
show = 'Text' if show == 'Request' else show

fig = go.Figure()
if show == 'Day':
    sf_mean = cur_df['SalaryFrom'].groupby('PublishedAt').median()
    st_mean = cur_df['SalaryTo'].groupby('PublishedAt').median()

    idx = pd.date_range(sf_mean.index.min(), sf_mean.index.max())
    sf_mean = sf_mean.reindex(idx, fill_value=0).fillna(0)
    st_mean = st_mean.reindex(idx, fill_value=0).fillna(0)

    sf_std = sf_mean * 0.2
    st_std = st_mean * 0.2

    
    plot_income(fig, 'SalaryFrom', sf_mean, sf_std, 'rgba(0,100,80,1)')
    plot_income(fig, 'SalaryTo', st_mean, st_std, 'rgba(0,176,246,1)')
else:
    fig.add_trace(go.Histogram(x=cur_df[show],
                            y=cur_df['SalaryFrom'],
                            histfunc='avg',
                            opacity=0.85,
                            marker_color='rgba(0,100,80,1)',
                            name='SalaryFrom',))
    fig.add_trace(go.Histogram(x=cur_df[show],
                            y=cur_df['SalaryTo'],
                            histfunc='avg',
                            opacity=0.35,
                            marker_color='rgba(0,176,246,1)',
                            name='SalaryTo',))
    fig.update_layout(barmode='overlay')
    
fig.update_layout(margin=margin,
                  xaxis_showgrid=False,
                  yaxis_showgrid=False,)
st.plotly_chart(fig)
