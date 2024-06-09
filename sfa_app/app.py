from shiny.express import ui, render, input, expressify, output
from shiny import reactive

from shared import data_dir, data_files, md_render, mds
from reactive import example_datafile_data 

from sfa_math import ols, cols_deterministic, compute_frontier, estimate_inefficiency, estimate_technical_efficiency
from dataframes import HalfNormal

import pandas as pd
import numpy as np

# Sidebar options
OPTIONS = {
            "Example files": {f"example_datafile:{element.name}": element.name for i, element in enumerate(data_files)},
            "Personalized data": {"w":"Write my own data", "r":"Create random data", "u":"Upload file"}
        }


ols_result = reactive.value([])
cols_constant = reactive.value(0)
sfa_result = reactive.value()

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
        with ui.card():
            ui.input_select("ineff_distr", "Distribution of the inefficiency term", ["Half-normal", "Exponential", "Truncated normal", "Gamma"])
        with ui.panel_conditional("input.datafile_selection === 'example_datafile:elsalvador.csv'"):
            with ui.card(height="150%"):
                ui.input_selectize("considered_elasticities", "Considered elasticities", 
                                   ["lland", "llabour", "lseeds", "lfertilizer", "lpesticide", "diste1"], 
                                   selected=["lland", "llabour", "lseeds", "lfertilizer", "lpesticide", "diste1"],
                                   multiple=True)
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
def display_OLS():
    # Get elasticities considered on the sidebar
    elasticities = list(input.considered_elasticities.get())

    # Compute and save ols/cols
    data = example_datafile_data.get()
    result = ols(data, "loutput", elasticities)
    ols_result.set(result)
    cols_const = cols_deterministic(result)
    cols_constant.set(cols_const)

    # Insert cols constant to params for displaying
    params = result.params
    params = np.insert(params, 1, cols_const)

    #Displayed dataframe (header are the elasticities name)
    df = pd.DataFrame({name: value for name, value in zip(["constant", "cols_constant"] + elasticities, params)}, 
                      index=['OLS'])
    return df


@reactive.calc
def compute_SFA():
    # Get relevant data
    elasticities = list(input.considered_elasticities.get())
    ols = ols_result.get()
    cols_const = cols_constant.get()
    data = example_datafile_data.get()

    result = compute_frontier('half-normal', data, ols, cols_const, 'loutput', elasticities)
    sfa = HalfNormal(result, elasticities)
    sfa_result.set(sfa)

    sfa.add_compund_error(data, 'loutput')
    sfa.add_epsilon_to_mu_star()

    return

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
                    ui.card_header("OLS estimation")
                    @render.data_frame
                    def f():
                        return display_OLS()
                with ui.card():
                    ui.card_header("Frontier estimation")
                    @render.data_frame
                    def g():
                        compute_SFA()
                        return sfa_result.get().dataframe()[0]
                    @render.data_frame
                    def h():
                        return sfa_result.get().dataframe()[1]
                with ui.card():
                    ui.card_header("Estimation of inefficiency per observation")
                    @render.data_frame
                    def j():
                        sfa = sfa_result.get()
                        inef = estimate_inefficiency(sfa, 'half-normal')
                        te = estimate_technical_efficiency(sfa, inef)
                        df = example_datafile_data.get().copy()
                        df.insert(0, 'efficiency_mode', te[1])
                        df.insert(0, 'efficiency_mean', te[0])
                        return df


elsalvador()