# scripts/viz.py (v4.0 - Expert Storytelling Dashboard)

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

# --- Step 1: Load the Enriched Data ---
try:
    df_biochemistry = pd.read_csv('data/biochemistry.csv')
    df_hematology = pd.read_csv('data/hematology.csv')
    with open('data/clinical_insights.json', 'r', encoding='utf-8') as f:
        insights_data = json.load(f)
    with open('data/ultrasound_findings.json', 'r', encoding='utf-8') as f:
        ultrasound_data = json.load(f)
except FileNotFoundError:
    print("ERROR: Data files not found. Please run 'scripts/data_parser.py' (v3.0) first.")
    exit()

# --- Step 2: Initialize the Dash App ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME])
server = app.server

# --- Step 3: Define the Application Layout ---
app.layout = dbc.Container(fluid=True, className="p-4 bg-light", children=[
    # Header
    html.Div(
        className='p-4 text-white text-center rounded shadow-lg mb-4',
        style={'background': 'linear-gradient(135deg, #2c3e50, #34495e)'},
        children=[
            html.H1('Dashboard de Análise Clínica Preditiva'),
            html.H2(f"Paciente: {insights_data['patient_id']}", className='text-xl font-light')
        ]
    ),
    
    # Main content area with a two-column layout
    dbc.Row([
        # Left Column for high-level insights and navigation
        dbc.Col(md=4, children=[
            dbc.Card(dbc.CardBody([
                html.H4("Sumário e Hipóteses", className="card-title"),
                html.P(f"Hipótese Principal: {insights_data['primary_hypothesis']['name_pt']}", className="text-danger font-weight-bold"),
                html.P(f"Risco Secundário: {insights_data['secondary_concerns'][0]['name_pt']}", className="text-warning font-weight-bold"),
            ])),
            html.Br(),
            dbc.Card(dbc.CardBody([
                html.H4("Navegador de Achados", className="card-title"),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem("Bexiga (Cistite)", id="nav-bladder", n_clicks=0, action=True, color="danger"),
                        dbc.ListGroupItem("Rins (Nefropatia)", id="nav-kidneys", n_clicks=0, action=True, color="warning"),
                        dbc.ListGroupItem("Hérnia Umbilical", id="nav-hernia", n_clicks=0, action=True, color="info"),
                    ],
                    id="organ-nav-listgroup",
                    flush=True,
                )
            ]))
        ]),
        
        # Right Column for detailed visualizations
        dbc.Col(md=8, children=[
            dbc.Card(id='details-card', children=[
                # This content will be updated by the callback
            ])
        ])
    ])
])

# --- Step 4: Callbacks for Interactivity ---

@app.callback(
    Output('details-card', 'children'),
    [Input('nav-bladder', 'n_clicks'),
     Input('nav-kidneys', 'n_clicks'),
     Input('nav-hernia', 'n_clicks')]
)
def display_details_card(b_clicks, k_clicks, h_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'nav-bladder' # Default view
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    organ_map = {"nav-bladder": "Urinary Bladder", "nav-kidneys": "Kidneys", "nav-hernia": "Abdominal Wall"}
    selected_organ = organ_map.get(button_id)
    finding = next((item for item in ultrasound_data['pathological_findings'] if item["organ"] == selected_organ), None)
    if not finding: return dbc.CardBody(html.P("Selecione um achado."))

    # --- Advanced Visualizations ---
    
    # 1. Sunburst Chart for Biochemistry
    sunburst_fig = go.Figure(go.Sunburst(
        labels=["Alta", "Normal", "Ureia", "Creatinina", "ALT", "Fosfatase"],
        parents=["", "", "Alta", "Normal", "Normal", "Normal"],
        values=[df_biochemistry[df_biochemistry['status']=='High']['value'].sum(), df_biochemistry[df_biochemistry['status']=='Normal']['value'].sum(), 84.9, 1.18, 25.4, 17.9],
        marker=dict(colors=['#dc3545', '#198754', '#ff7f0e', '#1f77b4', '#2ca02c', '#9467bd']),
        hovertemplate='<b>%{label}</b><br>Valor: %{value}',
        branchvalues="total"
    ))
    sunburst_fig.update_layout(margin=dict(t=20, l=20, r=20, b=20), title_text="Distribuição Bioquímica")

    # 2. Treemap for Hematology
    treemap_fig = px.treemap(
        df_hematology,
        path=[px.Constant("Hemograma"), 'status', 'parameter'],
        values='value',
        color='status',
        color_discrete_map={'High': '#dc3545', 'Low': '#ffc107', 'Normal': '#198754'},
        hover_data={'value':':.2f'}
    )
    treemap_fig.update_layout(margin=dict(t=20, l=20, r=20, b=20), title_text="Composição do Hemograma")
    
    # 3. Gauge Indicator for Severity
    severity_map = {"Urinary Bladder": 85, "Kidneys": 40, "Abdominal Wall": 25}
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = severity_map.get(selected_organ, 0),
        title = {'text': "Nível de Criticidade do Achado"},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': "#2c3e50"},
                 'steps' : [
                     {'range': [0, 33], 'color': "lightgreen"},
                     {'range': [33, 66], 'color': "yellow"},
                     {'range': [66, 100], 'color': "red"}],
                }
    ))
    gauge_fig.update_layout(height=250, margin=dict(t=40, l=40, r=40, b=10))

    # --- Card Layout ---
    return dbc.CardBody([
        html.H4(f"Análise Detalhada: {finding['impression']}", className='text-xl font-bold mb-3'),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=gauge_fig), md=4),
            dbc.Col(html.Blockquote(finding['report_description'], className='text-slate-700 border-l-4 ps-4 my-3'), md=8),
        ]),
        html.Hr(),
        html.H5("Análises Visuais Correlacionadas", className="font-bold mt-4"),
        dbc.Tabs([
            dbc.Tab(dcc.Graph(figure=sunburst_fig), label="Painel Bioquímico (Sunburst)"),
            dbc.Tab(dcc.Graph(figure=treemap_fig), label="Painel Hematológico (Treemap)"),
        ])
    ])

# --- Step 5: Run the Local Server ---
if __name__ == '__main__':
    app.run(debug=True)