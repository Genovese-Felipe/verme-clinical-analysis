# scripts/viz.py (v2.0 - Expert Insight Dashboard)

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json

# --- Step 1: Load the Enriched Data ---
# This version reads all our enriched data files.
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

# --- Step 2: Initialize the Dash App with Bootstrap Theme & Font Awesome Icons ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
server = app.server

# --- Step 3: Reusable Components Factory (Best Practice) ---
def create_kpi_card(title, content, color, icon):
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title", style={'color': color}),
            html.Div([
                html.I(className=f"{icon} me-2"),
                html.Span(content, className='text-lg font-semibold')
            ])
        ]),
        className="shadow-sm h-100"
    )

def create_recommendation_item(recommendation, index):
    return dbc.AccordionItem(
        title=f"💡 Recomendação #{index + 1}: {recommendation['recommendation']}",
        children=[
            html.P(recommendation['justification_pt']),
            dbc.Badge(f"Prioridade: {recommendation['priority']}", color="info")
        ]
    )

# --- Step 4: Define the Application Layout ---
app.layout = dbc.Container(fluid=True, className="bg-light p-0", children=[
    # Header
    dbc.Row(
        dbc.Col(
            html.Div(
                className='p-5 text-white text-center shadow-lg',
                style={'background': 'linear-gradient(135deg, #1e3a8a, #3b82f6)'},
                children=[
                    html.H1('Dashboard de Análise Clínica Integrada'),
                    html.H2(f"Paciente: {insights_data['patient_id']}", className='text-xl mt-2 font-light')
                ]
            )
        )
    ),
    
    # Body
    dbc.Row(className="p-4", children=[
        # Left Column: Insights & Recommendations
        dbc.Col(lg=4, children=[
            html.H3("Sumário e Hipóteses", className="text-2xl font-bold mb-3"),
            create_kpi_card("Hipótese Principal", insights_data['primary_hypothesis']['name_pt'], "#c81e1e", "fas fa-lightbulb"),
            html.Br(),
            create_kpi_card("Risco Secundário", insights_data['secondary_concerns'][0]['name_pt'], "#d97706", "fas fa-exclamation-triangle"),
            html.Br(),
            html.H3("Recomendações Avançadas", className="text-2xl font-bold mb-3 mt-4"),
            dbc.Accordion(
                [create_recommendation_item(rec, i) for i, rec in enumerate(insights_data['advanced_recommendations'])],
                start_collapsed=True,
                always_open=False,
                flush=True
            )
        ]),
        
        # Right Column: Data Exploration
        dbc.Col(lg=8, children=[
            html.H3("Explorador Interativo de Achados", className="text-2xl font-bold mb-3"),
            dbc.Card(dbc.CardBody([
                dbc.Tabs(id="organ-tabs", active_tab="tab-bladder", children=[
                    dbc.Tab(label="Bexiga", tab_id="tab-bladder"),
                    dbc.Tab(label="Rins", tab_id="tab-kidneys"),
                    dbc.Tab(label="Hérnia", tab_id="tab-hernia"),
                ]),
                html.Div(id='organ-details-output', className="mt-4")
            ])),
            html.Br(),
            html.H3("Painéis Laboratoriais Detalhados", className="text-2xl font-bold mb-3"),
            dbc.Card(dbc.CardBody(
                dbc.Tabs([
                    dbc.Tab(dcc.Graph(id='biochemistry-chart'), label="Bioquímica"),
                    dbc.Tab(dcc.Graph(id='hematology-chart'), label="Hemograma"),
                ])
            ))
        ])
    ])
])

# --- Step 5: Callbacks for Interactivity ---

@app.callback(
    Output('organ-details-output', 'children'),
    Input('organ-tabs', 'active_tab')
)
def display_organ_details(active_tab):
    organ_map = {"tab-bladder": "Urinary Bladder", "tab-kidneys": "Kidneys", "tab-hernia": "Abdominal Wall"}
    selected_organ = organ_map.get(active_tab)
    
    finding = next((item for item in ultrasound_data['pathological_findings'] if item["organ"] == selected_organ), None)
    if not finding:
        return html.P("Selecione um achado para ver os detalhes.")

    correlation_elements = [
        dbc.Toast(
            [html.P(f"Insight: {corr['insight']}", className="mb-0")],
            header=f"Correlação com {corr['parameter']} (Status: {corr['status']})",
            icon="primary" if corr['status'] == 'Normal' else ("danger" if corr['status'] == 'High' else "warning"),
            className="mb-2"
        )
        for corr in finding.get('correlated_lab_findings', [])
    ]

    return html.Div([
        html.H4(finding['impression'], className='text-xl font-bold'),
        html.Blockquote(finding['report_description'], className='text-slate-700 border-l-4 ps-4 my-3'),
        html.Hr(className="my-3"),
        html.H5('Correlações Clínicas com Exames Laboratoriais:', className='font-bold'),
        html.Div(correlation_elements) if correlation_elements else html.P('Nenhuma correlação direta notada.', className='text-sm italic')
    ])

@app.callback(
    Output('biochemistry-chart', 'figure'),
    Input('organ-tabs', 'active_tab') # Dummy trigger
)
def update_biochemistry_chart(_):
    fig = px.bar(df_biochemistry, x='parameter', y='value', color='status',
                 color_discrete_map={'Normal': '#198754', 'High': '#dc3545', 'Low': '#ffc107'},
                 labels={'value': 'Valor', 'parameter': 'Parâmetro'}, text='value')
    fig.update_layout(title_text='<b>Painel Bioquímico</b>', yaxis_title=None, xaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>%{x}</b>",
            "Resultado: %{y} %{customdata[0]}",
            "Referência: %{customdata[1]}",
            "Significado: %{customdata[2]}<extra></extra>"
        ]),
        customdata=df_biochemistry[['unit', 'reference_range', 'significance_pt']].values
    )
    return fig

@app.callback(
    Output('hematology-chart', 'figure'),
    Input('organ-tabs', 'active_tab') # Dummy trigger
)
def update_hematology_chart(_):
    fig = px.bar(df_hematology, x='parameter', y='value', color='status',
                 color_discrete_map={'Normal': '#198754', 'High': '#dc3545', 'Low': '#ffc107'}, text='value')
    fig.update_layout(title_text='<b>Painel Hematológico</b>', yaxis_title=None, xaxis_title=None, xaxis_tickangle=-45, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Resultado: %{y}<br>Status: %{customdata[0]}<extra></extra>",
        customdata=df_hematology[['status']].values
    )
    return fig

# --- Step 6: Run the Local Server (Corrected) ---
if __name__ == '__main__':
    app.run(debug=True) # <-- CORREÇÃO APLICADA AQUI