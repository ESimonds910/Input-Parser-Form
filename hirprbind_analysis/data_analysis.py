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


class DataAnalysis:
    def __init__(self, dict):
        self.parser_data_dict = dict
        self.proj_list = [proj for proj in self.parser_data_dict.keys()]
        self.proj_choice = ipw.Dropdown(options=self.proj_list)
        self.show_data_vis = ipw.Button(description="Show Visuals", button_style="info")
        self.data_vis = ipw.Output()
        self.vbox_data_vis = ipw.VBox([self.proj_choice, self.show_data_vis])
        self.choose_proj()
        self.full_calcs_df = pd.DataFrame()
        self.full_display_df = pd.DataFrame()
        self.full_calcs_rep_df = pd.DataFrame()
        self.full_display_rep_df = pd.DataFrame()

    # def import_data(self):
    #     with open("parser_data.json") as parserfile:
    #         self.parser_data_dict = json.load(parserfile)

    def choose_proj(self):
        display(self.vbox_data_vis)

    def build_display(self):
        # proj chosen from dropdown
        file_path = self.parser_data_dict[self.proj]["out_path"]
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

