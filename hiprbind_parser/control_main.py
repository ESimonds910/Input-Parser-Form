import pandas as pd
import json
import ipywidgets as ipw
import numpy as np
from time import time
from tkinter import Tk, messagebox
from IPython.display import display
from tkinter.filedialog import askopenfilename, askdirectory
from string import ascii_uppercase as upstr
import hiprbind_parser.file_split as fs
from hiprbind_parser.import_csv import FileFinder
import hiprbind_parser.data_formatter as formatter
import hiprbind_parser.enspire_od_join as enspire_od_join
import hiprbind_parser.pt_calculations as pt_calculations
from hiprbind_parser.import_od import import_od

# TODO just create separate inputs module


class RunParser:
    def __init__(self):
        self.window = Tk()
        self.window.withdraw()
        self.proj_data_dict = {}
        self.run_parser_btn = ipw.Button(description='Run parser', button_style='info')
        self.run_parser_btn.on_click(self.run_main)
        display(self.run_parser_btn)
        self.window.destroy()

    def concat_projs(self, df):
        all_projs_df = pd.DataFrame()
        pass

    def run_main(self, event):
        proj_concat = False
        try:
            with open(r"C:\Users\esimonds\GitHub\Input-Parser-Form\parser_data.json", "r") as parser_file:
                self.proj_data_dict = json.load(parser_file)
        except FileNotFoundError:
            messagebox.showinfo(title="Warning!", message="There's no file, did you complete the parser form?")

        file_finder = FileFinder()

        self.proj_data_dict = fs.split_projects(self.proj_data_dict)

        for proj, inner_dict in self.proj_data_dict.items():
            project_title = proj
            if "-" in proj:
                inner_dict["proj_name"] = proj.split("-")[0]
                inner_dict["ab_name"] = proj.split("-")[-1]
            else:
                inner_dict["ab_name"] = ""
                inner_dict["proj_name"] = proj

            proj_data = self.proj_data_dict[proj]

            source_df = file_finder.data_finder(proj_data)

            df_list = formatter.data_format(source_df, proj_data)

            if proj_data["od_file"]:
                raw_od = import_od(proj_data)
                joined_df_list = enspire_od_join.join_dfs(df_list, raw_od, proj_data)
                main_join_dfs = joined_df_list[:2]
                final_display_df = joined_df_list[2]
                final_display_rep_df = joined_df_list[3]
                completed_main_dfs = pt_calculations.make_calculations(main_join_dfs, proj_data)
            else:
                main_dfs = df_list[:2]
                final_display_df = df_list[2]
                final_display_rep_df = df_list[3]
                completed_main_dfs = pt_calculations.make_calculations(main_dfs, proj_data)

            final_main_df = completed_main_dfs[0]
            final_main_rep_df = completed_main_dfs[1]

            window = Tk()
            window.withdraw()
            output_path = askdirectory(
                title="Choose folder to place output file for " + project_title,
                initialdir='L:/Molecular Sciences/Small Scale Runs'
            )
            window.destroy()
            with pd.ExcelWriter(f"{output_path}/{project_title}_output.xlsx") as writer:
                final_main_df.to_excel(writer, sheet_name="Calculations")
                final_display_df.to_excel(writer, sheet_name="Display_Ready")
                final_main_rep_df.to_excel(writer, sheet_name="Rep_Calculations")
                final_display_rep_df.to_excel(writer, sheet_name="Rep_Display_Ready")
            messagebox.showinfo(title="Congratulations!", message=f"Project {project_title} has been output.")

        # Also return these four dataframes into list?
        # clean_df, main_df, clean_rep_df, main_rep_df = test_formatter.data_format(source_df, proj_data)
        # df_list = [clean_df, main_df, clean_rep_df, main_rep_df]
        # dfs_return = join_dfs(df_list, raw_od, proj_data)
        #
        # clean_join_df = dfs_return[0]
        # main_join_df = dfs_return[1]
        # clean_rep_join_df = dfs_return[2]
        # main_rep_join_df = dfs_return[3]
        #
        # complete_df = eight_pt_calculations.make_calculations(main_join_df, proj_data)
        # complete_rep_df = eight_pt_calculations.make_calculations(main_rep_join_df, proj_data)
        #


if __name__ == "__main__":
    start_time = time()
    window = Tk()
    window.withdraw()
    RunParser().run_main()
    window.destroy()
    end_time = time()
    split = round(end_time - start_time, 2)
    print(f"Program runtime: {split}s")
