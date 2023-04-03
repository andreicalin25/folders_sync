import sys
import os
import shutil
import hashlib
from datetime import datetime
import time


def write_to_file(text):
    ''' add text to a file '''

    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")


def write_to_console_and_file(text):
    ''' just one method that outputs both to console and to file '''
    print(text)
    write_to_file(text)


def folder_contents(path):
    ''' returns two lists (subdirectories, files) of all the contents found in the folder and
        subfolders with the given path '''

    filelist = []
    dirlist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            # os.path.join gets me the full path of each file
            # os.path.relpath gets me the relative (to the folder) path of each file
            filelist.append(os.path.relpath(os.path.join(root, file), path))

        for dir in dirs:
            dirlist.append(os.path.relpath(os.path.join(root, dir), path))

    return dirlist, filelist


def get_contents(source_folder, replica_folder):
    ''' function that takes a source folder and a replica folder
        and returns two lists(subdirectories, files) with their contents'''

    if not os.path.exists(source_folder):
        raise Exception("The source folder does not exist")
    if not os.path.exists(replica_folder):
        os.mkdir(replica_folder)

    source_contents = folder_contents(source_folder)
    replica_contents = folder_contents(replica_folder)

    return source_contents, replica_contents


def add_dirs(new_dirs, replica_folder):
    ''' copies new subdirectories from the source folder to the replica folder '''

    write_to_console_and_file("\nAdding new subdirectories:")
    for dir in new_dirs:
        replica_dir = os.path.join(replica_folder, dir)
        os.makedirs(replica_dir, exist_ok=True)

        write_to_console_and_file(f"{dir} was created")

    if len(new_dirs) == 0:
        write_to_console_and_file("no new subdirectory was created since last check")


def add_files(new_files, source_folder, replica_folder):
    ''' copies new files from the source folder to the replica folder '''

    write_to_console_and_file("\nAdding new files:")
    for file in new_files:
        source_file = os.path.join(source_folder, file)
        replica_file = os.path.join(replica_folder, file)

        # I copy the new file
        shutil.copy2(source_file, replica_file)

        write_to_console_and_file(f"{file} was copied")

    if len(new_files) == 0:
        write_to_console_and_file("no new file was created since last check")


def delete_files(removed_files, replica_folder):
    ''' deletes all files that no longer exist in the source folder '''

    write_to_console_and_file("\nDeleting old files:")
    for file in removed_files:
        replica_file = os.path.join(replica_folder, file)
        os.remove(replica_file)

        write_to_console_and_file(f"{file} was deleted")

    if len(removed_files) == 0:
        write_to_console_and_file("no file was removed since last check")


def delete_dirs(removed_dirs, replica_folder):
    ''' deletes all subdirectories that no longer exist in the source folder '''

    # I sort the dirs descending by default(lenght of sting) because I want to make sure that
    # 'dir1/dir2/dir3' is deleted before 'dir1/dir2'
    removed_dirs.sort(key=len, reverse=True)

    write_to_console_and_file("\nDeleting old subdirectories:")
    for dir in removed_dirs:
        replica_dir = os.path.join(replica_folder, dir)
        os.rmdir(replica_dir)

        write_to_console_and_file(f"{dir} was deleted")

    if len(removed_dirs) == 0:
        write_to_console_and_file("no subdirectory was removed since last check")


def get_hash(file):
    ''' returns a hash of the file '''

    with open(file) as f:
        data = f.read()
        return hashlib.md5(data.encode('UTF-8')).hexdigest()


def rewrite_files(common_files, source_folder, replica_folder):
    ''' rewrites files from source folder if they differ from those in replica folder '''

    rewritten_check = False

    write_to_console_and_file("\nRewriting changed files:")
    for file in common_files:
        source_file = os.path.join(source_folder, file)
        replica_file = os.path.join(replica_folder, file)


        if get_hash(source_file) != get_hash(replica_file):
            rewritten_check = True
            os.remove(replica_file)
            shutil.copy2(source_file, replica_file)

            write_to_console_and_file(f"{file} was rewritten")

    if not rewritten_check:
        write_to_console_and_file("no file was rewritten since last check")


def sync(source_folder, replica_folder):
    ''' function that is called once every given time (interval) and syncs the two folders '''

    current_time = datetime.now().strftime("%H:%M:%S")
    write_to_console_and_file(f"\n\n\n ----- Syncronization done at {current_time} ----- ")

    source_contents, replica_contents = get_contents(source_folder, replica_folder)

    source_dirs, source_files = source_contents
    replica_dirs, replica_files = replica_contents

    new_dirs = list(set(source_dirs) - set(replica_dirs))
    new_files = list(set(source_files) - set(replica_files))
    removed_dirs = list(set(replica_dirs) - set(source_dirs))
    removed_files = list(set(replica_files) - set(source_files))
    common_files = [x for x in source_files if x in replica_files]

    add_dirs(new_dirs, replica_folder)
    add_files(new_files, source_folder, replica_folder)
    delete_files(removed_files, replica_folder)
    delete_dirs(removed_dirs, replica_folder)
    rewrite_files(common_files, source_folder, replica_folder)


def main():
    ''' main '''
    global LOG_FILE

    souce_folder, replica_folder = sys.argv[1:3]
    time_interval = int(sys.argv[3])
    LOG_FILE = sys.argv[4]
    with open(LOG_FILE, "w") as f:
        f.write("")

    while True:
        sync(souce_folder, replica_folder)
        time.sleep(60*time_interval)


if __name__ == "__main__":
    main()
