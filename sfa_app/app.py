from shiny.express import ui, render, input


from shared import data_dir, data_files
import pandas as pd


# ui.input_checkbox("show", "Show radio buttons", False)

# with ui.panel_conditional("input.show"):
#     ui.input_radio_buttons("radio", "Choose ", ["slider", "select"])

# with ui.panel_conditional("input.show && input.radio === 'slider'"):
#     ui.input_slider("slider", None, min=0, max=100, value=50)

# with ui.panel_conditional("input.show && input.radio === 'select'"):
#     ui.input_select("select", None, ["A", "B", "C"])

with ui.sidebar(bg="#F5F5F5"):
    ui.input_select("datafile_selection", "Choose the data", 
        {
            "Example files": {f"example_datafile:{i}": element.name for i, element in enumerate(data_files)},
            "Personalized data": {"w":"Write my own data", "r":"Create random data", "u":"Upload file"}
        }
    )
    with ui.panel_conditional("input.datafile_selection.includes('example_datafile')"):
        
        ui.input_select("ineff_distr", "Distribution of the inefficiency term", ["Half-normal", "Exponential", "Truncated normal", "Gamma"])


with ui.panel_conditional("!input.datafile_selection.includes('example_datafile')"):
    "Not implemented"

with ui.panel_conditional("input.datafile_selection.includes('example_datafile')"):
    with ui.navset_pill(id="tab"):  
        with ui.nav_panel("Data"):
            with ui.card(full_screen=True):
                ui.card_header("Data")

                @render.data_frame
                def table():
                    if ':' not in (selection := input.datafile_selection.get()): 
                        return
                    index = int(selection.split(":")[-1])
                    file = data_files[index]
                    data = pd.read_csv(file)

                    return render.DataGrid(data)

        with ui.nav_panel("Result"):
            @render.text
            def f():
                return input.ineff_distr.get()
