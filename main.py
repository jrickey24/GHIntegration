import re
import csv
import os.path
import pyperclip
import pyautogui
import pandas as pd


def open_app(app_name):
    pyautogui.hotkey('win', 'r')  # send windows + run hotkey
    pyautogui.sleep(1)  # delay 1s
    pyautogui.write(app_name, interval=0.1)  # type cmd with .1 second delay between keystrokes
    pyautogui.press('enter')  # execute
    pyautogui.sleep(2)  # allow cmd to open before sending command


def send_cmd(cmd):
    pyautogui.press('enter')  # activate the window
    pyautogui.write(cmd, interval=0.1)  # send the command value
    pyautogui.press('enter')
    pyautogui.sleep(10)  # allow github results to populate before extracting


def extract_repos_to_csv(prepend_txt, append_txt, csv_file, i=0):
    pyautogui.hotkey('ctrl', 'a')  # select all content of cmd window
    pyautogui.sleep(.2)
    pyautogui.keyDown('ctrl')  # 1  - steps 1-3 are needed to copy to clipboard as work around for ctrl + c hotkey
    pyautogui.press('c')  # 2
    pyautogui.keyUp('ctrl')  # 3
    pyautogui.sleep(.2)
    windows_found = [w for w in pyautogui.getAllWindows() if 'cmd.exe' in w.title]  # check for cmd window
    if len(windows_found) > -1:
        windows_found[0].close()  # close cmd window
    response_returned = pyperclip.paste()  # get the raw response from the clipboard
    target_index = re.search(r'\b(repositories)\b', response_returned)  # find the index of the regex
    start_extract = target_index.end()  # get the position of the last sub-index of the target index
    # filter out the response result text that precedes & proceeds the returned repos data
    filtered_result = str(response_returned[(start_extract + 1):-(len(os.path.expanduser('~')) + 4)]).strip()
    repos = filtered_result.splitlines()  # split the result string line by line
    repo_list = []
    for repo in repos:
        split_repo = repo.split(sep="\t")  # split the repo lines by tab delimiter
        split_repo_field = re.split('\s', split_repo[0])  # split fields on the first occurrence of white space
        i += 1
        if i > 1:
            repo_name = split_repo_field[0]  # extract the repo name
            repo_ssh = prepend_txt + repo_name + append_txt  # generate ssh url by prepending & appending txt to name
            repo_list.append([repo_name, repo_ssh])  # append the repo_name & repo_ssh to the repo_list
    file = open(csv_file, 'w+', newline='')  # save the repo names & ssh urls to csv for later use
    with file:
        write = csv.writer(file)
        write.writerows(repo_list)


def clone_repos(read_file, passphrase):
    df = pd.read_csv(read_file, header=None, prefix='col_')  # read specific csv into pandas dataframe
    for r, i in df.iterrows():  # iterate through the dataframe to get ssh url of repos & clone them
        clone_cmd = "gh repo clone " + df.at[r, 'col_1']
        pyperclip.copy(clone_cmd)
        windows_found = [w for w in pyautogui.getAllWindows() if 'MING' in w.title]  # check for git bash window
        if len(windows_found) > -1:
            windows_found[0].maximize()  # maximize git bash window
            pyautogui.sleep(5)  # wait for window to resize
            pyautogui.press('enter')  # make sure window gets activated before pasting clone command
            pyautogui.hotkey('shift', 'insert')  # paste clone command into git bash
            pyautogui.press('enter')  # execute command
            pyautogui.sleep(3)  # delay to allow prompt for ssh key passphrase
            pyautogui.write(passphrase)  # send ssh passphrase
            pyautogui.sleep(.5)  # delay for acceptance
            pyautogui.press('enter')  # execute
            pyautogui.sleep(2)  # delay before next iteration to allow prior repo clone to finish


def main() -> None:
    open_app("cmd")
    send_cmd("gh search repos abc --language python --limit 15")
    extract_repos_to_csv("git@github.com:", ".git", "gh_repos.csv")
    clone_repos("gh_repos_cli.csv", "chopin")


if __name__ == "__main__":
    main()
