import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

#  Завантаження та підготовка даних
def load_weather(path: str = 'weather2026.csv') -> pd.DataFrame:
    df = pd.read_csv(path, encoding='UTF-8')

    df['період'] = df['період'].fillna('2026-04')

    df['хмарність_num'] = (
        df['хмарність'].str.replace('%', '', regex=False).astype(int)
    )

    df['опади_num'] = (
        df['опади']
        .str.replace(' м.м.', '', regex=False)
        .replace('-', '0')
        .astype(float)
    )

    df['день_темп'] = (
        df['денна температура повітря'].str.replace('°C', '', regex=False).astype(float)
    )
    df['ніч_темп'] = (
        df['нічна температура повітря'].str.replace('°C', '', regex=False).astype(float)
    )

    df['вітер_num'] = (
        df['сила вітру'].str.replace(' м/с', '', regex=False).astype(int)
    )

    df['тип_хмарності'] = pd.cut(
        df['хмарність_num'],
        bins=[-1, 34, 70, 100],
        labels=['Сонячний', 'Мінлива хмарність', 'Хмарний']
    )

    df['є_опади'] = df['опади_num'] > 0

    return df


df = load_weather()
periods = sorted(df['період'].unique())

GRAPH_OPTIONS = [
    {'label': 'а) Температура (денна та нічна)', 'value': 'temp'},
    {'label': 'б) Хмарність',                   'value': 'cloud'},
    {'label': 'в) Сила вітру',                  'value': 'wind'},
    {'label': 'г) Бульбашковий (температура/опади)', 'value': 'bubble'},
]

ANALYTICS_OPTIONS = [
    {'label': 'а) Відхилення нічної від денної температури', 'value': 'deviation'},
    {'label': 'б) Типи хмарності по місяцях (накопичена)',   'value': 'cloud_types'},
    {'label': 'в) Сонячний вибух (Sunburst)',                'value': 'sunburst'},
    {'label': 'г) Дні з опадами за весь період (кругова)',   'value': 'rain_pie'},
]

CLOUD_COLORS = {
    'Сонячний':          '#F9BF3B',
    'Мінлива хмарність': '#BDC3C7',
    'Хмарний':           '#5D6D7E',
}

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

_card = lambda children: html.Div(children, style={
    'background': '#F4F6F8',
    'padding': '22px 26px',
    'borderRadius': '12px',
    'marginBottom': '22px',
    'boxShadow': '0 2px 6px rgba(0,0,0,.08)',
})

_label_style = {'fontWeight': '600', 'fontSize': 14, 'color': '#2C3E50', 'marginBottom': 4}

app.layout = html.Div([

    html.Div([
        html.H1('🌤 Weather App 2025–2026', style={
            'margin': 0, 'fontSize': 28, 'color': '#2C3E50'
        }),
        html.P('Виконавець: Сєров Едуард Олегович  |  Група: К-26', style={
            'margin': '6px 0 0', 'fontSize': 13, 'color': '#7F8C8D'
        }),
    ], style={
        'textAlign': 'center', 'padding': '24px 0 16px',
        'borderBottom': '2px solid #D5D8DC', 'marginBottom': '22px'
    }),

    # Секція 1: Графіки за місяць
    _card([
        html.H2('📊 Графіки за обраний місяць',
                style={'margin': '0 0 14px', 'fontSize': 18, 'color': '#2980B9'}),

        html.Div([
            html.Div([
                html.P('Тип графіку:', style=_label_style),
                dcc.Dropdown(
                    id='graph-type',
                    options=GRAPH_OPTIONS,
                    placeholder='Оберіть тип графіку…',
                    style={'fontSize': 15},
                ),
            ], style={'flex': '1', 'marginRight': 16}),

            html.Div([
                html.P('Місяць:', style=_label_style),
                dcc.Dropdown(
                    id='month-select',
                    options=[{'label': p, 'value': p} for p in periods],
                    placeholder='Оберіть місяць…',
                    style={'fontSize': 15},
                ),
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': 12}),

        dcc.Graph(id='monthly-graph', config={'displayModeBar': True}),
    ]),

    # Секція 2: Аналітика
    _card([
        html.H2('📈 Аналітика за весь період спостережень',
                style={'margin': '0 0 14px', 'fontSize': 18, 'color': '#27AE60'}),

        html.P('Вид аналітики:', style=_label_style),
        dcc.Dropdown(
            id='analytics-type',
            options=ANALYTICS_OPTIONS,
            placeholder='Оберіть вид аналітики…',
            style={'fontSize': 15, 'marginBottom': 12},
        ),

        dcc.Graph(id='analytics-graph', config={'displayModeBar': True}),
    ]),

], style={
    'maxWidth': 1100,
    'margin': '0 auto',
    'fontFamily': '"Segoe UI", Arial, sans-serif',
    'padding': '0 18px 40px',
})


#  Callback 1: Місячні графіки
@app.callback(
    Output('monthly-graph', 'figure'),
    Input('graph-type', 'value'),
    Input('month-select', 'value'),
)
def update_monthly(graph_type, month):
    if not graph_type or not month:
        fig = go.Figure()
        fig.update_layout(
            title='← Оберіть тип графіку та місяць',
            plot_bgcolor='white', paper_bgcolor='white',
        )
        return fig

    d = df[df['період'] == month].sort_values('день')

    # а) Температура
    if graph_type == 'temp':
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=d['день'], y=d['день_темп'],
            mode='lines+markers', name='Денна температура',
            line=dict(color='#E74C3C', width=2),
            marker=dict(size=6),
        ))
        fig.add_trace(go.Scatter(
            x=d['день'], y=d['ніч_темп'],
            mode='lines+markers', name='Нічна температура',
            line=dict(color='#2E86C1', width=2, dash='dot'),
            marker=dict(size=6),
        ))
        fig.update_layout(
            title=f'Денна та нічна температура повітря — {month}',
            xaxis_title='День місяця',
            yaxis_title='Температура (°C)',
        )

    # б) Хмарність
    elif graph_type == 'cloud':
        fig = go.Figure(go.Bar(
            x=d['день'], y=d['хмарність_num'],
            marker_color='#85C1E9', name='Хмарність',
            text=d['хмарність'], textposition='outside',
        ))
        fig.update_layout(
            title=f'Хмарність — {month}',
            xaxis_title='День місяця',
            yaxis_title='Хмарність (%)',
            yaxis=dict(range=[0, 115]),
        )

    # в) Вітер
    elif graph_type == 'wind':
        fig = go.Figure(go.Scatter(
            x=d['день'], y=d['вітер_num'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(26,188,156,0.2)',
            line=dict(color='#1ABC9C', width=2),
            marker=dict(size=6),
            name='Сила вітру',
            text=d['сила вітру'],
            hovertemplate='День %{x}<br>Вітер: %{text}<extra></extra>',
        ))
        fig.update_layout(
            title=f'Сила вітру — {month}',
            xaxis_title='День місяця',
            yaxis_title='Швидкість вітру (м/с)',
        )

    # г) Бульбашковий
    elif graph_type == 'bubble':
        bubble_size = d['опади_num'].replace(0, 0.3) * 12 + 8

        fig = go.Figure(go.Scatter(
            x=d['день'],
            y=d['день_темп'],
            mode='markers',
            marker=dict(
                size=bubble_size,
                color=d['день_темп'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title='°C'),
                opacity=0.8,
                line=dict(width=1, color='#555'),
            ),
            text=d['опади'],
            hovertemplate=(
                'День %{x}<br>'
                'Денна температура: %{y}°C<br>'
                'Опади: %{text}<extra></extra>'
            ),
            name='Температура / Опади',
        ))
        fig.update_layout(
            title=(
                f'Денна температура — {month}<br>'
                '<sup>Розмір бульбашки відповідає кількості опадів</sup>'
            ),
            xaxis_title='День місяця',
            yaxis_title='Денна температура (°C)',
        )

    _apply_style(fig)
    return fig


#  Callback 2: Аналітика
@app.callback(
    Output('analytics-graph', 'figure'),
    Input('analytics-type', 'value'),
)
def update_analytics(analytics_type):
    if not analytics_type:
        fig = go.Figure()
        fig.update_layout(
            title='← Оберіть вид аналітики',
            plot_bgcolor='white', paper_bgcolor='white',
        )
        return fig

    # а) Гістограма відхилення
    if analytics_type == 'deviation':
        d = df.copy()
        d['відхилення'] = d['день_темп'] - d['ніч_темп']
        fig = px.histogram(
            d, x='відхилення', nbins=22,
            color_discrete_sequence=['#8E44AD'],
            title='Відхилення денної температури від нічної (за весь період)',
            labels={'відхилення': 'Відхилення денна − нічна (°C)', 'count': 'Кількість днів'},
        )
        fig.update_layout(yaxis_title='Кількість днів', bargap=0.05)

    # б) Накопичена стовпчикова
    elif analytics_type == 'cloud_types':
        counts = (
            df.groupby(['період', 'тип_хмарності'], observed=True)
              .size()
              .reset_index(name='кількість')
        )
        fig = px.bar(
            counts,
            x='період', y='кількість', color='тип_хмарності',
            barmode='stack',
            color_discrete_map=CLOUD_COLORS,
            title='Кількість сонячних, мінливих та хмарних днів по місяцях',
            labels={
                'кількість': 'Кількість днів',
                'період': 'Місяць',
                'тип_хмарності': 'Тип дня',
            },
        )
        fig.update_layout(xaxis_tickangle=-30)

    # в) Sunburst
    elif analytics_type == 'sunburst':
        tmp = df.copy()
        tmp['тип_хмарності'] = tmp['тип_хмарності'].astype(str)
        counts = (
            tmp.groupby(['період', 'тип_хмарності'], observed=True)
               .size()
               .reset_index(name='кількість')
        )
        fig = px.sunburst(
            counts,
            path=['період', 'тип_хмарності'],
            values='кількість',
            color='тип_хмарності',
            color_discrete_map=CLOUD_COLORS,
            title='Розподіл типів хмарності по місяцях — «Сонячний вибух»',
        )

    # г) Кругова: кількість дощових днів у кожному місяці
    elif analytics_type == 'rain_pie':
        rain_by_month = (
            df[df['є_опади']]
            .groupby('період')
            .size()
            .reset_index(name='дні_з_опадами')
            .sort_values('період')
        )
        fig = go.Figure(go.Pie(
            labels=rain_by_month['період'],
            values=rain_by_month['дні_з_опадами'],
            textinfo='label+value+percent',
            hovertemplate='%{label}<br>Днів з опадами: %{value}<br>%{percent}<extra></extra>',
        ))
        fig.update_layout(
            title='Кількість днів з опадами у кожному місяці (за весь період спостережень)',
        )

    _apply_style(fig)
    return fig


#  Допоміжна функція стилю
def _apply_style(fig: go.Figure) -> None:
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='"Segoe UI", Arial, sans-serif', size=13),
        legend=dict(orientation='h', y=-0.18),
        margin=dict(l=50, r=30, t=70, b=60),
        title_font_size=16,
    )
    fig.update_xaxes(showgrid=True, gridcolor='#EAECEE')
    fig.update_yaxes(showgrid=True, gridcolor='#EAECEE')


if __name__ == '__main__':
    app.run()
