import dash
from dash.dependencies import Output,Input
import dash_html_components as html
import dash_core_components as dcc
import plotly
import random
import plotly.graph_objs as go
import pandas as pd
import dash_table
from collections import deque
import plotly.figure_factory as ff
import os
import pandas as pd
import numpy as np
import quandl
import time


from plotly_formulas import f_heatmap_plotly,f_density_plotly   # importing cutom build functions

from tmqrfeed import DataManager ### !!!!
from datetime import datetime



from tmqrfeed import DataManager
from tmqrcampaigns import SmartCampaign, SmartCampaignSimpleReinvesting
from tmqrcampaigns.utils import run_campaign_alphas

from tmqrcampaigns import SmartCampaignInvVolExtended, SmartCampaignInvVolBidirectional


#######  Quandl API for extracting data ######
quandl_key = '' # provide your Quandl key!!!

#insert the required product ticker https://www.quandl.com/data/CHRIS-Wiki-Continuous-Futures
sp500 = quandl.get("CHRIS/CME_ES1", api_key=quandl_key).loc['2000':].Settle.resample('D').last()
vix = quandl.get("CHRIS/CBOE_VX1", api_key=quandl_key).loc['2000':].Settle.resample('D').last()

#Eurekahedge CTA/Managed Futures Hedge Fund Index
eureka_index = quandl.get("EUREKA/476", api_key=quandl_key).loc['2000':].cumsum().add(100).Returns.resample('D').last().ffill()#.interpolate() 

prices_sp500 = (sp500['2011':])
returns_sp500 = prices_sp500.pct_change()
#######


###### function get color red or blue depending on previous day value

# color of Bid & Ask rates
def get_color(a, b):
    if a == b:
        return "white"
    elif a > b:
        return "#45df7e"
    else:
        return "#da5657"

########






external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


colors = {
	'background':'#000011',
    'background_graphs': '#111111',
    'text': '#7FDBFF'
}
app=dash.Dash('Portfolio Analyis App',
    external_stylesheets=external_stylesheets)
app.title='Portfolio Monitoring & Analysis'
app.config['suppress_callback_exceptions']=True

server = app.server



###### Data API####

### importing data
INSTRUMENT = 'US.ES'

dm = DataManager()

dm.session_set(INSTRUMENT)
#front_fut = dm.chains_futures_get(INSTRUMENT, pd.to_datetime('2017-12-01').to_pydatetime())
front_fut = dm.chains_futures_get(INSTRUMENT, datetime.now())
print(front_fut)
chain = dm.datafeed.get_fut_chain(INSTRUMENT)
df = dm.datafeed.get_raw_series(f'{front_fut}', 'quotes_intraday')
#df = dm.datafeed.get_raw_series('US.F.XAV.M12', 'quotes_intraday')
df.tail(25)





### importing  data

#df=pd.read_csv(r'es_1mins.csv',parse_dates=['dt'])[2000:].reset_index(drop=True)

df=df[2000:]
df.reset_index(inplace=True) ### !!!
print(df.head())
df['dt']=pd.to_datetime(df.dt)

##### ES_cinser. Dash Data   ####
# PORTFOLIO_CONTEXT - will contain specific settings available per account basis
#
# Current portfolio context is just for development purposes, you must set it also to
# accounts
PORTFOLIO_CONTEXT = {
    'initial_capital': 6000000,
    'risk_free_rate': 0.00, # 0.02 = 2% annual rate (for Sharpe calculations)
    'expected_daily_risk': 0.020,
    'use_reinvesting': False,
    'high_conviction_adj': True, 
    'high_conviction_on_coef': 1.0, 
    'high_conviction_off_coef': 1.5, 
    'margin_per_contract': 7000,
    'margin_max_level': 0.071,  #  <---- this is margin % cap = 0.1 = 10% of equity
}

CAMPAIGN_DICT = {
    # Unique name
    'name': "ES_Conservative_min_vol_tail_hedge",
    
    # This sections is for realtime calculation
    'products': ['US.ES'],
    
    #
    # Campaign definition
    #
    'alphas': { 


                
        'ES_Passive_Long':{'tag': 'bullish', 'w': 8.0},
        
                    'alpha_composite_ml_1_bullish':
        {
            'tag': 'bullish',
            'alphas':{
                        #ML Strats
#                     'ES_ML_Test_1_BinaryFeatures_ES_long': 1.0,
#                     'ES_ML_Test_long_for_production': 2.0,
       # Long LPBP
                    'DSP_LPBP_ES_long_cluster5_20190329_000400':1.5,
                    'DSP_LPBP_ES_long_cluster6_20190329_000400':1.0,
                    'DSP_LPBP_ES_long_cluster6_20190329_214300': 1.5,       
                    'DSP_BP_ES_long_cluster2_20190330_033400':1.0,       
                    'BollingerBands_ES_long_cluster6_20190327_175100':1.5,
                    'ML_Test_ES_long_cluster2_20190330_182600': 1.0,
                
#                     'ES_Passive_Long': 8.0,
#                     'ES_Passive_Short':0.50,
                
                        #short Alphas
                    'ML_Test_ES_short_cluster8_20190330_182300': 1.0,
                    'ML_Test_ES_short_cluster2_20190330_182000': 1.0,
#                     'DSP_LPBP_ES_short_cluster1_20190329_213700':1.0,
#                     'BollingerBands_ES_short_cluster5_20190329_234400': 1.0,
#                     'DSP_BP_ES_short_cluster1_20190330_033200': 1.0,
#                     'DSP_BP_ES_short_cluster5_20190330_033200' :1.0, 
                
#                     'BollingerBands_ES_long_cluster2_20190330_160200':2.0,
#                     'BollingerBands_ES_long_cluster5_20190330_160600':2.0,
#                     'BollingerBands_ES_long_cluster9_20190330_163800': 2.0,       
#                     'BollingerBands_ES_long_cluster2_20190330_162800':2.0,  
            }
            
        },
        
        
        
        
        'ES_Passive_Short':{'tag': 'wolfish', 'w': 8.0},    # lets vary this to 0.5 and explain what happens    are these truely stacking
        
                'alpha_composite_ml_1_bearish':
        {
            'tag': 'bearish',
            'alphas':{


       # Long LPBP
                    'DSP_LPBP_ES_long_cluster5_20190329_000400':1.0,
                    'DSP_LPBP_ES_long_cluster6_20190329_000400':1.0,
                    'DSP_LPBP_ES_long_cluster6_20190329_214300': 1.0,       
#                     'DSP_BP_ES_long_cluster2_20190330_033400':1.0,       
#                     'BollingerBands_ES_long_cluster6_20190327_175100':1.0,
#                     'ML_Test_ES_long_cluster2_20190330_182600': 1.0,
                    
#                     'ES_Passive_Short':2.0,
                
                        #short Alphas
                    'ML_Test_ES_short_cluster8_20190330_182300': 0.5,
                    'ML_Test_ES_short_cluster2_20190330_182000': 0.50,
                    'DSP_LPBP_ES_short_cluster1_20190329_213700': 0.50,
#                     'BollingerBands_ES_short_cluster5_20190329_234400': 1.0,
#                     'DSP_BP_ES_short_cluster1_20190330_033200': 1.0,
#                     'DSP_BP_ES_short_cluster5_20190330_033200' :1.0,  
                
                    'BollingerBands_ES_short_cluster3_20190330_155200_m': 0.50,
                    'BollingerBands_ES_short_cluster7_20190330_162200': 0.50,
                    'BollingerBands_ES_short_cluster4_20190330_182300':0.50,
            }
            
        },
            
        
    }

}

dm = DataManager()


dm.alpha_find_by(name='*ES_short*')

# Loads smart campaign class and context
scmp_class, scmp_dict = SmartCampaign.load(dm, "ES_Conservative_min_vol_tail_hedge")
# Runs all alphas and gets equities
alpha_dict, alpha_positions = run_campaign_alphas(scmp_dict, save_results=False)
# Initialize SmartCampaign class saved in the DB
scmp = scmp_class(scmp_dict, alpha_dict)
# Backtest smart campaign
bt_results = scmp.backtest(PORTFOLIO_CONTEXT)

alpha_dict, alpha_positions = run_campaign_alphas(CAMPAIGN_DICT, save_results=True)

# scmp = SmartCampaignSimpleReinvesting(CAMPAIGN_DICT, alpha_dict)

# High Conviction Campaign v1 unidirectional
# scmp = SmartCampaignInvVolExtended(CAMPAIGN_DICT, alpha_dict)

# High Conviction Campaign v1 bidirectional
scmp = SmartCampaignInvVolBidirectional(CAMPAIGN_DICT, alpha_dict)
bt_results = scmp.backtest(PORTFOLIO_CONTEXT)

equity_mm = bt_results['equity_mm']
equity_mm.index = equity_mm.index.tz_localize(None).floor('D')

# alphas_contracts_mm = bt_results['alphas_contracts_mm'] # Changed this to bt_results['alphas_deltas_mm'] April 25, 2019
alphas_contracts_mm = bt_results['alphas_deltas_mm']

alphas_contracts_mm.index = alphas_contracts_mm.index.tz_localize(None).floor('D')

trades=alphas_contracts_mm.diff().sum(axis=1)
net_position=alphas_contracts_mm.sum(axis=1)
pnl_dol=equity_mm.diff().dropna()
pnl_per=equity_mm['2019-04-19':].diff().div(bt_results['initial_capital'] +  (14000000)).loc['2019-04-19':].tail()*100


print(type(pnl_dol[0]))


trades=pd.DataFrame(trades).reset_index()
net_position=pd.DataFrame(net_position).reset_index()
pnl_dol=pd.DataFrame(pnl_dol).reset_index()
pnl_per=equity_mm['2019-04-19':].diff().div(bt_results['initial_capital'] +  (14000000)).loc['2019-04-19':].tail()*100
pnl_per=pd.DataFrame(pnl_per).reset_index()
equity_mm=pd.DataFrame(equity_mm).reset_index()
equity_mm2=pd.DataFrame(equity_mm).set_index('dt')
print(equity_mm)
print(trades)
print(type(trades))
time.sleep(5)
print(pnl_per)
print(equity_mm2)
print(pnl_dol.info())
###############


prices = pd.Series(equity_mm2.iloc[:,0] + 14000000)
prices.index=pd.to_datetime(prices.index)

returns = prices.pct_change()


CEP_prices = prices


### Data Api end###

#df=pd.read_csv(r'es_1mins.csv',parse_dates=['dt'])[2000:].reset_index(drop=True)



    
##### App Layout or Frontend starts from here.. (if needed to add someting that appears on screen need to add here..)
app.layout=html.Div([
    html.Div([
    html.Div([
        html.H3("Portfolio Monitoring and Analysis APP",
        style={ 
            'textAlign': 'left',
            'color': 'black'
        })],className='five columns'),
    html.Div([
        html.Img(src=app.get_asset_url(r"Logo_60.png")),
    ], className='seven columns')],className='row'),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
        dcc.Tab(label='Tab three', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])

## defyning callbacks as when change tab appropriate chart appear..

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(style={'backgroundColor': colors['background']},children=[
            html.Div([
            html.Div([
                html.Summary('YTD% PnL Date: {} Value: {}'.format(pd.to_datetime(equity_mm2.index[-1],format=r'%Y-%m-%d').strftime('%Y-%m-%d'),round((((equity_mm2.iloc[-1,0] - equity_mm2[equity_mm2.index==pd.to_datetime('2018-12-31')])/20000000)).iloc[:,0].values[0],3)),style={'color': get_color(round((((equity_mm2.iloc[-1,0] - equity_mm2[equity_mm2.index==pd.to_datetime('2018-12-31')])/20000000)).iloc[:,0].values[0],3), round((((equity_mm2.iloc[-2,0] - equity_mm2[equity_mm2.index==pd.to_datetime('2018-12-31')])/20000000)).iloc[:,0].values[0],3))}),
                html.Summary('YTD$ PnL Date: {} Value: $ {:,.2f}'.format(pd.to_datetime(equity_mm2.index[-1],format=r'%Y-%m-%d').strftime('%Y-%m-%d'),((equity_mm2.iloc[-1,0] - equity_mm2[equity_mm2.index==pd.to_datetime('2018-12-31')]).iloc[:,0].values[0])),style={'color': get_color(((equity_mm2.iloc[-1,0] - equity_mm2[equity_mm2.index==pd.to_datetime('2018-12-31')]).iloc[:,0].values[0]),((equity_mm2.iloc[-2,0] - equity_mm2[equity_mm2.index==pd.to_datetime('2018-12-31')]).iloc[:,0].values[0]))}),
                html.Summary('MTD% PnL Date: {} Value: {}'.format(pd.to_datetime(equity_mm2.index[-1],format=r'%Y-%m-%d').strftime('%Y-%m-%d'),round(((equity_mm2.iloc[-1,0] - (equity_mm2.asfreq('BM').iloc[-1,0]))/20000000),3)),style={'color': get_color(round(((equity_mm2.iloc[-1,0] - (equity_mm2.asfreq('BM').iloc[-1,0]))/20000000),3),round(((equity_mm2.iloc[-2,0] - (equity_mm2.asfreq('BM').iloc[-1,0]))/20000000),3))}),
                html.Br(),
        
    
    html.Details([
        html.Summary('Trades Date: {} Value: {}'.format(pd.to_datetime(trades.iloc[-1,0],format=r'%Y-%m-%d').strftime('%Y-%m-%d'),trades.iloc[-1,1]),style={'color': get_color(trades.iloc[-1,1],trades.iloc[-2,1])}),
        
        
        html.H4('Trades',style={'color': 'white'}),
        dash_table.DataTable(
        id='table_trades1',
        columns=[{"name": i, "id": i} for i in trades.columns],
        data=trades.iloc[-4:,:].to_dict('records'),
        style_header={'backgroundColor': colors['background_graphs']},
        style_cell={
            'backgroundColor': colors['background_graphs'],
            'color': 'white'
        })
    ]),
    
    html.Details([
        html.Summary('Net Position Date: {} Value: {:,.2f}'.format(pd.to_datetime(net_position.iloc[-1,0],format=r'%Y-%m-%d').strftime('%Y-%m-%d'),net_position.iloc[-1,1]),style={'color': get_color(net_position.iloc[-1,1],net_position.iloc[-2,1])}),
        
            html.H4('Net Position',style={'color': 'white'}),
            dash_table.DataTable(
            id='table_net_position1',
            columns=[{"name": i, "id": i} for i in net_position.columns],
            data=net_position.iloc[-4:,:].to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            })],className='row'),
    
    
    html.Details([
        html.Summary('PNL in $ Date: {} Value: $ {:,.2f}'.format(pd.to_datetime(pnl_dol.iloc[-1,0],format='%Y-%m-%d').strftime('%Y-%m-%d'),pnl_dol.iloc[-1,1]),style={'color': get_color(pnl_dol.iloc[-1,1],pnl_dol.iloc[-2,1])}),
        
            html.Div([html.H4('PNL in $',style={'color': 'white'}),
            dash_table.DataTable(
            id='table_pnl1',
            columns=[{"name": i, "id": i} for i in pnl_dol.columns],
            data=pnl_dol.iloc[-4:,:].to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            })
            ], className="four columns", style = {'margin-top': '35',
                                               'margin-left': '15',
                                               'border': '1px solid #C6CCD5'})],className='row'),
    
    html.Details([
        html.Summary('PNL in % Date: {} Value: {}'.format(pd.to_datetime(pnl_per.iloc[-1,0],format='%Y-%m-%d').strftime('%Y-%m-%d'),round(pnl_per.iloc[-1,1],2)),style={'color': get_color(round(pnl_per.iloc[-1,1],2),round(pnl_per.iloc[-2,1],2))}),
        
        html.Div([
            html.H4('PNL in %',style={'color': 'white'}),
            dash_table.DataTable(
            id='pnl_table_per1',
            columns=[{"name": i, "id": i} for i in pnl_per.columns],
            data=pnl_per.iloc[-4:,:].to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            })
            ], className="four columns")],className='row'),
    
        dcc.Graph(id='net_position_bar',
            figure={
            'data' : [go.Bar(
            x=net_position.iloc[-5:,0],
            y=net_position.iloc[-5:,1]
        )],'layout':{'title': 'Net Position Last 5 days',
                    'width': 550,
                    'height': 350,
                    'plot_bgcolor': colors['background_graphs'],
                    'paper_bgcolor': colors['background_graphs'],
                    'font': {
                        'color': colors['text']
                    }}}),
                ],className='five columns'),
            html.Div([

                dcc.Graph(id='candlestick',animate=True),
                    dcc.Interval(
                    id='interval-component',
                    interval=30*1000, # in milliseconds
                    n_intervals=0
                ),

        dcc.Graph(id='closing_price_line',animate=True)], className="seven columns"),
                
            
        
                
            ], className='row')],className='row')
    
    elif tab == 'tab-2':
        return html.Div([
            html.Div([
     html.Div([

        dcc.Graph(id='equity_mm_line',
            figure={
            'data' : [go.Scatter(
            x=equity_mm.iloc[:,0],
            y=equity_mm.iloc[:,1],
            mode='lines'
        )],'layout':{'title': 'Historical Equity MM Line',
                    'width':1300,
                    'height':600,
                    'plot_bgcolor': colors['background_graphs'],
                    'paper_bgcolor': colors['background_graphs'],
                    'font': {
                        'color': colors['text']
                    }
}}
            )], className="six columns"),
     

        ], className="row"),
            html.Div([
        html.Div([
            dcc.RadioItems(
                id='returns_hist_check',
                options=[
                    {'label': 'Weekly frequency', 'value': 'W'},
                    {'label': 'Semi-month end frequency (15th and end of month)', 'value': 'SM'},
                    {'label': 'Month end frequency', 'value': 'M'},
                    {'label': 'Quarter end frequency', 'value': 'Q'}
                ],
                value='W',
                labelStyle={'display': 'inline-block'},
                style={ 
                    'textAlign': 'left',
                    'color': colors['text']
                }
                ),
     

        ], className="row"),
            html.Div([

        dcc.Graph(id='returns_hist')], className="twelve columns")
            ])
        ], className="row")

    elif tab == 'tab-3':
        return html.Div([
             html.Div([
     html.Div([

        dcc.Graph(id='monthly_returns_heatmap',
            figure=f_heatmap_plotly(prices, title='Monthly Conservative Enhanced PAM Returns (%)', eoy=True, is_prices=True, compounded=False) 
            )], className="twelve columns")

        ], className="row"),
        html.Div([
     html.Div([

        dcc.Graph(id='monthly_returns_sp500_heatmap',
            figure=f_heatmap_plotly(prices_sp500, title='Monthly S&P 500 Returns (%)', eoy=True, is_prices=True, compounded=False) 
            )], className="twelve columns")

        ], className="row")
            
        ], className="row")
    

@app.callback(
    [Output('candlestick', 'figure'),
     Output('closing_price_line', 'figure')],
    [Input('interval-component', 'n_intervals')])
def update_graph(input):
	
	#front_fut = dm.chains_futures_get(INSTRUMENT, pd.to_datetime('2017-12-01').to_pydatetime())
	front_fut = dm.chains_futures_get(INSTRUMENT, datetime.now())
	
	chain = dm.datafeed.get_fut_chain(INSTRUMENT)
	df = dm.datafeed.get_raw_series(f'{front_fut}', 'quotes_intraday')
	#df = dm.datafeed.get_raw_series('US.F.XAV.M12', 'quotes_intraday')
	

	df=df[-420:].reset_index() ### candlestick rollover value
	
	df['dt']=pd.to_datetime(df.dt)
	print(df.tail())
    
	
    

	return {
        'data': [go.Candlestick(x=list(df.dt),
                open=list(df.o),
                high=list(df.h),
                low=list(df.l),
                close=list(df.c),
                increasing=dict(line=dict(color= 'blue')),
                decreasing=dict(line=dict(color= 'red'))
                )],
        'layout': go.Layout(
            xaxis={'title': 'dt','range': [pd.Series(df.dt).min(), pd.Series(df.dt).max()]},
            yaxis={'title': 'value', 'range': [pd.Series(df.l).min(), pd.Series(df.h).max()]},
            # width=1250,
            # height=600,
            title={'text':'Futures Candlestick','font':{'size':20}},
            plot_bgcolor =colors['background_graphs'],
            paper_bgcolor=colors['background_graphs'],
            font={'color': colors['text']}
    )},{
        'data': [go.Scatter(
            x=list(df.dt),
            y=list(df.c),
            mode='lines'
        )],
        'layout': go.Layout(
            xaxis={'title': 'dt','range': [pd.Series(df.dt).min(), pd.Series(df.dt).max()]},
            yaxis={'title': 'value', 'range': [pd.Series(df.c).min(), pd.Series(df.c).max()]},
            # width=600,
            # height=400,
            title={'text':'Closing Price','font':{'size':20}},
            plot_bgcolor =colors['background_graphs'],
            paper_bgcolor=colors['background_graphs'],
            font={'color': colors['text']}
    )}


@app.callback(
    Output('returns_hist', 'figure'),
    [Input('returns_hist_check', 'value')])
def update_graph(input):
	return f_density_plotly([returns,returns_sp500], group_labels=['returns','returns_sp500'],period=input)
            
### Dash app always need to be fininshed with below code..
if __name__ == '__main__':
	app.run_server(debug=True)
