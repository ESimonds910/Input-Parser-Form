import ipywidgets as ipw
from IPython.display import display
from ipywidgets import interact
import plotly.express as px
from string import ascii_uppercase as upstr
import json

STYLE = {'description_width': 'initial'}


class DisplayImage:
    img_path = open('AbSciImg.jfif', 'rb')
    img = img_path.read()
    display(ipw.Image(value=img, format='jfif', height='200px', width='200px'))


class InputForm:

    def __init__(self):
        self.proj_dict = {}
        self.std_dict_all = {}
        with open('parser_data.json', 'w') as parser_file:
            json.dump(self.proj_dict, parser_file, indent=4)
        self.proj_name = ipw.Text()
        self.point_choice = ipw.Dropdown(options=[('Four', 4), ('Eight', 8)])
        self.plates = ipw.Text()
        self.d_vols = ipw.Text()
        self.check = ipw.Checkbox(indent=False)

        self.loc = ipw.Dropdown(options=["Column", "Row"])
        self.well_loc = ipw.Text()
        self.std_conc = ipw.Text()
        self.add_stc_button = ipw.Button(description='Add Standard', button_style='info')
        self.stc_out = ipw.Output(layout={'border': '1px solid black'})
        # self.display_standard()
        self.add_stc_button.on_click(self.add_standard)

        self.button_update = ipw.Button(
            description='Add Project',
            button_style='info'
        )
        self.output = ipw.Output(layout={'border': '1px solid black'})
        self.button_update.on_click(self.on_button_click)
        self.vbox_result = ipw.VBox([self.button_update, self.output])

        self.display_inputs()

    def display_inputs(self):
        display(
            ipw.Label("Enter project name:"),
            self.proj_name,
            ipw.Label("Enter plate ids for project, e.g., P1-1, P1-2, P2:"),
            self.plates,
            ipw.Label("Choose four or eight point dilution scheme:"),
            self.point_choice,
            ipw.Label("Enter dilution volumes:"),
            self.d_vols,
            ipw.Label("Check box to indicate if OD file is required:"),
            self.check,

            ipw.Label(f"{'-' * 100}"),
            ipw.HTML(value="<h3><b>*** Add Standard information here ***</b></h3>"),
            ipw.Label("Choose if standard curve was place in row or column:"),
            self.loc,
            ipw.Label("Enter the location of first well used, e.g., A11, or H01:"),
            self.well_loc,
            ipw.Label("Enter the standard curve concentrations, match first concentration with well"),
            self.std_conc,
            self.add_stc_button,
            self.stc_out,
            ipw.HTML(value="<h5><b>Check inputs for accuracy and add."
                           " Enter new details for multiple projects or run parser.</b></h5>"),
            self.vbox_result
        )

    def on_button_click(self, event):
        self.output.clear_output()

        with open('parser_data.json', 'r') as parser_file:
            proj_dict_all = json.load(parser_file)

        proj = self.proj_name.value
        point = self.point_choice.value
        if ',' in self.plates.value:
            plate_ids = list(map(str.strip, self.plates.value.split(',')))
        else:
            plate_ids = list(map(str.strip, self.plates.value.split()))

        if ',' in self.d_vols.value:
            d_volumes = [float(x) for x in self.d_vols.value.split(',')]
        else:
            d_volumes = [float(x) for x in self.d_vols.value.split()]

        self.proj_dict = {proj: {
            'plates': plate_ids,
            'points': point,
            'volumes': d_volumes,
            'od_file': self.check.value,
            'std_conc': self.std_dict_all
        }
        }
        proj_dict_all.update(self.proj_dict)

        with open('parser_data.json', 'w') as parser_file:
            json.dump(proj_dict_all, parser_file, indent=4)

        self.std_dict_all = {}

        with self.output:
            print('***  Project Updated  ***')
            for proj, inner in proj_dict_all.items():
                print(f'\nProject name entered: {proj}\n')
                print(f"Plate Ids: {', '.join(inner['plates'])}\n")
                print(f"Point Scheme: {inner['points']}\n")
                print(f"Dilution Volumes: {self.d_vols.value}\n")
                print(f"Add OD data: {inner['od_file']}\n")
                for key, value in inner['std_conc'].items():
                    print(f"Well ID: {key}, Standard Concentration: {value}")
        #             for key, value in inner.items():
        #                 print(f'{key} entered: {value}\n')
        return self.std_dict_all

    def add_standard(self, event):
        self.stc_out.clear_output()
        if ',' in self.std_conc.value:
            std_conc_list = [float(x) for x in self.std_conc.value.split(',')]
        else:
            std_conc_list = [float(x) for x in self.std_conc.value.split()]

        std_conc_list_len = len(std_conc_list)
        if self.loc.value == 'Column':
            col_letter = self.well_loc.value[:1]
            letter_idx = upstr.index(col_letter)
            col_num = self.well_loc.value[1:]
            std_ids = [f"{upstr[letter]}{str(col_num).zfill(2)}" for letter in range(letter_idx, std_conc_list_len)]
            std_dict = (dict(zip(std_ids, std_conc_list)))

        elif self.loc.value == 'Row':
            row_letter = self.well_loc.value[:1]
            row_num = int(self.well_loc.value[1:])
            std_ids = [f"{row_letter}{str(num).zfill(2)}" for num in range(row_num, row_num + std_conc_list_len)]
            std_dict = dict(zip(std_ids, std_conc_list))
        try:
            self.std_dict_all.update(std_dict)
        except AttributeError:
            std_dict_all = {}
            std_dict_all.update(std_dict)
        else:
            with self.stc_out:
                print("*** Standard Updated ***\n")
                for key, value in self.std_dict_all.items():
                    print(f'Well ID: {key}, Concentration: {value}')
                print("\nTo add replicate, change well id, or 'column/row' to indicate new standard curve position.\n")
            return self.std_dict_all


# class StandardForm(InputForm):
#
#     def __init__(self):
#         super().__init__()
#         self.loc = ipw.Dropdown(options=["Column", "Row"])
#         self.well_loc = ipw.Text()
#         self.std_conc = ipw.Text()
#         self.add_stc_button = ipw.Button(description='Add Standard', button_style='info')
#         self.stc_out = ipw.Output()
#         self.display_standard()
#         self.add_stc_button.on_click(self.add_standard)
#
#     def display_standard(self):
#         display(
#             ipw.Label("Add Standard information here:"),
#             ipw.Label("Choose if standard curve was place in row or column:"),
#             self.loc,
#             ipw.Label("Enter the location of first well used, e.g., A11, or H01:"),
#             self.well_loc,
#             ipw.Label("Enter the standard curve concentrations, match first concentration with well"),
#             self.std_conc,
#             self.add_stc_button,
#             self.stc_out
#         )
#
#     def add_standard(self, event):
#         self.stc_out.clear_output()
#
#         std_conc_list = [float(x) for x in self.std_conc.value.split(',')]
#         std_conc_list_len = len(std_conc_list)
#         if self.loc.value == 'Column':
#             col_letter = self.well_loc.value[:1]
#             letter_idx = upstr.index(col_letter)
#             col_num = self.well_loc.value[1:]
#             std_ids = [f"{upstr[letter]}{str(col_num).zfill(2)}" for letter in range(letter_idx, std_conc_list_len)]
#             std_dict = (dict(zip(std_ids, std_conc_list)))
#
#         elif self.loc.value == 'Row':
#             row_letter = self.well_loc.value[:1]
#             row_num = int(self.well_loc.value[1:])
#             std_ids = [f"{row_letter}{str(num).zfill(2)}" for num in range(row_num, row_num + std_conc_list_len)]
#             std_dict = dict(zip(std_ids, std_conc_list))
#         try:
#             self.std_dict_all.update(std_dict)
#         except AttributeError:
#             std_dict_all = {}
#             std_dict_all.update(std_dict)
#         else:
#             with self.stc_out:
#                 for key, value in self.std_dict_all.items():
#                     print(f'Well ID: {key}, Concentration: {value}')
#                 print("\nTo add replicate, change well id, or 'column/row' to indicate new standard curve position.\n")
#             return self.std_dict_all

