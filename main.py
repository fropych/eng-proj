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

unique_df = get_unique_df(selected_df)
unique_df = unique_df[unique_df['Currency'] == 'RUR']

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
color = pd.Categorical(unique_df.Text).codes
fig = go.Figure(go.Scattermapbox(lat=unique_df['Lat'], lon=unique_df['Lon'],
                                 text=unique_df['Text'],
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
sum_counts = selected_df['Text'].value_counts()
fig = go.Figure()
fig.add_trace(go.Pie(values=sum_counts,
                     labels=sum_counts.index,
                     opacity=0.85))
fig.update_layout(margin=margin)
st.plotly_chart(fig)

#SALARY MEAN
st.header('Average Salary by Day')

sf_mean = unique_df['SalaryFrom'].groupby('PublishedAt').median()
st_mean = unique_df['SalaryTo'].groupby('PublishedAt').median()

idx = pd.date_range(sf_mean.index.min(), sf_mean.index.max())
sf_mean = sf_mean.reindex(idx, fill_value=0).fillna(0)
st_mean = st_mean.reindex(idx, fill_value=0).fillna(0)

sf_std = sf_mean * 0.2
st_std = st_mean * 0.2

fig = go.Figure()
plot_income(fig, 'SalaryFrom', sf_mean, sf_std, 'rgba(0,100,80,1)')
plot_income(fig, 'SalaryTo', st_mean, st_std, 'rgba(0,176,246,1)')

fig.update_layout(margin=margin,
                  xaxis_showgrid=False,
                  yaxis_showgrid=False,)
st.plotly_chart(fig)

#SALARY BY EXPERIENCE
st.header('Average Salary by Experience')
fig = go.Figure()
fig.add_trace(go.Histogram(x=df['Experience'],
                           y=df['SalaryFrom'],
                           histfunc='avg',
                           opacity=0.85,
                           marker_color='rgba(0,100,80,1)',
                           name='SalaryFrom',))
fig.add_trace(go.Histogram(x=df['Experience'],
                           y=df['SalaryTo'],
                           histfunc='avg',
                           opacity=0.35,
                           marker_color='rgba(0,176,246,1)',
                           name='SalaryTo',))
fig.update_layout(margin=margin,
                  barmode='overlay',
                  xaxis_showgrid=False,
                  yaxis_showgrid=False,)
st.plotly_chart(fig)

#NUMBER OF VACANCIES BY DAY
st.header('Number of Vacancies by Day')
show = st.checkbox('Show with Experience')
if not show:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=unique_df.index,
                            opacity=0.5,
                            marker_color='rgba(0,176,246,1)'))
else:
    fig = px.histogram(x=unique_df.index, color=unique_df["Experience"], opacity=0.65)
fig.update_layout(margin=margin,
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                xaxis_title=None,
                yaxis_title=None)
st.plotly_chart(fig)

#NUMBER OF VACANCIES BY EXPERIENCE
st.header('Number of Vacancies by Experience')
fig = go.Figure()
fig.add_trace(go.Histogram(x=selected_df['Experience'],
                           opacity=0.5,
                           marker_color='rgba(0,176,246,1)'))
fig.update_layout(margin=margin,
                  xaxis_showgrid=False,
                  yaxis_showgrid=False,)
st.plotly_chart(fig)
