import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from scipy import stats
import ipywidgets as ipw
from IPython import display


class BuildDashboard:
    def __init__(self, proj_dict):
        self.app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

        self.parser_data_dict = proj_dict
        # self.file_path = r"L:\High Throughput Screening\Strain Screening Funnel (SSF)\SSF_Experiments\SSF00655 DSS Sheepdog004 Discrete host screening\Assays\HiPrBind\Processed\SSF00655_output.xlsx"

        # working_proj = self.grab_project()

        self.all_stacked_df = pd.DataFrame()
        for proj, inner in self.parser_data_dict.items():
            self.file_path = inner["out_path"]
            self.full_display_df = pd.DataFrame()
            self.full_display_rep_df = pd.DataFrame()
            self.display_df = pd.read_excel(self.file_path, index_col=0, sheet_name="Display_Ready")
            self.display_reps_df = pd.read_excel(self.file_path, index_col=0, sheet_name="Rep_Display_Ready")
            self.full_display_df = pd.concat([self.full_display_df, self.display_df])
            self.full_display_rep_df = pd.concat([self.full_display_rep_df, self.display_reps_df])
            self.stacked_display_df = pd.concat([self.full_display_df, self.full_display_rep_df])

            self.stacked_display_df.dropna(subset=["Sample_type"], how='any', inplace=True)
            self.all_stacked_df = pd.concat([self.stacked_display_df, self.all_stacked_df])
        # try:
        #     self.proj_name = self.stacked_display_df['SSF_exp'].unique()[0]
        #
        # except KeyError:
        #     print("No ID")

        self.build_display()

    # Grab project
    # def grab_project(self):
    #     proj_options = [{'label': proj, 'value': proj} for proj in self.parser_data_dict.keys()]
    #     self.app.layout = html.Div([
    #         html.H1(id='proj-header'),
    #         dcc.Dropdown(id='proj-picker', options=proj_options, value=proj_options[0])
    #     ])
    #
    #     @self.app.callback(Output(component_id='proj-header', component_property='children'),
    #                        [Input(component_id='proj-picker', component_property='value')])
    #     def picked_proj(selected_proj):
    #         self.working_proj = self.parser_data_dict[selected_proj]
    #         return self.working_proj

    def build_display(self):
        proj_options = [{'label': proj, 'value': proj} for proj in self.parser_data_dict]
        plate_options = [{'label': plate, 'value': plate} for plate in self.stacked_display_df["Plate"].unique()]
        column_options = [{'label': column, 'value': column} for column in self.stacked_display_df.columns]
        corr_plate_options = [{'label': corr_plate,
                               'value': corr_plate} for corr_plate in self.stacked_display_df["Plate"].apply(lambda x: x.split('-')[0]).unique()]
        # print(stacked_display_df["Plate"].unique()[0])
        self.app.layout = html.Div([
            dcc.Store(id='proj-output'),
            dcc.Dropdown(id='proj-picker', options=proj_options, value=proj_options[0]),

            html.Div([
                dcc.Markdown(id='graph-1-heading', children=f"# Data Analysis for Projects")],
                style={'color': 'black', 'margin':'50px 0px 50px 20px'}),
            html.Hr(),

            html.Div([
                dcc.Dropdown(id='plate-picker',
                             options=plate_options,
                             value=self.stacked_display_df["Plate"].unique()[0],
                             style={'margin': '0px 20px', 'width':'50%'}),
                dcc.Graph(id='graph')
            ]),

            html.Hr(),

            html.Div([
                dcc.Dropdown(id='column-picker',
                             options=column_options,
                             value="Plate",
                             style={'margin': '0px 20px', 'width':'50%'}),
                dcc.Graph(id='graph2')
            ]),

            html.Hr(),

            html.Div([
                dcc.Dropdown(id='rep-picker',
                             options=corr_plate_options,
                             value="P1",
                             style={'margin': '0px 20px', 'width':'50%'}),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Div(dcc.Graph(id='graph3'),
                                     className='graph-corr-box col-lg-6')
                        ]),
                        dbc.Col([
                            html.Div(html.P(id='corr-output',
                                            className='graph-corr-box col-lg-6',
                                            style={'margin': '300px auto 100px 0px',
                                                   'textAlign':'left'}))
                        ])
                    ])
                ], style={'width':'100%'})

            ])

        ], style={'marginLeft': '20px'})

        @self.app.callback(Output(component_id='proj-output', component_property='data'),
                           [Input(component_id='proj-picker', component_property='value')])
        def picked_proj(selected_proj):
            filtered_proj_df = self.all_stacked_df[self.all_stacked_df["SSF_exp"]]
            return filtered_proj_df

        @self.app.callback(Output(component_id='graph', component_property='figure'),
                           [Input(component_id='proj-output', component_property='data'),
                            Input(component_id='plate-picker', component_property='value')])
        def update_figure(data, selected_plate):
            # by_plate_df = self.stacked_display_df[self.stacked_display_df["Plate"] == selected_plate]
            by_plate_df = data[data["Plate"] == selected_plate]
            proj_name = data["SSF_exp"].unique()[0]
            # traces = []
            # for well in by_plate_df["Well_Id"].unique():
            #     sample_trace_df = by_plate_df[by_plate_df["Well_Id"] == well]
            #     traces.append(go.Scatter(x=sample_trace_df["Volumes"], y=sample_trace_df["Alpha"], mode='markers+lines', name=well))
            traces = px.line(x=by_plate_df["Volumes"],
                    y=by_plate_df["Alpha"],
                    color=by_plate_df['Sample_type'],
                    line_group=by_plate_df["Well_Id"],
                    log_x=True,
                    height=800, width=800, title=f"{proj_name}: {selected_plate}")
            traces.update_xaxes(title='Log Volumes: log(ul)',
                                rangemode='tozero',
                                zeroline=True,
                                zerolinecolor='grey',
                                showline=True,
                                linewidth=1,
                                linecolor='grey')
            traces.update_yaxes(title='Alpha',
                                rangemode='tozero',
                                zeroline=True,
                                zerolinecolor='grey',
                                showline=True,
                                linewidth=1,
                                linecolor='grey')
            traces.update_traces(mode="markers+lines")
            traces.update_layout(legend_title="Sample Type")
            fig = go.Figure(traces)

            return fig

        @self.app.callback(Output(component_id='graph2', component_property='figure'),
                     [Input(component_id='proj-picker', component_property='data'),
                      Input(component_id='column-picker', component_property='value')])
        def update_traces(data, selected_column):
            try:
                proj_name = data["SSF_exp"].unique()[0]
                traces = px.line(data,
                                 x="Volumes",
                                 y="Alpha",
                                 facet_col="Col",
                                 facet_row="Row",
                                 color=selected_column,
                                 line_group="Plate",
                                 log_x=True,
                                 height=800, width=1200,
                                 title=proj_name)
            except ValueError:
                fig = go.Figure()
                return fig
            except AttributeError:
                fig = go.Figure()
                return fig
            else:
                traces.update_xaxes(tickangle=45,
                                    tickfont=dict(size=8),
                                    title_font=dict(size=10),
                                    showline=True,
                                    linecolor='grey')
                traces.update_yaxes(tickangle=45,
                                    tickfont=dict(size=8),
                                    title_font=dict(size=10),
                                    showline=True,
                                    linecolor='grey')
                traces.update_traces(line=dict(width=0.8))
                traces.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                fig = go.Figure(traces)
                return fig

        @self.app.callback([Output(component_id='graph3', component_property='figure'),
                            Output(component_id='corr-output', component_property='children')],
                           [Input(component_id='proj-picker', component_property='data'),
                            Input(component_id='rep-picker', component_property='value')])
        def corr_analysis(data, corr_plate):
            corr_plate_df = data[data["Plate"].str.startswith(corr_plate)]
            sample_type = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)][
                "Sample_type"].values
            well_id = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)]["Well_Id"].values
            main_alpha = corr_plate_df[corr_plate_df["Plate"].str.contains("-1", case=False)]["Alpha"].values
            rep_alpha = corr_plate_df[corr_plate_df["Plate"].str.contains("-2", case=False)]["Alpha"].values
            proj_name = data["SSF_exp"].unique()[0]
            try:
                corr_plot = px.scatter(x=main_alpha,
                                       y=rep_alpha,
                                       color=sample_type,
                                       width=800,
                                       height=800,
                                       title=f"{proj_name}: {corr_plate}")
            except ValueError:
                fig = go.Figure()
                corr_value = "No correlation"
                return fig, corr_value

            else:
                corr_plot.update_xaxes(title='Main',
                                       tickangle=45,
                                       tickfont=dict(size=8),
                                       showline=True,
                                       linecolor='grey')
                corr_plot.update_yaxes(title='Replicate',
                                       tickangle=45,
                                       tickfont=dict(size=8),
                                       showline=True,
                                       linecolor='grey')
                corr_plot.update_layout(legend_title="Sample Type")
                fig = go.Figure(corr_plot)

                pcorr, pvalue = stats.pearsonr(main_alpha, rep_alpha)
                corr_value = f"Correlation: {str(round(pcorr, 4))}  |  p-value: {str(round(pvalue, 4))}"
                return fig, corr_value

        self.app.run_server(
            debug=True,
            use_reloader=False
        )


if __name__ == "__main__":
    BuildDashboard()