import pandas as pd
from shiny import reactive
from shiny.express import input

example_datafile_data = reactive.value(pd.DataFrame())

@reactive.effect
@reactive.event(input.datafile_selection)
def _():
    print("xD")
    if "example_datafile" not in (selection := input.datafile_selection.get()):
        print("allo")

    print("eiyou")