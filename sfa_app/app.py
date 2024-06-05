from shiny.express import ui, render, input, expressify
from shiny import reactive

from shared import data_dir, data_files, md_render, mds
from reactive import example_datafile_data 

from sfa_math import ols

import pandas as pd

# Sidebar options
OPTIONS = {
            "Example files": {f"example_datafile:{element.name}": element.name for i, element in enumerate(data_files)},
            "Personalized data": {"w":"Write my own data", "r":"Create random data", "u":"Upload file"}
        }



@reactive.effect
@reactive.event(input.datafile_selection, input.salvador_Participation, input.salvador_fullten, input.salvador_ageold60, input.salvador_nooutinc, input.salvador_footaccess, input.salvador_caraccess, input.salvador_dum01, input.salvador_dum02, input.salvador_dum03, input.salvador_dum04)
def _():
    if "example_datafile" not in (selection := input.datafile_selection.get()):
        return
    
    if "elsalvador" in selection:
        file = [f for f in data_files if f.name == "elsalvador.csv"][0]
        data = pd.read_csv(file)
        filters = ["Participation", "fullten", "ageold60", "nooutinc", "footaccess", "caraccess", "dum01", "dum02", "dum03", "dum04"]
        for filter in filters:
            if input["salvador_" + filter].get() == '0':
                data = data[data[filter] == 0]
            elif input["salvador_" + filter].get() == '1':
                data = data[data[filter] == 1]
        example_datafile_data.set(data)




ui.HTML(r"""<script type="text/javascript" async
        src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>""")
ui.h1("Stochastic Frontier Analaysis")

with ui.sidebar(bg="#F5F5F5"):
    ui.input_select("datafile_selection", "Choose the data", OPTIONS)
    with ui.panel_conditional("input.datafile_selection.includes('example_datafile')"):
        ui.input_select("ineff_distr", "Distribution of the inefficiency term", ["Half-normal", "Exponential", "Truncated normal", "Gamma"])
        with ui.panel_conditional("input.datafile_selection === 'example_datafile:elsalvador.csv'"):
            with ui.card():
                "Data filters"
                ui.input_select("salvador_Participation", "Participation", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_fullten", "fullten", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_ageold60", "ageold60", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_nooutinc", "nooutinc", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_footaccess", "footaccess", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_caraccess", "caraccess", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_dum01", "dum01", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_dum02", "dum02", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_dum03", "dum03", [0,1,"Any"], selected="Any")
                ui.input_select("salvador_dum04", "dum04", [0,1,"Any"], selected="Any")

# MAIN PAGE

with ui.panel_conditional("!input.datafile_selection.includes('example_datafile')"):
    "Not implemented"

@reactive.calc
def sfa():
    data = example_datafile_data.get()
    result = ols(data, "loutput", ["fam_electricidad", "fam_letrinas"])
    return result.params

@expressify
def elsalvador():
    #For some reason I cannot move this to another file, it gets frozen at "input.xxx.get()"
    with ui.panel_conditional("input.datafile_selection === 'example_datafile:elsalvador.csv'"):
        with ui.navset_pill(id="tab"):  
            with ui.nav_panel("Dataset explanation"):
                ui.markdown(mds["elsalvador.md"])

            with ui.nav_panel("Data"):
                with ui.card(full_screen=True):
                    ui.card_header("Data")
                    
                    @render.data_frame
                    def table():
                        file = [f for f in data_files if f.name == "elsalvador.csv"][0]
                        data = pd.read_csv(file)
                        filters = ["Participation", "fullten", "ageold60", "nooutinc", "footaccess", "caraccess", "dum01", "dum02", "dum03", "dum04"]
                        for filter in filters:
                            if input["salvador_" + filter].get() == '0':
                                data = data[data[filter] == 0]
                            elif input["salvador_" + filter].get() == '1':
                                data = data[data[filter] == 1]
                        example_datafile_data.set(data)
                        return render.DataGrid(data)

            with ui.nav_panel("Result"):
                with ui.card():
                    @render.text
                    def f():
                        return sfa()

elsalvador()