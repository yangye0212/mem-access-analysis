from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

# 定义每页显示的数据量
CSV_FILE='./csvs/lite.csv'
PAGE_SIZE = 1000
df = pd.read_csv(CSV_FILE, nrows=PAGE_SIZE)

df['vaddr_dec_value'] = df['vaddr'].apply(lambda x: int(x, 16))

color_map = {
    'ld': 'blue',
    'st': 'red'
}

df['color'] = df['type'].map(color_map)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Row(
        dbc.Col(
            html.H1(
                style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
                className='text-center text-primary mb-4',
                children='Memory Access'
            ),
        )
    ),
    html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
        children=[
            dcc.Dropdown(
                id='type-dropdown',
                options=[
                    {'label': 'All Types', 'value': 'All'},
                    {'label': 'load', 'value': 'ld'},
                    {'label': 'store', 'value': 'st'}
                ],
                value='All',  # 默认选中第一个类型
                clearable=False,  # 不允许清除选择
                searchable=False,  # 禁用搜索
                style={'width': '150px', 'marginRight': '40px'}
            ),
            dcc.Dropdown(
                id='pc-dropdown',
                options=[
                    {'label': pc, 'value': pc} for pc in df['pc'].unique()
                ],
                multi=True,  # 允许多选
                placeholder='Select PC',  # 设置占位符
                style={'width': '150px', 'marginRight': '40px', 'textAlign': 'left', 'verticalAlign': 'middle'}  # 设置筛选器宽度为150像素
            ),
            dcc.Dropdown(
                id='line-dropdown',
                options=[
                    {'label': '点阵图', 'value': 'scatter'},
                    {'label': '折线图', 'value': 'line'}
                ],
                value='scatter',  # 默认选中点阵图
                clearable=False,  # 不允许清除选择
                searchable=False,  # 禁用搜索
                style={'width': '150px', 'marginRight': '40px'}
            ),
            html.Div(
                style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '20px'},
                children=[
                    html.Div(
                        style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'},
                        children=[
                            html.Div(
                                style={'width': '20px', 'height': '20px', 'backgroundColor': 'blue', 'borderRadius': '50%', 'marginRight': '10px'}
                            ),
                            html.Span('load')
                        ]
                    ),
                    html.Div(
                        style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'},
                        children=[
                            html.Div(style={'width': '20px', 'height': '20px', 'backgroundColor': 'red', 'borderRadius': '50%', 'marginRight': '10px'}),
                            html.Span('store')
                        ]
                    )
                ]
            )
        ]
    ),
    html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginTop': '20px'},
        children=[
            dcc.RadioItems(
                id='toggle-axis',
                options=[
                    {'label': 'Both Y Axes', 'value': 'both'},
                    {'label': 'Left Y Axis', 'value': 'left'},
                    {'label': 'Right Y Axis', 'value': 'right'}
                ],
                value='both',
                style={'marginLeft': '20px'}
            )
        ]
    ),
    dcc.Graph(
        id='mem-access-graph',
        style={'width': '98vw', 'height': '80vh'}
    ),
    dbc.Pagination(
        id='pagination',
        active_page=1,
        max_value=1,  # 暂时设为1，稍后在回调中更新
        fully_expanded=False,
        previous_next=True,
        first_last=True
    )
], style={'backgroundColor': '#d3d3d3', 'height': '100vh', 'padding': '20px'}
)


@app.callback(
    Output('pagination', 'max_value'),
    Input('pagination', 'active_page')
)
def update_max_value(active_page):
    df = pd.read_csv(CSV_FILE)
    return (len(df) + PAGE_SIZE - 1) // PAGE_SIZE  # 计算页数


@app.callback(
    Output('mem-access-graph', 'figure'),
    [Input('pagination', 'active_page'),
     Input('type-dropdown', 'value'),
     Input('pc-dropdown', 'value'),
     Input('line-dropdown', 'value'),
     Input('toggle-axis', 'value')]
)
def update_graph(active_page, selected_type, selected_pc, selected_line_mode, toggle_axis):
    if active_page is None:
        active_page = 1

    start_idx = (active_page - 1) * PAGE_SIZE
    df_page = pd.read_csv(CSV_FILE, skiprows=range(1, start_idx + 1), nrows=PAGE_SIZE)

    df_page['vaddr_dec_value'] = df_page['vaddr'].apply(lambda x: int(x, 16))
    df_page['color'] = df_page['type'].map(color_map)

    if selected_type and selected_type != 'All':
        df_filtered = df_page[df_page['type'] == selected_type]
    else:
        df_filtered = df_page

    if selected_pc:
        df_filtered = df_filtered[df_filtered['pc'].isin(selected_pc)]

    mode = 'markers' if selected_line_mode == 'scatter' else 'lines+markers'

    scatter_data = []
    line_data = []

    if toggle_axis in ['both', 'left']:
        for t in df_filtered['type'].unique():
            df_t = df_filtered[df_filtered['type'] == t]
            scatter_data.append(
                go.Scatter(
                    x=df_t['instret'],
                    y=df_t['vaddr_dec_value'],
                    mode=mode,
                    marker=dict(size=10, color=df_t['color'].iloc[0]),
                    text=df_t['vaddr'],
                    name=t,
                    legendgroup=t,
                    hovertemplate=(
                        'instret: %{x}<br>'
                        'vaddr: %{text}<br>'
                        'pc: %{customdata}<extra></extra>'
                    ),
                    customdata=df_t['pc'].values
                )
            )

    if toggle_axis in ['both', 'right']:
        line_data.append(
            go.Scatter(
                x=df_filtered['instret'],
                y=df_filtered['pc'],
                mode='lines+markers',
                name='PC',
                yaxis='y2',
                line=dict(color='orange')
            )
        )

    fig = go.Figure(data=scatter_data + line_data)

    yaxis_config = {
        'title': 'Virtual Address',
        'tickmode': 'array',
        'tickvals': df_filtered['vaddr_dec_value'],
        'ticktext': df_filtered['vaddr']
    }

    yaxis2_config = {
        'title': 'PC',
        'overlaying': 'y',
        'side': 'right'
    }

    if toggle_axis == 'left':
        yaxis2_config['showticklabels'] = False
        fig.update_layout(yaxis=yaxis_config, yaxis2=dict(showticklabels=False, visible=False))
    elif toggle_axis == 'right':
        fig.update_layout(yaxis=dict(showticklabels=False, visible=False), yaxis2=yaxis2_config)
    else:
        fig.update_layout(yaxis=yaxis_config, yaxis2=yaxis2_config)

    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=40)
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
