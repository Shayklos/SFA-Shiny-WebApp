from shiny.express import ui
from shared import data_dir, data_files


# ui.input_checkbox("show", "Show radio buttons", False)

# with ui.panel_conditional("input.show"):
#     ui.input_radio_buttons("radio", "Choose ", ["slider", "select"])

# with ui.panel_conditional("input.show && input.radio === 'slider'"):
#     ui.input_slider("slider", None, min=0, max=100, value=50)

# with ui.panel_conditional("input.show && input.radio === 'select'"):
#     ui.input_select("select", None, ["A", "B", "C"])

with ui.layout_sidebar(border=True):
    with ui.sidebar(bg="#F5F5F5"):
        ui.input_select("datafile_selection", "Choose the data", 
            {
                "Example files": {i: element for i, element in enumerate(data_files)},
                "Personalized data": {"w":"Write my own data", "r":"Create random data", "u":"Upload file"}
            }
        )