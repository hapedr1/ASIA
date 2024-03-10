# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 21:16:20 2024

@author: pgalorda
"""
import dash_bootstrap_components as dbc
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
from math import ceil
import plotly.graph_objs as go
from dash import dash_table
# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], )
server = app.server  # For deployment

# Define data loading function
def load_data(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name, index_col='date')

# Load all industries data
def load_all_data(file_path, sheet_names):
    all_data = {}
    for sheet in sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        df.drop_duplicates(subset='date', inplace=True)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        all_data[sheet] = df
    return all_data

# Aggregate columns based on patterns
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

file_path = 'ASIA.xlsx'
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


all_industries_data = load_all_data(file_path, industry_list_asia)
new_orders_business_df = aggregate_columns(all_industries_data, ["New Orders", "New Business"])
future_activity_output_df = aggregate_columns(all_industries_data, ["Future Activity", "Future Output"])
pmi_output_df = aggregate_columns(all_industries_data, ["PMI_"])
colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}
# Define app layout
app.layout = html.Div(style={'backgroundColor': colors['background'], 'color': colors['text']}, children=[
    html.Div(id='sidebar', style={
        'width': '13%', 
        'position': 'fixed',  # Fixed positioning
        'height': '100vh',  # Full height of the viewport
        'overflowY': 'auto',  # Allow vertical scrolling inside the sidebar if content overflows
        'padding': '20px',
        'backgroundColor': '#D5564A', # '#A93226'
        'borderRight': '1px solid black'
    }, children=[
        html.H3("ASIA DASHBOARD\n\n", style={'textAlign': 'center', 'color': "white"}),
        html.Div(style={'margin-bottom': '60px'}),
        html.H6("Choose the industry to display:", style={'textAlign': 'center', 'color': "white"}),
        html.Div(style={'margin-bottom': '20px'}),
        dcc.Dropdown(
            id='industry-dropdown',
            options=[{'label': i, 'value': i} for i in industry_list_asia],
            value=industry_list_asia[0],
            style={'width': '100%', 'color': 'black'}
        ),
       
    ]),
    html.Div(id='main-content', style={
        'marginLeft': '13%',  # Sidebar width
        'padding': '20px',
        'display': 'flex',  # Display charts horizontally
        'justifyContent': 'space-between',  # Space between charts
        'flexWrap': 'wrap',  # Allow wrapping for responsiveness
    }, children=[
        html.Div(dcc.Graph(id='new-orders-chart'), style={
            'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',  # Box shadow effect
            'width': '30%',  # Chart width
            'margin': '12px',  # Margin around cards
            'backgroundColor': 'white',  # Background color for the card
        }),
        html.Div(dcc.Graph(id='future-activity-chart'), style={
            'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
            'width': '30%',
            'margin': '12px',
            'backgroundColor': 'white',
        }),
        html.Div(dcc.Graph(id='pmi-chart'), style={
            'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
            'width': '30%',
            'margin': '12px',
            'backgroundColor': 'white',
        })
        
    ]),
        html.H3(id='dynamic-title', style={'textAlign': 'center', 'color': 'black','marginLeft': '10%'}),
    html.Div([
        html.Div(id='country-charts-container'),  # Container for the country charts
    ], style={'width': '80%', 'marginLeft': '6%', 'marginTop': '20px','padding': '20px'})
])



# Callbacks to update charts
@app.callback(
    [Output('new-orders-chart', 'figure'),
     Output('future-activity-chart', 'figure'),
     Output('pmi-chart', 'figure')],
    Output('country-charts-container', 'children'),
    Output('dynamic-title', 'children'),
    [Input('industry-dropdown', 'value')]
)
def update_charts(selected_industry):
    if not selected_industry:
        raise PreventUpdate
    
    def style_figure(fig, title):
        fig.update_layout(
            title_text=title,
            title_x=0.5,  # Center title
            margin=dict(l=20, r=20, t=50, b=20),
            plot_bgcolor='rgba(1,0,0,0)',  # Transparent plot background
            paper_bgcolor="white",  # Card color for paper background
            font=dict(color='black'),
            xaxis=dict(showgrid=False),  # Hide the x-axis grid lines
            yaxis=dict(showgrid=False),  # Hide the y-axis grid lines
            xaxis_title='Date',
            yaxis_title='Value',
            showlegend=False,
            title_font=dict(size=20, family="Arial", color='black')
        )
        fig.add_hline(y=50, line_dash="dash", line_color="red")
        fig.update_traces(line=dict(width=2))
        # Set the axis linecolor to white to make it visible on the background
        fig.update_xaxes(linecolor='orange')
        fig.update_yaxes(linecolor='orange')
        return fig
    
    # Create new orders figure
    new_orders_fig = px.line(new_orders_business_df.rolling(6).mean()["2021-08":],
                             labels={'variable': 'Industry'}, template='plotly_dark')
    new_orders_fig = style_figure(new_orders_fig, 'New Orders')
    
    # Create future activity figure
    future_activity_fig = px.line(future_activity_output_df.rolling(6).mean()["2021-08":],
                                  labels={'variable': 'Industry'}, template='plotly_dark')
    future_activity_fig = style_figure(future_activity_fig, 'Future Activity')
    
    # Create PMI figure
    pmi_fig = px.line(pmi_output_df.rolling(6).mean()["2021":],
                      labels={'value': 'PMI', 'variable': 'Industry'}, template='plotly_dark')
    pmi_fig = style_figure(pmi_fig, 'PMI')
        
    countries_data = load_data(file_path, selected_industry)

    # Create country charts

    country_charts = []
    grid_style = {'display': 'grid', 'gridTemplateColumns': 'repeat(7, 1fr)', 'gap': '10px', 'width': '106%','marginLeft': '13%'}
    dynamic_title = selected_industry if selected_industry else " "
    
    for i, column in enumerate(countries_data.columns):
        country_charts.append(
            html.Div(dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=countries_data.index,
                            y=countries_data[column].rolling(3).mean(),
                            mode='lines',
                            name=column
                        )
                    ],
                    layout=go.Layout(
                        title=column,
                        xaxis_title='Date',
                        yaxis_title='Value',
                        margin=dict(l=20, r=20, t=50, b=20),
                        plot_bgcolor=colors['background'],
                        paper_bgcolor=colors['background'],
                        font=dict(color='black'),
                        height=300
                    )
                ).update_traces(line=dict(width=2))
                .add_hline(y=50, line_dash="dash", line_color="red"),
            ), style={'width': '88%', 'display': 'inline-block'})  # Define width for each chart container
        )

    # Organize the charts into a grid layout
    country_charts_grid = html.Div(style=grid_style, children=country_charts)

    return new_orders_fig, future_activity_fig, pmi_fig, country_charts_grid,dynamic_title

if __name__ == '__main__':
    app.run_server(debug=True)