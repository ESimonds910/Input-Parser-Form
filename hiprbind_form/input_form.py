import ipywidgets as ipw
from IPython.display import display
from ipywidgets import Layout
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
        self.proj_name = ipw.Text(placeholder="e.g. SSFXXXXX or SOMXXXXX")
        self.point_choice = ipw.Dropdown(options=[('Four', 4), ('Eight', 8)])
        self.plates = ipw.Text(placeholder="e.g. P1, P2 or P1-1, P1-2, P2")
        self.d_vols = ipw.Text(placeholder="e.g. 2, 1, 0.5, 0.25 or 2 1 0.5 0.25")
        self.check = ipw.Checkbox(indent=False)

        self.loc = ipw.Dropdown(options=["Column", "Row"])
        self.well_loc = ipw.Text(placeholder="e.g. A11 or G01")
        self.std_conc = ipw.Text(placeholder="e.g. 100, 50, 25 or 100 50 25")
        self.add_stc_button = ipw.Button(description='Add Standard', button_style='info')
        self.stc_out = ipw.Output(layout={'border': '1px solid black'})
        # self.display_standard()
        self.add_stc_button.on_click(self.add_standard)
        self.vbox_stc_result = ipw.VBox([self.add_stc_button, self.stc_out])

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
            ipw.Label("Enter plate ids for project:"),
            self.plates,
            ipw.Label("Choose four or eight point dilution scheme:"),
            self.point_choice,
            ipw.Label("Enter dilution volumes:"),
            self.d_vols,
            ipw.Label("Check box to indicate if OD file is required:"),
            self.check,

            ipw.Label(f"{'-' * 100}"),
            ipw.HTML(value="<h4><b>*** Add Standard information here: enter replicates separately ***</b></h4>"),
            ipw.Label("Is the standard curve in a row or a column:"),
            self.loc,
            ipw.Label("Enter the location of first well used:"),
            self.well_loc,
            ipw.Label("Enter the standard curve concentrations- match first listed concentration with indicated well"),
            self.std_conc,
            self.vbox_stc_result,
            ipw.HTML(value="<h5><b>Check inputs for accuracy and add."
                           " Enter new details for multiple projects or run parser.</b></h5>"),
            self.vbox_result
        )

    def on_button_click(self, event):
        self.output.clear_output()
        all_valid = True
        with open('parser_data.json', 'r') as parser_file:
            proj_dict_all = json.load(parser_file)

        proj = self.proj_name.value
        point = self.point_choice.value

        if ',' in self.plates.value:
            plate_ids = list(map(str.strip, self.plates.value.split(',')))
        else:
            plate_ids = list(map(str.strip, self.plates.value.split()))

        for plate in plate_ids:
            if plate[:1].upper() == "P":
                if plate[-1] == '-':
                    fix_plate = "Add replicate number."
                elif len(plate) > 3:
                    if "-" in plate:
                        fix_plate = "No issues"
                    else:
                        fix_plate = "Specify replicate plate with '-'," \
                                    " e.g. P1 for non-replicate, or P1-1, P1-2 for replicates."
                        all_valid = False
                        break
                else:
                    fix_plate = 'No issues'
            else:
                fix_plate = "Please write in following format: P1, P2 for plates, or P1-1, P1-2 for replicate plates."
                all_valid = False
                break

        if ',' in self.d_vols.value:
            dvs = self.d_vols.value.split(',')
        else:
            dvs = self.d_vols.value.split()

        try:
            d_volumes = [float(x) for x in dvs]
        except ValueError:
            fix_vols = "Please use a valid number for dilution volumes"
            all_valid = False
        else:
            if len(d_volumes) != self.point_choice.value:
                fix_vols = "Please use the same number of volumes as points indicated - 4 or 8 points."
                all_valid = False
            else:
                fix_vols = "No issues"

        if all_valid:
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
                display(ipw.HTML("<b>*** Project Updated ***</b>"))
                # print('***  Project Updated  ***')
                for proj, inner in proj_dict_all.items():
                    display(ipw.HTML(f"<b>Project name entered:</b> {proj}"),
                            ipw.HTML(f"<b>Plate Ids:</b> {', '.join(inner['plates'])}"),
                            ipw.HTML(f"<b>Point Scheme:</b> {inner['points']}"),
                            ipw.HTML(f"<b>Dilution Volumes:</b> {self.d_vols.value}"),
                            ipw.HTML(f"<b>Add OD data:</b> {inner['od_file']}"),
                            ipw.HTML("<b>Standards:</b>"))
                    for key, value in inner['std_conc'].items():
                        labels = ipw.HTML(f"<ul><li style='line-height:1px';><b>Well ID:</b> {key}, <b>Standard Concentration:</b> {value}</li></ul>")
                        display(labels)
            #             for key, value in inner.items():
            #                 print(f'{key} entered: {value}\n')
            return self.std_dict_all
        else:
            with self.output:
                if fix_plate == "No issues":
                    display(ipw.HTML(f"<font color='green'>Plate IDs: {fix_plate}"))
                else:
                    display(ipw.HTML(f"<b><font color='red'>Plate IDs: {fix_plate}</b>"))
                if fix_vols == "No issues":
                    display(ipw.HTML(f"<font color='green'>Dilution Volumes: {fix_vols}"))
                else:
                    display(ipw.HTML(f"<b><font color='red'>Dilution Volumes: {fix_vols}</b>"))

    def add_standard(self, event):
        self.stc_out.clear_output()
        all_valid = True

        if self.well_loc.value[:1].upper() not in "ABCDEFGH":
            fix_well = f"{self.well_loc.value[:1].upper()} is invalid. Please fix."
            all_valid = False
        elif len(self.well_loc.value[1:]) != 2:
            fix_well = f"Please enter valid column number between 01 and 12."
            all_valid = False
        elif self.well_loc.value[1:] not in [f"{y}".zfill(2) for y in range(1, 13)]:
            fix_well = f"Please enter valid column number between 01 and 12. Remember, for numbers < 10, use 01 format."
            all_valid = False
        else:
            fix_well = "No issues"

        if ',' in self.std_conc.value:
            stc_list = self.std_conc.value.split(',')
        else:
            stc_list = self.std_conc.value.split()

        try:
            std_conc_list = [float(x) for x in stc_list]
            fix_conc = "No issues"
        except ValueError:
            fix_conc = "Valid number was not added. Check input values."
            all_valid = False

        if all_valid:
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
                    display(ipw.HTML("<b>*** Standard Updated ***</b>"))
                    for key, value in self.std_dict_all.items():
                        labels = ipw.HTML(
                            f"<ul><li style='line-height:1px';><b>Well ID:</b> {key}, <b>Standard Concentration:</b> {value}</li></ul>")
                        display(labels)
                    display(ipw.HTML("<b>To add replicate, change well id, or 'column/row' to indicate new standard curve position.</b>"))
                return self.std_dict_all
        else:
            with self.stc_out:
                if fix_well == "No issues":
                    display(ipw.HTML(f"<font color='green'>Well ID: {fix_well}"))
                else:
                    display(ipw.HTML(f"<b><font color='red'>Well ID: {fix_well}</b>"))
                if fix_conc == "No issues":
                    display(ipw.HTML(f"<font color='green'>Standard concentrations: {fix_conc}"))
                else:
                    display(ipw.HTML(f"<b><font color='red'>Standard concentrations: {fix_conc}</b>"))

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

