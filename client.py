from ftplib import FTP
import sqlite3
import os
import sys
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

working_dir = os.getcwd()

logFile = 'log.log'
logging.basicConfig(filename=logFile, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)
logger.info("-"*40)
logger.info("client.py starting with parameter(s): {}".format(sys.argv[1:]))
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=1*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setLevel(logging.INFO)
# logger.addHandler(my_handler)


class Settings:  # used to interact with settings for CustomFTPClient
    def ftp_setup_interface(self):
        ftp_settings = self.get_settings("ftp_settings")
        if len(ftp_settings) == 0:
            msg = "\nYou have no servers set up. Type ADD to add a server:"
        else:
            msg = "\nYou have {} server(s) already set up. Type HELP HERE to see FTP SETUP options:" \
                  "".format(len(ftp_settings))
        Input().input_catcher(msg, "FTP SETUP", **{"add": self.add_ftp_server, "show": self.show_ftp_servers,
                                                   "edit": self.edit_ftp_server, "delete": self.delete_ftp_server})
        self.ftp_setup_interface()

    def add_ftp_server(self, command="ADD", delete=None):
        name = Input().input_catcher("Please enter a name for the new server connection settings:",
                                     "FTP SETUP - {}".format(command))
        host = Input().input_catcher("Please enter the host name (IP address only) for the FTP server you are trying to"
                                     " access:", "FTP SETUP - {}".format(command), "input_.count('.') == 3",
                                     "7 <= len(input_) <= 15", "any(char.isdigit() for char in input_)")
        username = Input().input_catcher("Please enter the username for the FTP server you are trying to access:",
                                         "FTP SETUP - {}".format(command))
        password = Input().input_catcher("Please enter the password for the FTP server you are trying to access:",
                                         "FTP SETUP - {}".format(command))
        msg = "\nPlease confirm that the following settings are correct:\n\nName - {name}\nHost - {host}\n" \
              "Username - {username}\nPassword - ****\n\nType YES/Y for yes and NO/N for no " \
              "(type SHOW to show password):".format(name=name, host=host, username=username)
        while True:
            response = Input().input_catcher(msg, "FTP SETUP - {}".format(command))
            if response.lower() in ['yes', 'y']:
                break
            elif response.lower() in ['no', 'n']:
                print("Okay, restarting the setup process.\n")
                self.add_ftp_server()
            elif response.lower() == 'show':
                msg = "Name - {name}\nHost - {host}\nUsername - {username}\nPassword - {password}\n\n" \
                      "Type YES/Y for yes and NO/N for no (type SHOW to show password):" \
                      "".format(name=name, host=host, username=username, password=password)
                response = Input().input_catcher(msg, "FTP SETUP - {}".format(command))
                if response.lower() in ['yes', 'y']:
                    break
                elif response.lower() in ['no', 'n']:
                    print("Okay, restarting the setup process.\n")
                    self.add_ftp_server()
            else:
                print("\nPlease enter a valid response!\n")
        if delete is not None:
            self.delete_ftp_server(delete, silent=True)
            
        connection, cursor = DBInteraction().db_opener("settings.db")
        try:
            cursor.execute("INSERT INTO ftp_settings VALUES(?, ?, ?, ?)", (name, host, username, password))
        except sqlite3.IntegrityError:
            print("Error! Name is already in use. Please start again with a different name.")
        connection.commit(), cursor.close(), connection.close()

    def show_ftp_servers(self, name):
        if name == "all":
            name = None
        try:
            servers = self.get_settings("ftp_settings", name)
            for server in servers:
                print("Server Name:\t{name}\nHost Address:\t{host}\nUsername:\t\t{username}\nPassword:\t\t{password}\n"
                      "".format(name=server[0], host=server[1], username=server[2], password=server[3]))
        except sqlite3.OperationalError:
            print("No such server name saved! Type SHOW ALL to see full list of saved servers.")

    def edit_ftp_server(self, name):
        msg = "Settings saved for {} will now be deleted and you will be sent to add new details. Are you sure " \
              "you want to continue?".format(name)
        Input().input_catcher(msg, "FTP SETUP", **{"yes": [self.add_ftp_server, "EDIT", name],
                                                   "no": [print,
                                                          "You are being redirected to the FTP SETUP homepage"]})

    def delete_ftp_server(self, name, silent=False):
        connection, cursor = DBInteraction().db_opener("settings.db")
        cursor.execute("DELETE FROM ftp_settings WHERE name = \"{}\"".format(name))
        connection.commit(), cursor.close(), connection.close()
        if not silent:
            print("{} has been successfully deleted!".format(name))

    def get_settings(self, table, name=None):
        connection, cursor = DBInteraction().db_opener("settings.db")
        if name is None:
            cursor.execute("SELECT * FROM {}".format(table))
        else:
            cursor.execute("SELECT * FROM {} WHERE name = \"{}\"".format(table, name))
        settings = cursor.fetchall()
        cursor.close(), connection.close()
        return settings

    def path_setup_interface(self):
        paths = self.get_settings("path_settings")
        if len(paths) == 0:
            msg = "\nYou have no paths set up. Type ADD to add a path:"
        else:
            msg = "\nYou have {} path(s) already set up. Type HELP HERE to see PATH SETUP options:" \
                  "".format(len(paths))
        Input().input_catcher(msg, "PATH SETUP", **{"add": self.add_path, "show": self.show_paths,
                                                    "edit": self.edit_paths, "delete": self.delete_paths})
        self.path_setup_interface()

    def add_path(self, command="ADD", delete=None):
        name = Input().input_catcher("Please enter the name for the server connection that the path is being added for:"
                                     "", "PATH SETUP - {}".format(command))
        remote_path = Input().input_catcher("Please enter the path for the remote server:",
                                            "PATH SETUP - {}".format(command))
        local_path = Input().input_catcher("Please enter the local path:", "PATH SETUP - {}".format(command))

        remote_path = "/files/DOWNLOADED/AUTODL/DOWNLOADING"
        # remote_path = "/files/AUTODL/DOWNLOADED/apple"
        # remote_path = "/files/DOWNLOADED/RATIO"
        local_path = "D:\Downloads"

        if delete is not None:
            self.delete_paths(delete, silent=True)
        connection, cursor = DBInteraction().db_opener("settings.db")
        try:
            cursor.execute("INSERT INTO path_settings VALUES(?, ?, ?)", (name, remote_path, local_path))
        except sqlite3.IntegrityError:
            print("Error! Server name does not exist (or remote path with local path provided are already set). Please "
                  "start again with a known server configuration name. To see all server configurations (and their "
                  "names) type HELP to get help navigating to the FPT SETUP for the SHOW ALL command.")
        connection.commit(), cursor.close(), connection.close()

    def show_paths(self, name):
        if name == "all":
            name = None
        try:
            servers = self.get_settings("path_settings", name)
            for server in servers:
                print("Server Name:\t{name}\nRemote Path:\t{remote}\nLocal Path:\t\t{local}\n".format(name=server[0],
                                                                                                      remote=server[1],
                                                                                                      local=server[2]))
        except sqlite3.OperationalError:
            print("No such server name saved! Type SHOW ALL in FTP SETUP to see full list of saved servers to add paths"
                  " for.")

    def edit_paths(self, name):
        msg = "Settings saved for {} will now be deleted and you will be sent to add new details. Are you sure " \
              "you want to continue?".format(name)
        Input().input_catcher(msg, "PATH SETUP", **{"yes": [self.add_path, "EDIT", name],
                                                    "no": [print,
                                                           "You are being redirected to the PATH SETUP homepage"]})

    def delete_paths(self, name, silent=False):  # fix this to work with path not name and to ensure that wrong details
        # presents an error message as opposed to saying it works
        msg = "In order to continue all related recorded downloads will need to be purged. Are you sure you want to " \
              "continue? Type either YES or NO."
        Input().input_catcher(msg, "DELETE PATH", "input_ in ['yes', 'no]")
        connection, cursor = DBInteraction().db_opener("settings.db")
        cursor.execute("DELETE FROM path_settings WHERE name = \"{}\"".format(name))
        # print(cursor.rowcount)
        connection.commit()
        cursor.close(), connection.close()
        if not silent:
            print("{} has been successfully deleted!".format(name))

    def combine_funcs(*funcs):  # this function is used to allow buttons to call multiple functions since they can
        # otherwise only call one; this function is the function called by the button and it can input as the parameters
        # to this function whichever other functions (and however many)
        def combined_func(*args, **kwargs):
            for f in funcs:
                f(*args, **kwargs)
        return combined_func


class FTPClient:
    def check_dirs(self, name):
        logger.info("Checking directory for server name:", name)
        if name == "all":
            name = None
        for ftp_ in Settings().get_settings("ftp_settings", name):
            dirs = Settings().get_settings("path_settings", name)
            print("{}\nFTP Server Name: {}\n{}".format("-"*20, ftp_[0], "-"*20))
            with FTP(host=ftp_[1], user=ftp_[2], passwd=ftp_[3]) as ftp:
                for dir_ in dirs:
                    print("\nDirectory:", dir_[1], "\n")
                    print("Type\tSize\t\t\tName\n{}".format("-"*40))
                    for item in list(ftp.mlsd(dir_[1], ["type", "size", "perm"])):
                        try:
                            print("{type}\t{size}\t\t{name}".format(type=item[1]['type'], size=item[1]['size'],
                                                                    name=item[0]))
                        except KeyError:
                            print("{type}\t\t\t\t\t\t{name}".format(type=item[1]['type'], name=item[0]))
                print()
        Interface()

    def run_now(self):
        to_create, to_save = list(), list()

        def get_children_dirs(ftp_, path, folder_name, first=False):
            # path = path + "/" if path[-1] != "\\" else path  # work out the double forward slash that's occurring
            if not first:
                to_create.append(["{}/{}".format(path, folder_name), "dir"])  # to create the folder
            for item_ in list(ftp_.mlsd("{}/{}".format(path, folder_name), ['type'])):
                if item_[1]['type'] == "dir":  # send this folder for iteration as well
                    get_children_dirs(ftp, "{}/{}".format(path, folder_name), item_[0])
                if item_[1]['type'] == "file":  # to create the files in the folder
                    to_create.append(["{}/{}/{}".format(path, folder_name, item_[0]), "file"])

        for ftp_ in Settings().get_settings("ftp_settings"):
            dirs = Settings().get_settings("path_settings")
            logger.info("Logging into FTP server with host={}, user={} and password={}...".format(*ftp_[1:]))
            with FTP(host=ftp_[1], user=ftp_[2], passwd=ftp_[3]) as ftp:
                logger.info("Login successful.")
                for dir_ in dirs:
                    get_children_dirs(ftp, dir_[1], "", True)

                file_names = DBInteraction().get_downloaded_files_list()
                # [print(item) for item in file_names]
                print()
                total_file_count, file_count, mk_dir_count = int(), int(), int()

                for item in to_create:
                    destination = dir_[2] + item[0][len(dir_[1]) + 1:].replace("/", "\\")
                    remote_path = item[0].replace("//", "/")[1:]

                    if item[1] == "dir":
                        cont = False
                        for file in to_create[to_create.index(item) + 1:]:
                            if file[1] == "dir":
                                break
                            cont = True if file[0] in file_names else None
                        if cont:  # only if any files in current dir have not yet been downloaded then create dir for em
                            continue

                        if remote_path not in file_names:  # don't create folders that have already been downloaded
                            try:
                                os.mkdir(destination)
                                mk_dir_count += 1
                            except FileExistsError:
                                pass
                            # print(item[0] + " built")
                            to_save.append([dir_[1], dir_[2], remote_path, "dir"])  # mark file as downloaded

                    if item[1] == "file":
                        total_file_count += 1

                        if remote_path not in file_names:  # download file if not been downloaded yet
                            file_count += 1
                            logger.info("Command: RETR {filename}; Destination: {dest}".format(filename=remote_path,
                                                                                               dest=destination))
                            print("Command: RETR {filename}; Destination: {dest}".format(filename=remote_path,
                                                                                         dest=destination))
                            local_file = open(destination + '.!sync', "wb+")
                            ftp.retrbinary("RETR {filename}".format(filename=remote_path), local_file.write)
                            local_file.close()

                            to_save.append([dir_[1], dir_[2], remote_path, "file"])  # mark file as downloaded
                        else:
                            print("Item already downloaded!", remote_path)

            os.chdir(working_dir)
            count_msg = "\nTotal files found: {}\nTotal files downloaded: {}\nTotal folders created: {}".format(
                total_file_count, file_count, mk_dir_count)
            print(count_msg)
            logger.info(count_msg.replace("\n", "; ")[2:])
            for item in to_save:
                if item[3] == "file":
                    print(item)
                    local_dest = item[1] + "\\" + item[2][len(item[0]):].replace("/", "\\") + ".!sync"
                    print(local_dest, local_dest[:-len(".!sync")])
                    os.rename(local_dest, local_dest[:-len(".!sync")])  # ## !!!
                logger.debug("Inserting into file_downloaded:", item)
                connection, cursor = DBInteraction().db_opener("settings.db")
                cursor.execute("INSERT INTO file_downloaded VALUES(?, ?, ?, ?, ?)", (item[0], item[1], item[2], item[3],
                                                                                     datetime.now()))
                connection.commit(), connection.close()

        self.purge()
        if not args:
            Interface()

    def purge(self):  # check if this is working properly
        connection, cursor = DBInteraction().db_opener("settings.db")
        cursor.execute("DELETE FROM file_downloaded WHERE date <= DATE('now','-14 day')")
        connection.commit(), connection.close()


class Interface:
    def __init__(self):
        # self.testing()
        # self.delete()
        print("{}\nWelcome to CustomFTPClient!".format("-"*20))
        Input().input_catcher("", "HOMEPAGE", **{"ftp setup": Settings().ftp_setup_interface,
                                                 "path setup": Settings().path_setup_interface,
                                                 "check_dirs": FTPClient().check_dirs,
                                                 "run now": FTPClient().run_now})

    def testing(self):
        connection_, cursor_ = DBInteraction().db_opener("settings.db")
        # cursor_.execute("SELECT * FROM sqlite_master WHERE type='table';")
        cursor_.execute("SELECT * FROM file_downloaded;")
        # [print(item[2]) for item in cursor_.fetchall()]
        print(len(cursor_.fetchall()))
        exit()

    def delete(self):
        connection_, cursor_ = DBInteraction().db_opener("settings.db")
        cursor_.execute("DELETE FROM file_downloaded;")
        connection_.commit()
        [print(item) for item in cursor_.fetchall()]
        exit()


class Input:  # used to help catch certain commands from any input location
    def input_catcher(self, msg, location, *conditions, **catch_action):
        try:
            ca = catch_action.items()
        except IndexError:
            ca = None
        logger.debug("Input Catcher - msg: {}; location: {}, conditions: {}, catch_actions: {}".format(msg, location,
                                                                                                       conditions, ca))
        while True:
            print(msg)
            input_ = input().lower().strip(" ")
            if input_ in catch_action.keys():
                if type(list(catch_action.values())[list(catch_action.keys()).index(input_)]) is list:  # if action is
                    # provided in list format then use all items in list from index 1 onwards as parameters
                    list(catch_action.values())[list(catch_action.keys()).index(input_)][0](
                        *list(catch_action.values())[list(catch_action.keys()).index(input_)][1:])
                else:
                    try:
                        list(catch_action.values())[list(catch_action.keys()).index(input_)]()
                    except TypeError:
                        print("You must provide a name!\n")
                        Interface()
                break
            elif input_.split(" ")[0] in catch_action.keys():
                try:
                    list(catch_action.values())[list(catch_action.keys()).index(input_.split(" ")[0])](
                        input_.split(" ")[1])
                    break
                except IndexError:
                    print("That name does not exist! Perhaps you mistyped it? Please try again. Type HELP for a full "
                          "list of options.\n")
                    Interface()
            elif input_ in ["help", "help here", "/?", "?"]:
                print("You are currently at '{}'".format(location))
                if "here" not in input_:
                    print("\nHere is a list of commands possible at any point in the program:")
                    print("HELP\t-\tThis will bring you to this help page; type HELP HERE for only a list of commands "
                          "specific to location")
                    print("HOME\t-\tAt any time you can always type HOME to go back to the homepage")
                    print("EXIT\t-\tAt any time you can always type EXIT quit the program")
                print("\nHere is a list of commands specific to this location ({}):".format(location))
                if location == "HOMEPAGE":
                    print("FTP SETUP\t\t\t\t\t-\tAdd/Edit/Delete FTP server connection details")
                    print("PATH SETUP\t\t\t\t\t-\tAdd/Edit/Delete paths for FTP connections to be made from")
                    print("CHECK_DIRS [SERVER NAME]\t-\tReturn a list of all items in the directory at the path(s) "
                          "stored for said server. Alternatively, type CHECK_DIRS ALL for all servers.")
                    print("RUN NOW\t\t\t\t\t\t-\tRun FTP now. This will download any undownloaded files to the saved "
                          "locations from all saved FTP locations.")
                if location == "FTP SETUP":
                    print("ADD\t\t\t\t\t\t\t-\tAdd a new FTP server connection settings")
                    print("DELETE [SERVER NAME]\t\t-\tDelete an FTP server connection settings")
                    print("EDIT [SERVER NAME]\t\t\t-\tEdit an FTP server connection settings")
                    print("SHOW [SERVER NAME]\t\t\t-\tShow an FTP server connection settings; type SHOW ALL to show all"
                          " server connection settings")
                if location == "PATH SETUP":
                    print("ADD\t\t\t\t\t\t\t\t-\tAdd a new FTP server connection path")
                    print("DELETE [REMOTE PATH NAME]\t\t-\tDelete an FTP server connection path")
                    print("EDIT [REMOTE PATH NAME]\t\t\t-\tEdit an FTP server connection path")
                    print("SHOW [SREMOTE PATHERVER NAME]\t-\tShow an FTP server connection path; type SHOW ALL to "
                          "show all server connection settings")
            elif input_ == "home":
                print()
                Interface()
            elif input_ == "exit":
                exit()
            else:
                if len(catch_action) == 0:
                    if len(conditions) > 0:
                        cont = True
                        for condition in conditions:
                            if not eval(condition):
                                cont = False
                                print("That is an invalid entry. Please try again.\n")
                                break
                        if cont:
                            return input_
                    else:
                        return input_
                else:
                    print("That is an invalid entry! Type HELP for a list of options.")


class DBInteraction:
    def db_opener(self, database_name, foreign_keys=True):
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        if foreign_keys:
            cursor.execute("PRAGMA foreign_keys = 1")
        return connection, cursor

    def get_downloaded_files_list(self):
        connection, cursor = self.db_opener("settings.db")
        cursor.execute("select name from sqlite_master where type = 'table'")
        cursor.execute("SELECT name FROM file_downloaded")
        file_names = list()
        [file_names.append(item[0]) for item in cursor.fetchall()]
        connection.commit(), connection.close()
        return file_names


if not os.path.isfile("settings.db"):
    logger.info("No database found. Creating database...")
    connection_, cursor_ = DBInteraction().db_opener("settings.db")
    sql_command = """
                CREATE TABLE ftp_settings (
                name VarChar(15) PRIMARY KEY,
                host VarChar(15) NOT NULL,
                username VARCHAR(30) NOT NULL,
                password VARCHAR(30) NOT NULL);
                """
    cursor_.execute(sql_command)
    sql_command = """
                CREATE TABLE path_settings (
                name VarChar(15) NOT NULL,
                remote_path VarChar(255) NOT NULL,
                local_path VarChar(255) NOT NULL,
                    PRIMARY KEY (remote_path, local_path),
                    FOREIGN KEY (name) REFERENCES ftp_settings(name));
                """
    cursor_.execute(sql_command)
    sql_command = """
                    CREATE TABLE file_downloaded (
                    remote_path VarChar(255) NOT NULL,
                    local_path VarChar(255) NOT NULL,
                    name VarChar(255) PRIMARY KEY,
                    path VarChar(255) NOT NULL,
                    date DATE NOT NULL,
                        FOREIGN KEY (remote_path, local_path) REFERENCES path_settings(remote_path, local_path));
                    """
    # FOREIGN KEY (remote_path, local_path) REFERENCES path_settings(remote_path, local_path)
    cursor_.execute(sql_command)
    connection_.commit(), connection_.close()
    logger.info("Database created.")

args = list(sys.argv)
del args[0]

if not args:  # if no arguments are passed then call the interface for user interaction
    Interface()
else:
    if "-auto" in args:
        sys.stdout = open(os.devnull, 'w')  # disable print
        FTPClient().run_now()
