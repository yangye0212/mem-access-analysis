from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px

import pandas as pd
import plotly.graph_objs as go

df = pd.read_csv('./csvs/lite.csv')

df['vaddr_dec_value'] = df['vaddr(hex)'].apply(lambda x: int(x, 16))

color_map = {
    'ld': 'blue',
    'st': 'red'
}

df['color']=df['type'].map(color_map)

app = Dash()

# 创建点阵图数据
scatter_data = []
for t in df['type'].unique():
    df_t = df[df['type'] == t]
    scatter_data.append(
        go.Scatter(
            x=df_t['instret'],
            y=df_t['vaddr_dec_value'],
            mode='markers',
            marker=dict(size=10, color=df_t['color'].iloc[0]),
            text=df_t['vaddr(hex)'],  # 使用原始十六进制数据作为文本标签
            name=t,
            legendgroup=t,
            hovertemplate=(# 定制悬停提示模板
                'instret: %{x}<br>'
                'vaddr: %{text}<br>'
                'pc: %{customdata}<extra></extra>'
            ),
            customdata=df['pc'].values
        )
    )

fig = go.Figure(data=scatter_data)

fig.update_layout(
    yaxis=dict(
        tickmode='array',
        tickvals=df['vaddr_dec_value'],
        ticktext=df['vaddr(hex)']
    ),
    margin=dict(l=0,r=0,t=20,b=40)# 调整图形的边距
)

app.layout = html.Div([
    html.H1(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
        children='Memory Access'
    ),

    html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},

        children = [
            dcc.Dropdown(
                id='type-dropdown',
                options=[
                    {'label': 'All Types', 'value': 'All'},
                    {'label': 'load', 'value': 'ld'},
                    {'label': 'store', 'value': 'st'}
                ],
                value='All',   # 默认选中第一个类型
                clearable=False, # 不允许清除选择
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
  

    dcc.Graph(
        id='mem-access-graph',
        figure=fig,
        style={'width': '98vw', 'height': '80vh'}
    )

]
)

@app.callback(
    Output('mem-access-graph', 'figure'),
    [Input('type-dropdown', 'value'),
     Input('pc-dropdown', 'value')]
)
def update_graph(selected_type, selected_pc):
    # selected by type
    if selected_type is None or 'All' in selected_type:
        df_filtered = df
    else:
        # 根据所选type筛选数据
        if (isinstance(selected_type, str)):
            selected_type = [selected_type]
        df_filtered = df[df['type'].isin(selected_type)]

    # selected by pc
    if selected_pc is not None and len(selected_pc) > 0:
        # 根据所选pc进一步筛选数据
        df_filtered = df_filtered[df_filtered['pc'].isin(selected_pc)]

    # 创建图形
    # 创建点阵图数据
    scatter_data = []
    for t in df_filtered['type'].unique():
        df_t = df_filtered[df_filtered['type'] == t]
        scatter_data.append(
            go.Scatter(
                x=df_t['instret'],
                y=df_t['vaddr_dec_value'],
                mode='markers',
                marker=dict(size=10, color=df_t['color'].iloc[0]),
                text=df_t['vaddr(hex)'],  # 使用原始十六进制数据作为文本标签
                name=t,
                legendgroup=t,
                hovertemplate=(# 定制悬停提示模板
                    'instret: %{x}<br>'
                    'vaddr: %{text}<br>'
                    'pc: %{customdata}<extra></extra>'
                ),
                customdata=df['pc'].values
            )
        )

    fig = go.Figure(data=scatter_data)

    # 定制y轴标签格式
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=df['vaddr_dec_value'],
            ticktext=df['vaddr(hex)']
        ),
        margin=dict(l=0, r=0, t=20, b=40)  # 调整图形的边距
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)