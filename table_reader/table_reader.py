# This module should be used to bring the functions for reading lineup files into a separate module to make it easier to make applications around lineups
import pandas as pd
import datetime as dt
import numpy as np

from colorama import Back, Fore

fore_color = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE,
    Fore.LIGHTRED_EX,
    Fore.LIGHTGREEN_EX,
    Fore.LIGHTYELLOW_EX,
    Fore.LIGHTBLUE_EX,
    Fore.LIGHTMAGENTA_EX,
    Fore.LIGHTCYAN_EX,
]
back_color = [
    Back.RED,
    Back.GREEN,
    Back.YELLOW,
    Back.BLUE,
    Back.MAGENTA,
    Back.CYAN,
    Back.WHITE,
    Back.LIGHTRED_EX,
    Back.LIGHTGREEN_EX,
    Back.LIGHTYELLOW_EX,
    Back.LIGHTBLUE_EX,
    Back.LIGHTMAGENTA_EX,
    Back.LIGHTCYAN_EX,
]


def GetDays():  # Return days that match the next WS and then the next 2 and previous 1
    today = dt.date.today()  # Return the weekday

    # 0 = Monday, 6 = Sunday, 3 = Thursday
    if today.weekday() <= 3:  # Before or on a thursday
        # Return the date for the thursday, the saturday and the next week's thursday
        ws1 = today + dt.timedelta(
            days=(3 - today.weekday())
        )  # Shift into the thursday of this week
        ws2 = today + dt.timedelta(
            days=(6 - today.weekday())
        )  # Shift into this week's sunday
        ws0 = ws2 - dt.timedelta(days=7)
    if today.weekday() > 3 and today.weekday() <= 6:  # Between friday and sunday
        ws1 = today + dt.timedelta(days=6 - today.weekday())
        ws2 = today + dt.timedelta(days=(7 + (3 - today.weekday())))
        ws0 = ws2 - dt.timedelta(days=7)
    ws3 = ws1 + dt.timedelta(days=7)

    return [ws0, ws1, ws2, ws3]


def MainMenuDataframe():
    days = GetDays()
    print(days)
    prev_month = dt.date.today().replace(day=1) - dt.timedelta(days=1)
    # print(prev_month)
    whole_df = pd.DataFrame()
    whole_df = pd.concat([whole_df, Month_Dataframe(prev_month)], axis=1)
    mm_df = pd.DataFrame()
    missing_file = []
    for i, day in enumerate(days):
        print(day)
        if prev_month.month == day.month:
            print("In current month")
            # Don't add the dataframe but do add the corresponding header into the main menu dataframe
            try:
                mm_df = pd.concat([mm_df, whole_df[str(day)]], axis=1)
            except KeyError:
                print(f"Value in table not found: {i}")
                missing_file.append(FileFromDate(day))
                continue
            continue
        else:
            print("In new month")
            prev_month = day
            whole_df = pd.concat([whole_df, Month_Dataframe(day)], axis=1)
            # print(whole_df)
            try:
                mm_df = pd.concat([mm_df, whole_df[str(day)]], axis=1)
            except KeyError:
                print(f"Value in table not found: {day}")
                missing_file.append(FileFromDate(day))
                continue
    return mm_df, list(set(missing_file))


def Month_Dataframe(date):
    # Return the dataframe for the given month if it exists, while changing the headers
    try:
        file_df = pd.read_csv(FileFromDate(date), sep=",", engine="python")
    except:
        print(f"{FileFromDate(date)} not found")
        return
    headers = file_df.columns.tolist()
    normalised_headers = []
    for i in headers:
        if len(i) < 2:
            i = "0" + i
            normalised_headers.append(i)
        else:
            normalised_headers.append(i)
    new_headers = [str(date)[:8] + i for i in normalised_headers]
    file_df.columns = new_headers
    return file_df


def FileFromDate(date):  # Must be a datetime value
    # Standard naming convention from file is:
    # Lineup-[Month]-[Year].csv
    # Note, the locale is VERY important here, as changing locale will change this as well
    return "Lineup-" + date.strftime("%B-%Y") + ".csv"


def CreateFile(dataframe, file_name="newfile"):
    if file_name == None or file_name == (): # Unsure if windows returns an empty tuple for cancelling
        print("User cancelled")
        return
    file_extension = file_name[-4:]
    if file_extension == ".csv":
        pass
    elif file_extension != ".csv":
        file_name = file_name + ".csv"
    dataframe.to_csv(file_name, encoding="utf-8-sig", index=False)


def AddColumn(dataframe, header="", content=""):
    # Adds a column to an existing or new csv file
    # Input: List
    # Maximum Length: However long the longest column is. Cannot be longer.

    # Validate the header and content arguments
    if not header or not content:
        print("Please provide a valid header and content for the column.")
        # sg.Popup("Please provide a valid header and content for the column")
        return

    # Convert the content string into a list of integers
    try:
        content_list = list(map(int, (content.split(","))))
    except ValueError:
        # sg.Popup("Please input only numbers and commas for the content.")
        print("Please input only numbers and commas for the content.")
        return

    # Add the new column to the dataframe using pd.concat
    new_column = pd.DataFrame({header: content_list})
    dataframe = pd.concat([dataframe, new_column], axis=1)
    dataframe1 = dataframe.replace(np.nan, 0)
    dataframe2 = dataframe1.astype(int, copy=True, errors="raise")
    print(dataframe2)
    # Print the updated dataframe
    return dataframe2


def RemoveColumn(dataframe, header):
    # Removes a selected column
    # Input: Index
    print(dataframe)
    del dataframe[header]

    return dataframe
    # dataframe.drop(header,axis=1)


def SortColumns(dataframe, selection):
    # extra_column_array = extra_column.split(",")
    sorting_array = []
    if type(selection) == str:
        selection_array = selection.split(",")
    if type(selection) == list:
        selection_array = selection

    print(selection_array)

    for column in selection_array:
        values = dataframe[column].tolist()
        sorting_array.append(values)

    # if extra_column != "":
    #     selection_array.append(extra_column)
    #     sorting_array.append([int(x) for x in extra_column_array])

    return sorting_array, selection_array


def ReplaceColumn(dataframe, selection, data="", new_header=""):
    # Chooses the given column and replaces with the data given
    # Can replace the header if needed
    # Selection is integer so it should be
    # If new_header is empty, just replace the data, keep the column name.
    content_list = list(map(int, (data.split(","))))
    max_len = max(len(dataframe), len(content_list))
    print(selection, type(selection))
    print(new_header, type(new_header))
    if max_len > len(dataframe):
        df  = df.reindex(range(max_len))
    if new_header == selection:
        print("New header is old header")
        new_header = selection
    new_data = content_list
    # print(new_data)
    dataframe[selection] = pd.Series(new_data)
    # dataframe2 = dataframe.assign(new_header=new_data[new_header])
    dataframe = dataframe.rename({selection: new_header}, axis="columns", inplace=True)
    print(dataframe)
    try:
        dataframe = dataframe.replace(np.nan, 0)
    except: # When no nan values are present
        pass
    print(dataframe)
    return dataframe


def array_to_string(sorting_array, selection_array):
    # Converts string into platform specific colours. Might not work on linux for displaying in Multiline elements
    c_unsorted, c_sorted = ColorArray(sorting_array, selection_array)
    formatted_unsorted_array = ", ".join(str(item) for item in c_unsorted)
    formatted_sorted_array = ", ".join(str(item) for item in c_sorted)
    # print(formatted_unsorted_array + "\n" + formatted_sorted_array) -- added for fallback in case it doesn't work

    return formatted_sorted_array, formatted_unsorted_array


def ColorArray2(sorting_array, selection_array):
    # Obtain the separate lists to compare against
    # Assumes that each column is equal length
    print(sorting_array, selection_array)
    try:
        split_array = np.array_split(sorting_array, len(selection_array))
    except ValueError:
        print("No values to color")
        return [0], [0]
    # Can't sort the list later on so sort it now
    # sorted_array = sorted([*set(sorting_array)])
    sorted_array = sorted([*set(sorting_array)])
    unsorted_array = sorting_array[:]

    # Make copies that don't affect original
    final_sorted_array = sorted_array[:]
    final_unsorted_array = unsorted_array[:]
    # Each lineup will have their own colour.
    for color, column in enumerate(split_array):
        # Each element in the sorted array
        for count2, s_element in enumerate(sorted_array):
            # Check the current split array column. This will choose the color
            for count4, l in enumerate(
                set(column.tolist()), start=0
            ):  # Remove mismatched array length
                if l == s_element:  # If it exists in the column array, color it
                    final_sorted_array[count2] = (
                        fore_color[color] + str(s_element) + Fore.RESET
                    )
        # Same for unsorted array.
        for count3, us_element in enumerate(unsorted_array):
            for count5, l2 in enumerate(column.tolist(), start=0):
                if l2 == us_element:
                    final_unsorted_array[count3] = (
                        fore_color[color]
                        + str(final_unsorted_array[count3])
                        + Fore.RESET
                    )

    return final_unsorted_array, final_sorted_array

def ColorArray(sorting_array, selection_array):
    # Obtain the lists to sort, maybe switch over to just getting a list of arrays
    # Zip the arrays together and then assign colours based on their array index
    # Why not switch over to a pandas dataframe to send over?
    zipped = []
    color_index = 0
    for i in sorting_array: # Each i should be a list
        # dataframe_data = dataframe[i].tolist()
        data = i
        color_list = [fore_color[color_index%len(fore_color)]] * len(i)
        # zipped.append(zip(dataframe[i].tolist(), color_list))
        z = zip(data, color_list)
        for o in z:
            zipped.append(o)
        color_index += 1

    # Then make a sorted list of the indexes and unsorted list
    # Zipped is unsorted list
    sorted_zip = sorted(zipped, key=lambda x: x[0])

    # Then iterate over both, combining the color index with their respective string
    unsorted_colored = []
    # Remove zeros
    zipped = [x for x in zipped if x[0] != 0]
    for i in zipped:
        unsorted_colored.append(i[1] + str(i[0]) + Fore.RESET)

    # Remove zeros
    sorted_zip = [x for x in sorted_zip if x[0] != 0]
    sorted_colored = []
    for i in sorted_zip:
        sorted_colored.append(i[1] + str(i[0]) + Fore.RESET)

    return unsorted_colored, sorted_colored



def SortList(array):
    # Sorts and returns a sorted array that removes duplicate entries
    return sorted([*set(array)])
