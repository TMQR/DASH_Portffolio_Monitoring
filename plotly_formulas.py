import pandas as pd
import plotly.plotly as py
import numpy as np

import plotly.graph_objs as go
import plotly.figure_factory as ff

colors = {
    'background':'#000011',
    'background_graphs': '#111111',
    'text': '#7FDBFF'
}


def sum_returns(returns, groupby, compounded=True):
    def returns_prod(data):
        return (data + 1).prod() - 1
    if compounded:
        return returns.groupby(groupby).apply(returns_prod)
    return returns.groupby(groupby).sum()


def get(returns, eoy=False, is_prices=False, compounded=True):

    # get close / first column if given DataFrame
    if isinstance(returns, pd.DataFrame):
        returns.columns = map(str.lower, returns.columns)
        if len(returns.columns) > 1 and 'close' in returns.columns:
            returns = returns['close']
        else:
            returns = returns[returns.columns[0]]

    # convert price data to returns
    if is_prices:
        returns = returns.pct_change()

    original_returns = returns.copy()

    # build monthly dataframe
    # returns_index = returns.resample('MS').first().index
    # returns_values = sum_returns(returns,
    #     [returns.index.year, returns.index.month]).values
    # returns = pd.DataFrame(index=returns_index, data={
    #                        'Returns': returns_values})

    # simpler, works with pandas 0.23.1
    returns = pd.DataFrame(sum_returns(returns,
                                       returns.index.strftime('%Y-%m-01'),
                                       compounded))
    returns.columns = ['Returns']
    returns.index = pd.to_datetime(returns.index)

    # get returnsframe
    returns['Year'] = returns.index.strftime('%Y')
    returns['Month'] = returns.index.strftime('%b')

    # make pivot table
    returns = returns.pivot('Year', 'Month', 'Returns').fillna(0)

    # handle missing months
    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        if month not in returns.columns:
            returns.loc[:, month] = 0

    # order columns by month
    returns = returns[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]

    if eoy:
        returns['eoy'] = sum_returns(original_returns,
                                     original_returns.index.year).values
    
    return returns


def f_heatmap_plotly(returns,
         title='Monthly Conservative Enhanced PAM Returns (%)',
         title_size=14,
         annot_size=10,
         figsize=None,
         colorscale='Portland',
         square=False,
         is_prices=False,
         compounded=True,
         eoy=False):

    returns = get(returns, eoy=eoy, is_prices=is_prices, compounded=compounded)
    returns *= 100

    
    
    fig=ff.create_annotated_heatmap(z=np.array(returns), x=list(returns.columns), y=list(returns.index), annotation_text=np.around(np.array(returns),decimals=2), colorscale='Viridis')
    fig.layout.update({'title': title})
    fig.layout.update({'plot_bgcolor': colors['background_graphs']})
    fig.layout.update({'paper_bgcolor': colors['background_graphs']})
    fig.layout.update({'font': {'color': colors['text']}})
    fig.layout.update({'width': 1300})
    fig.layout.update({'height': 700})
    fig['data'][0]['showscale'] = True
    #     trace = go.Heatmap(
#     z=np.array(returns),
#     y=returns.index,
#     x=returns.columns,
#     colorscale=colorscale,
#     colorbar = dict(
#                 title = 'Monthly Returns Rate in %',
#                 titleside = 'top',
#                 tickmode = 'array',
#                 tickvals = [0,50,100],
#                 ticktext = ['0 %','50 %','100%'],
#                 ticks = 'outside'
#             ))
#     data = [trace]

#     layout = dict(width = 1500, height = 900,
#                 autosize = False,title=title,
#                  xaxis=dict(title='Month'),
#                  yaxis=dict(title='Year'))

#     fig = go.Figure(data=data,layout=layout)

    return fig


def f_density_plotly(returns,
         title='Returns Density Plot',
         title_size=14,
         period='W',
         group_labels=['returns']):

    fig=ff.create_distplot([i.resample(period).mean().dropna().values for i in returns], group_labels=group_labels,histnorm='probability density',bin_size=0.0002)
    
    fig.layout.update({'title': title})
    fig.layout.update({'plot_bgcolor': colors['background_graphs']})
    fig.layout.update({'paper_bgcolor': colors['background_graphs']})
    fig.layout.update({'font': {'color': colors['text']}})
    fig.layout.update({'width': 1300})
    fig.layout.update({'height': 700})
    

    return fig


