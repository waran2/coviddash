import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import re


#import dash_bootstrap_components as dbc

main_page_style = {'backgroundColor':'#f2f2f2',
                #'margin': '.5%',
                'display': 'flex',
                'flexDirection': 'column'
                }

container_style = {'width': 'True',
                'height': 'True',
                'display': 'inline-block',
                'borderRadius': '5px',
                'boxShadow': '8px 8px 8px grey',
                'background-color': '#f9f9f9',
                #'padding': '10px',
                'margiBottom': '10px',
                'position': 'relative'

                 }

grapgh_layout = {
    'paper_bgcolor':'#f9f9f9'
}

# pr_container = {pretty_container {
#   border-radius: 5px;
#   background-color: #f9f9f9;
#   margin: 10px;
#   padding: 15px;
#   position: relative;
#   box-shadow: 2px 2px 2px lightgrey;
# }



#Read Data
df = pd.read_csv('test.csv')

#Get Continent dropdown list data from the dataframe
dl_continent = df['Continent_Name'].unique().tolist()
dl_continent.append('World')

def rtn_chloropleth(df, loc, col, scope):
    cl = px.choropleth(df,
                    locations=loc, # states code
                    scope=scope.lower(),
                    color=col # variable to be used for colour
                    #scope="usa"
                   )

    title_c = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', col)
    cl.update_layout(title_text = f'{title_c} in {scope}')#,title_x=0.5
    return cl


def rtn_geo_buble(g_data, loc, col, scope, input):

    if scope != 'World':
        print(scope)
        g_data = g_data.query("Continent_Name =='"+scope+"'"  )

    geo_graph = px.scatter_geo(g_data, locations=loc, color=col,
                     hover_name="CountryCode", size=input, size_max=80,
                     animation_frame="Date",
                     scope = scope.lower(),
                     #projection="natural earth",
                     opacity=0.6)
    title_g = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', input)
    geo_graph.update_layout(title_text = f'{title_g} in {scope}', paper_bgcolor = '#f9f9f9')
                    # "species": "Species of Iris)#,title_x=0.5
    return geo_graph



top5 = pd.read_csv('q5.csv')
#x-axis labels
date_list = top5.Date.unique().tolist()

#
x_val = [i for i in date_list[::14]]
x_text = [pd.to_datetime(str(i), format='%Y-%m-%d').strftime('%b-%d') for i in date_list[::14]]
x_text[0] = x_text[0] + ' 2020'

#
l_xval = [0 , 1, 2, 3]
sc_txt = ['no measures' , 'recommend closing' ,'require localised closing' ,'require all closing']
sh_txt = ['no measures', 'recommend not leaving house', 'require not leaving house with exceptions',  'require not leaving house with minimal exceptions']

def rtn_line_graph(x, y, col):

    if y == 'ConfirmedCases':
        log = True
    else:
        log = False
    title_l = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', y)



    line_g = px.line(top5, x=x, y=y, color=col, log_y=log, title=f'{title_l} in top five countries', )
    line_g.update_xaxes(ticktext=x_text, tickvals=x_val)

    if y == 'School closing':
        y_txt = sc_txt
        y_val = l_xval
        line_g.update_yaxes(ticktext=y_txt, tickvals=y_val)

    elif y == 'Stay at home requirements':
        y_txt = sh_txt
        y_val = l_xval
        line_g.update_yaxes(ticktext=y_txt, tickvals=y_val)

    else:
        line_g.update_yaxes()
    #
    # line_g.update_yaxes(ticktext=y_txt, tickvals=y_val)

    line_g.update_layout(paper_bgcolor = '#f9f9f9',  yaxis_title=title_l, legend_title='Country Name')


    return line_g


geo_bubble = rtn_geo_buble(df,'CountryCode','CountryCode', 'World', 'ConfirmedCases')
top5_line = rtn_line_graph('Date', 'ConfirmedCases', 'CountryName')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
        html.H2("COVID-19 Dashboard"),

        html.Div([
        html.Div([
            html.Label('Scope'),
            html.Div([
                dcc.Dropdown(id="dl_continent",
                    options=[{'label': i, 'value': i} for i in dl_continent],
                    value='World')],
                    style={'width': '50%', 'display': 'inline-block'}),

            html.Br(),
            html.Br(),

            html.Label('Input data'),
            dcc.RadioItems(id="rb_input_data",
                options=[{'label': 'Confirmed Cases', 'value': 'ConfirmedCases'},
                {'label': 'Confirmed Deaths', 'value': 'ConfirmedDeaths'},
                {'label': 'Stringency Index', 'value': 'StringencyIndex'}],
                value='ConfirmedCases'),

            html.Br(),
            html.Br(),

            html.Label('Policies'),
            dcc.RadioItems(id="rb_policies",
                options=[{'label': 'Not selected', 'value': 'Not selected'},
                {'label': 'School closing', 'value': 'School closing'},
                {'label': 'Staying at home', 'value': 'Stay at home requirements'}],
                value='Not selected'),


            html.Br(),
            ], className="four columns", style=container_style),


        html.Div([
            dcc.Graph(id='fig1', figure=top5_line)],
            className="eight columns", style = container_style)

    ], className="row", ),

html.Br(),


html.Div([
    dcc.Graph(id='fig2', figure = geo_bubble)
], className="twelve columns", style = container_style)


],style = main_page_style)


#Callback functions
@app.callback([Output('fig1', 'figure'), Output('fig2', 'figure')],[Input('dl_continent', 'value'),Input('rb_input_data', 'value'),Input('rb_policies', 'value')])
def updatefig(c,i, p):

    if p != 'Not selected':
        print(p)

        return rtn_line_graph('Date', p, 'CountryName'), rtn_chloropleth(df, 'CountryCode', p, c)
    else:
        print(c)
        return rtn_line_graph('Date', i, 'CountryName'), rtn_geo_buble(df,'CountryCode','CountryCode', c, i)

if __name__ == '__main__':
    app.run_server(debug=True)
