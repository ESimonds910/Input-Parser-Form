import pandas as pd
import numpy as np
import ipywidgets as ipw
from IPython.display import display
from ipywidgets import Layout
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

STYLE = {"description_width": "initial"}


class DataAnalysis:
    def __init__(self, dict):
        self.parser_data_dict = dict
        self.full_calcs_df = pd.DataFrame()
        self.full_display_df = pd.DataFrame()
        self.full_calcs_rep_df = pd.DataFrame()
        self.full_display_rep_df = pd.DataFrame()

        self.proj_list = [proj for proj in self.parser_data_dict.keys()]
        self.proj_choice = ipw.Dropdown(options=self.proj_list)
        self.show_data_vis = ipw.Button(description="Show Visuals", button_style="info")
        self.data_vis = ipw.Output()
        self.chart_out = ipw.Output(layout={'border': '1px solid black'})
        self.vbox_data_vis = ipw.VBox([self.proj_choice, self.show_data_vis])
        self.choose_proj()
        self.show_data_vis.on_click(self.build_display)


    # def import_data(self):
    #     with open("parser_data.json") as parserfile:
    #         self.parser_data_dict = json.load(parserfile)

    def choose_proj(self):
        display(self.vbox_data_vis, self.chart_out)

    def build_display(self, event):
        # proj chosen from dropdown
        proj_name = self.proj_choice.value
        file_path = self.parser_data_dict[proj_name]["out_path"]
        calcs_df = pd.read_excel(file_path, index_col=0, sheet_name="Calculations")
        display_df = pd.read_excel(file_path, index_col=0, sheet_name="Display_Ready")
        calcs_reps_df = pd.read_excel(file_path, index_col=0, sheet_name="Rep_Calculations")
        display_reps_df = pd.read_excel(file_path, index_col=0, sheet_name="Rep_Display_Ready")

        self.full_calcs_df = pd.concat([self.full_calcs_df, calcs_df])
        self.full_display_df = pd.concat([self.full_display_df, display_df])

        self.full_calcs_rep_df = pd.concat([self.full_calcs_rep_df, calcs_reps_df])
        self.full_display_rep_df = pd.concat([self.full_display_rep_df, display_reps_df])

        stacked_calcs_df = pd.concat([self.full_calcs_df, self.full_calcs_rep_df])
        stacked_display_df = pd.concat([self.full_display_df, self.full_display_rep_df])

        stacked_display_df.dropna(subset=["Sample_type"], how='any', inplace=True)

        with self.chart_out:
            display(ipw.HTML("This Code"))
            column_name = ipw.Dropdown(
                options=list(stacked_display_df.columns),
                description="Choose column to indicate color",
                style=STYLE,
                value='Plate'
            )

            def create_traces(column_name):
                try:
                    rep_lines = px.line(stacked_display_df, x="Volumes", y="Alpha", facet_col="Col", facet_row="Row",
                                        color=column_name, line_group="Plate", log_x=True,
                                        height=800, width=1000, title=proj_name)
                    rep_lines.update_xaxes(tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                    rep_lines.update_yaxes(tickangle=45, tickfont=dict(size=8), title_font=dict(size=10))
                    rep_lines.update_traces(line=dict(width=0.8))

                    rep_lines.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                    rep_lines.show()
                except KeyError:
                    print("\nChoose a different column! This one doesn't work.")
                except ValueError:
                    print("\nChoose a different columns! These values don't look right.")


            trace_plot = ipw.interactive(create_traces, column_name=column_name)
            display(trace_plot)

