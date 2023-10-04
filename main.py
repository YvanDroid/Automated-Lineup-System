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


def CreateFile(dataframe, file_name="newfile"):
    file_extension = file_name[-4:]
    if file_extension == ".csv":
        pass
    elif file_extension != ".csv":
        file_name = file_name + ".csv"
    dataframe.to_csv(file_name, encoding="utf-8-sig", index=False)


def CreateTable(dataframe, rc_menu):
    data = dataframe.values.tolist()
    headers = dataframe.columns.tolist()

    table = [
        [
            sg.Table(
                values=data,
                headings=headers,
                display_row_numbers=True,
                auto_size_columns=False,
                num_rows=min(25, len(data)),
                enable_events=True,
                enable_click_events=True,
                key="-TABLE-",
                right_click_menu=rc_menu,
                right_click_selects=True,
            )
        ]
    ]

    return table, headers


def TableReader(filename, rc_menu):
    # data = []
    # header_list = []
    # button = sg.popup_yes_no("Does this file have column names already?")
    try:
        df = pd.read_csv(filename, sep=",", engine="python")
        # data = df.values.tolist()
        # # if button == "Yes":
        # # Use first row as headers
        # header_list = df.columns.tolist()  # df.iloc[0].tolist()
        # # Drops the headers
        # # data = df[1:].values.tolist()
        # # elif button == "No":
        # #     # Creates column names for each column
        # #     header_list = ["column" + str(x) for x in range(len(data[0]))]
    except:
        sg.popup_error("Error Reading File")

    table, headers = CreateTable(df, rc_menu)
    return table, df, headers


def TableUpdate(dataframe, window):
    # Recreate the window for the table
    # Close the old window
    # window_table is the window['index'] of the table.
    # Returns a values and headings of the listed dataframe.
    # data = dataframe.values.tolist()
    # headers = dataframe.columns.tolist()

    window.close()
    create_edit_menu(dataframe, mode=0)
    # window_table.update(values=data, headings=headers)
    # table.configure(columns=(i for i in headers))
    # for i in headers:
    #     table.heading(i, text=headers[i])


def AddColumn(dataframe, header="", content=""):
    # Adds a column to an existing or new csv file
    # Input: List
    # Maximum Length: However long the longest column is. Cannot be longer.

    # Validate the header and content arguments
    if not header or not content:
        # print("Please provide a valid header and content for the column.")
        sg.Popup("Please provide a valid header and content for the column")
        return

    # Convert the content string into a list of integers
    try:
        content_list = list(map(int, (content.split(","))))
    except ValueError:
        sg.Popup("Please input only numbers and commas for the content.")
        return

    # Add the new column to the dataframe using pd.concat
    new_column = pd.DataFrame({header: content_list})
    dataframe = pd.concat([dataframe, new_column], axis=1)
    dataframe1 = dataframe.replace(np.nan, 0)
    dataframe2 = dataframe1.astype(int, copy=True, errors="raise")
    # Print the updated dataframe
    return dataframe2


def RemoveColumn(dataframe, header):
    # Removes a selected column
    # Input: Index
    print(dataframe)
    del dataframe[header]

    return dataframe
    # dataframe.drop(header,axis=1)


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

# ----------- Create actual layout using Columns and a row of Buttons
layout = [
    [
        sg.Column(mainmenu, key="-COL1-"),
    ],
]

window = sg.Window("Automated Lineup System", layout)


def create_edit_menu(dataframe, mode=0):  # Editing = 1, Creating = 0
    ce_rc_menu = [
        "&Right",
        ["Delete Column", "Select Column to Replace", "Save to File"],
    ]
    ce_title = "Table Editor"
    if mode == 1:  # No name given
        ce_filename = GetFile()
        ce_table, ce_dF, ce_headers = TableReader(ce_filename, ce_rc_menu)
    if mode == 0:
        ce_dF = dataframe
        ce_table, ce_headers = CreateTable(ce_dF, ce_rc_menu)

    ce_form = [
        [sg.Text("Header")],
        [sg.Input("", key="-CEHEAD-"), sg.Button("Clear", key="-CEHEADCLR-")],
        [sg.Text("List")],
        [sg.Input("", key="-CELIST-"), sg.Button("Clear", key="-CELISTCLR-")],
        [sg.Button("Submit Column"), sg.Button("Replace Selected Column")],
    ]

    ce_menu = [
        [sg.Column(ce_table, key="-CE1-"), sg.Column(ce_form, key="-CEFORM-")],
        [sg.Button("Main Menu"), sg.Button("Save to File"), sg.Button("Open New File")],
    ]  # Layout
    ce_window = sg.Window(ce_title, ce_menu)

    ce_table = ce_window["-TABLE-"].Widget
    selected_column = 0

    while True:
        event3, values3 = ce_window.read()
        print(f"event3's output: {event3}")
        print(f"values3's output: {values3}")
        if event3 == "Main Menu" or event3 == sg.WIN_CLOSED:
            break
        if "+CLICKED+" in event3:
            selected_column = event3[2][1]
            # The second value in the tuple given by the table
            print(selected_column)

        if event3 == "Submit Column":
            ce_dF = AddColumn(
                ce_dF, header=values3["-CEHEAD-"], content=values3["-CELIST-"]
            )
            TableUpdate(ce_dF, ce_window)

        if event3 == "Delete Column" or event3 == "Delete Selected Column":
            print(ce_headers[selected_column])
            ce_dF = RemoveColumn(ce_dF, str(ce_headers[selected_column]))
            TableUpdate(ce_dF, ce_window)

        if event3 == "Save to File":
            CreateFile(
                ce_dF,
                file_name=sg.popup_get_text(
                    "Please enter the name to save", title="Save file name"
                ),
            )

    ce_window.close()


def change_layout(old_layout, new_layout):
    window[f"-COL{old_layout}-"].update(visible=False)
    window[f"-COL{new_layout}-"].update(visible=True)
    return new_layout


def sort_menu():
    selected_column = 0  # Default for if the user has not selected a column yet
    sm_filename = GetFile()
    sm_rc_menu = [
        "&Right",
        ["Add Column to Sort", "Sort Columns", "Clear Sorting List"],
    ]
    if sm_filename == None:
        sg.popup("No file selected. Returning to menu")
        return
    sm_table, sm_df, sm_df_headers = TableReader(sm_filename, sm_rc_menu)
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
            lineup_list = sm_df.iloc[0:, selected_column]
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
        create_edit_menu("", 1)
    elif event == "Create":
        dF = pd.DataFrame()
        create_edit_menu(dF, 0)

window.close()
