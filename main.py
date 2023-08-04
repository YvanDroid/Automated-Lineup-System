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

    return table, df, header_list


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


def create_edit_menu(edit_status=0):  # Editing = 1, Creating = 0
    # To do:
    # Make layout
    # Add event handling
    # Find a way to sync the table and the dataframe

    if edit_status == 1:
        # Editing file
        # Obtain file using GetFile()
        # Put csv into dataframe
        ce_title = "Edit Menu"
        ce_filename = GetFile()
        ce_table, ce_dF, ce_headers = TableReader(ce_filename)
    else:
        # Creating file
        # No table yet, so don't try it
        # Intialize an empty dataframe
        ce_title = "Create Menu"
        ce_headers = []
        ce_dF = pd.DataFrame()
        ce_dummy_data = ["This", "Will", "Change", "When", "First", "Column", "Added"]
        ce_table = [
            [
                sg.Table(
                    values=ce_dummy_data,
                    headings=["column" + str(x) for x in range(len(ce_dummy_data))],
                    display_row_numbers=True,
                    auto_size_columns=False,
                    num_rows=min(25, len(ce_dummy_data)),
                    enable_events=True,
                    enable_click_events=True,
                    key="-TABLE-",
                )
            ]
        ]

    ce_menu = []  # Layout
    ce_window = sg.Window(ce_title, ce_menu)

    while True:
        event, values = ce_window.read()
        if event == "Main Menu" or event == sg.WIN_CLOSED:
            break

    ce_window.close()


def change_layout(old_layout, new_layout):
    window[f"-COL{old_layout}-"].update(visible=False)
    window[f"-COL{new_layout}-"].update(visible=True)
    return new_layout


def sort_menu():
    sm_filename = GetFile()
    if sm_filename == None:
        sg.popup("No file selected. Returning to menu")
        return
    sm_table, sm_df, sm_df_headers = TableReader(sm_filename)
    print(sm_df_headers)
    sm_list = []
    sm_headers = []
    sortmenu = [
        [sg.Text(f"Now reading: {sm_filename}")],
        [sg.Column(sm_table, key="-SM1-")],
        [
            sg.Button("Main Menu"),
            sg.Button("Add Column to Sort"),
            sg.Button("Sort Columns"),
            sg.Button("Clear Sorting List"),
            sg.Button("Add One-Off Column", key="-SORTEXTRA-"),
            sg.Input(key="-SORTEXTRADATA-"),
        ],
        [sg.Text("Selected Columns:", key="-SELCOL-")],
        [sg.Text("Unsorted List:", key="-UNSORLIS-")],
        [sg.Text("Sorted List:", key="-SORLIS-")],
    ]

    sort_window = sg.Window("Sort Menu", sortmenu, modal=True)
    sort_window.finalize()
    while True:
        event2, values2 = sort_window.read()
        print(event2, values2)
        if event2 == "Main Menu" or event2 == sg.WIN_CLOSED:
            break
        if "+CLICKED+" in event2:
            # Find the selected column
            print(f"Row Selected: {event2[2][0]}")
            print(f"Column Selected: {event2[2][1]}")
            selected_column = event2[2][1]
            # Display the selected column in terminal
            lineup_list = sm_df.iloc[1:, selected_column]
            print(lineup_list.to_list())

        if event2 == "Add Column to Sort":
            sm_headers.append(sm_df_headers[selected_column])
            print(sm_headers)
            sort_window["-SELCOL-"].update(f"Selected Columns: {set(sm_headers)}")
            for i in lineup_list.to_list():
                sm_list.append(i)
            print(sm_list)
            sort_window["-UNSORLIS-"].update(f"Unsorted List: {sm_list}")

        if event2 == "-SORTEXTRA-":
            # Grab the data from the text box and make it into a list.
            try:
                extra_list = values2["-SORTEXTRADATA-"].split(",")
                for i in extra_list:
                    sm_list.append(int(i))
                sort_window["-UNSORLIS-"].update(f"Unsorted List: {sm_list}")
            except:
                sg.popup_ok(
                    "Please make sure that your list is populated and consists of integers."
                )

        if event2 == "Sort Columns":
            sort_window["-SORLIS-"].update(f"Sorted List:{SortList(sm_list)}")

        if event2 == "Clear Sorting List":
            sort_window["-SORLIS-"].update("Sorted List:")
            sort_window["-UNSORLIS-"].update("Unsorted List:")
            sort_window["-SELCOL-"].update("Selected Columns:")
            sm_headers = []
            sm_list = []
    sort_window.close()


while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    elif event == "Sort":
        sort_menu()
    elif event == "Edit":
        create_edit_menu(1)
    elif event == "Create":
        create_edit_menu(0)

window.close()
