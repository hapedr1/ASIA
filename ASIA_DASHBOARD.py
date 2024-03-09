# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 16:43:05 2024

@author: pgalorda
"""
#cd C:\Users\pgalorda\OneDrive - Analistas Financieros Internacionales (Afi)\Desktop\PMI EUROPA
#streamlit run ASIA_DASHBOARD.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from math import ceil
import plotly.express as px

industry_list_asia = ['Chemicals',
 'Forestry & Paper Products',
 'Metals & Mining',
 'Automobiles & Auto Parts',
 'Beverages & Food',
 'Household & Personal Use Produc',
 'Consumer Services',
 'Banks',
 'Insurance',
 'Real Estate',
 'Pharmaceuticals & Biotechnology',
 'Healthcare Services',
 'Industrial Goods',
 'Industrial Services',
 'Transportation',
 'Technology Equipment',
 'Software & Services']

@st.cache_data

def load_data(file_path, sheet_name):

    return pd.read_excel(file_path, sheet_name=sheet_name, index_col='date')

st.set_page_config(layout="wide", page_title="ASIA DASHBOARD")
st.markdown("<h1 style='text-align: center;'>ASIA DASHBOARD</h1>", unsafe_allow_html=True)




file_path = 'ASIA.xlsx'

industry = st.sidebar.selectbox('Select the first industry:', options=industry_list_asia)



countries_data = load_data(file_path,sheet_name=industry)

def load_all_data(file_path, sheet_names):
    all_data = {}
    for sheet in sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)

        df.drop_duplicates(subset='date', inplace=True)
   
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        all_data[sheet] = df
    return all_data


def aggregate_columns(data, column_patterns):
    aggregate_df = pd.DataFrame()
    for sheet, df in data.items():
        for col in df.columns:
            for pattern in column_patterns:
           
                if pattern in col:
            
                    new_col_name = f"{sheet} - {col}"
                    if new_col_name not in aggregate_df.columns:
                        aggregate_df[new_col_name] = df[col]
                    break
    return aggregate_df


all_industries_data = load_all_data(file_path, industry_list_asia)


new_orders_business_df = aggregate_columns(all_industries_data, ["New Orders", "New Business"])
future_activity_output_df = aggregate_columns(all_industries_data, ["Future Activity", "Future Output"])
pmi_output_df = aggregate_columns(all_industries_data, ["PMI_"])

col1, col2= st.columns([1, 1])  

with col1:
    st.markdown("### Ordenes Futuras")
    fig = px.line(new_orders_business_df.rolling(6).mean()["2021-08":], labels={'variable':'Industry'})
    fig.update_traces(mode='lines+markers')
    
    fig.update_layout(showlegend=False)
    fig.add_hline(y=50, line_dash="solid", line_color="red") 
    fig.update_layout(hovermode='closest')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Actividad Futura")
    fig = px.line(future_activity_output_df.rolling(6).mean()["2021-08":], labels={'variable':'Industry'})
    fig.update_traces(mode='lines+markers')
 
    fig.update_layout(showlegend=False)
    fig.add_hline(y=50, line_dash="solid", line_color="red") 
    fig.update_layout(hovermode='closest')
    st.plotly_chart(fig, use_container_width=True)
    
fig = px.line(pmi_output_df.rolling(6).mean()["2021":], labels={'value': 'PMI', 'variable': 'Industry'})
fig.update_traces(mode='lines+markers')
fig.add_hline(y=50, line_dash="solid", line_color="red") 
fig.update_layout(
    showlegend=False,
    hovermode='closest',
    title={
        'text': "PMI",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(
          
            size=20,
          
        )
    }
)
st.plotly_chart(fig, use_container_width=True)

    
    




st.markdown(f"<h2 style='text-align: center;'>{industry}</h2>", unsafe_allow_html=True)

charts_per_row = 3

num_rows = ceil(len(countries_data.columns) / charts_per_row)


fig, axs = plt.subplots(num_rows, charts_per_row, figsize=(20, num_rows * 4))
axs = axs.flatten() 

for i, column in enumerate(countries_data.columns):
    ax = axs[i]
    ax.plot(countries_data.index, countries_data[column].rolling(3).mean(), label=column)

    ax.axhline(y=50, color='r', linestyle='--', linewidth=1)
    ax.set_xlabel('Date')
    ax.set_ylabel(column)
    ax.tick_params(axis='x', labelsize=8)
    ax.legend()

for j in range(i + 1, len(axs)):
    axs[j].axis('off')

plt.tight_layout()
st.pyplot(fig)

