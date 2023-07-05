import pandas as pd
import numpy as np
import os
import sys
import PySimpleGUI as sg
import datetime as dt

dF = pd.DataFrame()


def GetFile():
    filename = sg.popup_get_file(
        "Select a lineup csv", no_window=True, file_types=(("CSV Files", "*.csv"),)
    )
    return None if filename == "" else filename


def TableReader(filename):
    data = []
    header_list = []
    button = sg.popup_yes_no("Does this file have column names already?")
    try:
        df = pd.read_csv(filename, sep=",", engine="python", header=None)
        if button == "Yes":
            # Use first row as headers
            header_list = df.iloc[0].tolist()
            # Drops the headers
            data = df[1:].values.tolist()
        elif button == "No":
            # Creates column names for each column
            header_list = ["column" + str(x) for x in range(len(data[0]))]
    except:
        sg.popup_error("Error Reading File")
        # Return to main menu

        # return

    table = [
        [
            sg.Table(
                values=data,
                headings=header_list,
                display_row_numbers=True,
                auto_size_columns=False,
                num_rows=min(25, len(data)),
                enable_events=True,
                enable_click_events=True,
                key="-TABLE-",
            )
        ]
    ]

    return table, filename, df, header_list


def SortColumns(dataframe, selection, extra_column):
    extra_column_array = extra_column.split(",")
    selection_array = selection.split(",")
    sorting_array = []

    for column in selection_array:
        values = dataframe[column].tolist()
        for i in values:
            sorting_array.append(i)

    if extra_column != "":
        selection_array.append(extra_column)
        for i in extra_column_array:
            sorting_array.append(int(i))

    sorted_array = SortList(sorting_array)

    return sorting_array, sorted_array


def SortList(list):
    # Sorts and returns a sorted array that removes duplicate entries
    return sorted([*set(list)])


# ----------- Create the 3 layouts this Window will display -----------
mm_3lineups = [[]]  # TableReader(GetFile())
mm_date_buttons = [
    [sg.Text(dt.date.today())],
    [sg.Button("Create")],
    [sg.Button("Edit")],
    [sg.Button("Sort")],
]

mainmenu = [
    [sg.Column(mm_date_buttons, key="-MM1"), sg.Column(mm_3lineups, key="-MM2")]
]

createmenu = [
    [sg.Text("This is layout 3 - It is all Radio Buttons")],
]

# ----------- Create actual layout using Columns and a row of Buttons
layout = [
    [
        sg.Column(mainmenu, key="-COL1-"),
        # sg.Column(sortmenu, visible=False, key="-COL2-"),
        sg.Column(createmenu, visible=False, key="-COL3-"),
    ],
]

window = sg.Window("Automated Lineup System", layout)


def change_layout(old_layout, new_layout):
    window[f"-COL{old_layout}-"].update(visible=False)
    window[f"-COL{new_layout}-"].update(visible=True)
    return new_layout


def sort_menu():
    sm_lineup, sm_filename, sm_df, sm_df_headers = TableReader(GetFile())
    print(sm_df_headers)
    sm_list = []
    sm_headers = []
    sortmenu = [
        [sg.Text(f"{sm_filename}")],
        [sg.Column(sm_lineup, key="-SM1-")],
        [
            sg.Button("Main Menu"),
            sg.Button("Add Column to Sort"),
            sg.Button("Sort Columns"),
            sg.Button("Clear Sorting List"),
        ],
        [sg.Text("Selected Columns:", key="-SELCOL-")],
        [sg.Text("Sorted List:", key="-SORLIS-")],
    ]

    sort_window = sg.Window("Sort Menu", sortmenu, modal=True)

    while True:
        event2, values2 = sort_window.read()
        print(event2, values2)
        if event2 == "Main Menu" or event2 == sg.WIN_CLOSED:
            break
        if "+CLICKED+" in event2:
            print(f"Row Selected: {event2[2][0]}")
            print(f"Column Selected: {event2[2][1]}")
            selected_column = event2[2][1]
            lineup_list = sm_df.iloc[1:, selected_column]
            print(lineup_list.to_list())

        if event2 == "Add Column to Sort":
            sm_headers.append(sm_df_headers[selected_column])
            print(sm_headers)
            sort_window["-SELCOL-"].update(f"Selected Columns: {set(sm_headers)}")
            for i in lineup_list.to_list():
                sm_list.append(i)
            print(sm_list)

        if event2 == "Sort Columns":
            sort_window["-SORLIS-"].update(f"Sorted List:{SortList(sm_list)}")

        if event2 == "Clear Sorting List":
            sort_window["-SORLIS-"].update("Sorted List:")
            sort_window["-SELCOL-"].update("Selected Columns:")
            sm_headers = []
            sm_list = []
    sort_window.close()


layout = 1  # The currently visible layout
while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    elif event == "Sort":
        sort_menu()

    elif event == "Main Menu":
        layout = change_layout(layout, 1)

window.close()
