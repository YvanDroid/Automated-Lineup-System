import os
import re

# Please place this script in the root directory of your hymns folder

user_input = input(
    "Please enter the list of hymns that you want to put in order, separated by commas: \n"
)

filename = input("Please enter the name of the playlist: \n")

if filename[-4:] != ".m3u":
    filename = filename + ".m3u"

hymn_list = user_input.split(",")
print(hymn_list)
cwd = os.getcwd()

mp3files = [
    os.path.join(root, name)
    for root, dirs, files in os.walk(cwd)
    for name in files
    if name.endswith((".mp3"))
]

hymn_paths = []


def substring_index(path_list, substring):
    search_string = rf"\b([E,T]?)329\b(?!([\W\D](alto|bass|soprano|tenor|\(alto\)|\(tenor\)|\(bass\)|\(soprano\))))"
    for i, s in enumerate(path_list):
        if re.search(search_string, s) is not None:
            return i
    return -1


for h in hymn_list:
    result = substring_index(mp3files, h)
    if result != -1:
        try:
            print(f"{h} found at {mp3files[result]}")
            hymn_paths.append(mp3files[result] + "\n")
        except IndexError:
            print("I have no idea why it fails here")
    else:
        print("Hymn not found. Please source the file and try again")

# Make a file
with open(filename, "+w") as f:
    f.writelines(hymn_paths)

complete_dialog = input(
    f"Playlist complete, saves as {filename}. Please press enter to complete"
)
