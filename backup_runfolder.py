#!/usr/bin/env python3
"""backup_runfolder

Uploads an Illumina runfolder to DNANexus.

Example:
    usage: backup_runfolder.py [-h] -i RUNFOLDER -a AUTH [--ignore IGNORE] [-p PROJECT]
                               [--logpath LOGPATH]
    where IGNORE is a comma seperated string of terms which prevents the upload of files if that term is present in the filename or filepath.
"""

import argparse
import re
import os
import sys
import subprocess
from distutils.spawn import find_executable
import math

import logging
from logging.config import dictConfig

def log_setup(args):
    """Set up script logging object.
    Logs are written to STDERR and appended to a logfile, named after the input runfolder.
    Create loggers by assigning logging.getLogger('<name>') objects. Call using desired log level
    as method. Formatter objects define the format of the log string, while Handler objects dictate
    where the log is recorded. See the 'logging' module docs in the standard library for detail.

    Logs can be written with different levels, in order of event severity: DEBUG, INFO, WARNING, ERROR,
    CRITICAL. Each has a corresponding method that can be used to log events at that level of severity.
    Logs are written by passing a string to one of these methods (see example below).

    An example of the logging protocol:
        # Create logging object. This can be performed anywhere in the script once config created.
        logger = logging.getLogger('backup_runfolder')
        # Write to log with level 'INFO'
        logger.info('Searching for executables...')
    >>> 2018-11-06 10:11:30,071 backup_runfolder INFO - Searching for executables...
    """
    # If logfile path passed to --logpath, prepend to logfile name, else write to current directory
    logpath = args.logpath if args.logpath else ""
    # Set logfile name as runfolder name with '.log' extension
    logfile_name = "".join([os.path.basename(args.runfolder), ".log"])
    logfile_fullpath = os.path.join(logpath, logfile_name)

    # Create dictionary with logging config parameters.
    # Loggers can be configured explicitly through code, config files, or the dictConfig module. Here,
    # a dictionary is created to define a logger the writes messages to both the terminal (logging.StreamHandler,
    # which writes to STDERR) and a logfile (logging.FileHandler, set to 'runfoldername.log', prefxied with
    # a path if --logpath given at the command line). These parameters are added to a root logger,
    # from which all future loggers in the module, initiated with logging.getLogger, will inherit.
    logging_config = dict(
        version=1.0,
        formatters={'log_formatter': {'format': "{asctime} {name} {levelname} - {message}", 'style': '{'}},
        handlers={
            'stream_handler': {'class': 'logging.StreamHandler', 'formatter': 'log_formatter', 'level': logging.DEBUG},
            'file_handler': {'class': 'logging.FileHandler', 'formatter': 'log_formatter', 'level': logging.DEBUG,
                             'filename': os.path.join(logpath, logfile_name)}},
        root={'handlers': ['file_handler'], 'level': logging.DEBUG}
        )

    # Read the logging config and initaite root logger for the script.
    dictConfig(logging_config)
    # Log the beginning of the script with the root logger.
    logging.info('START. Logging to %s', logfile_fullpath)

def cli_arguments(args):
    """Parses command line arguments.
    Args:
        args: A list containing the expected commandline arguments. Example:
            ['backup_runfolder.py', '-i', 'media/data1/share/180216_M02353_0185_000000000-D357Y/', '-a',
             'AUTH_TOKEN', '-p', '003_180924_TrioPipelineGATK', '--ignore', '.txt']
    Returns:
        An argparse.parser object with methods named after long-option command-line arguments. Example:
            --runfolder "media/data1/share/runfolder" --> parser.parse_args(args).runfolder
    """
    # Define arguments.
    parser = argparse.ArgumentParser()
    # The runfolder string argument is immediately passed to os.path.expanduser using the *type* argument, and this
    # value is contained as the .runfolder() method in the object returned by parser.parser_args().
    # Os.path.expanduser allows expands tilde signs (~) to a string containing the user home directory.
    parser.add_argument('-i', '--runfolder', required=True, help='An Illumina runfolder directory', type=os.path.expanduser)
    parser.add_argument('-a', '--auth-token', help='A string or file containing a DNAnexus authorisation key used to access the DNANexus project. Default = ~/.dnanexus_auth_token', default='~/.dnanexus_auth_token', type=os.path.expanduser)
    parser.add_argument('--ignore', default=None, help="Comma-separated list of patterns which prevents the file from being uploaded if any pattern is present in filename or filepath.")
    # Note: When no project is given to the -p argument below, this script searches for a project in DNAnexus. See UAcaller.find_nexus_project() for details.
    parser.add_argument('-p', '--project', default=None, help='The name of an existing DNAnexus project for the given runfolder')
    parser.add_argument('--logpath', help='Logfile output directory', type=os.path.expanduser)
    # Collect arguments and return
    return parser.parse_args(args)

def find_executables(programs):
    """Check programs (input arguments) exist in system path.
    Args:
        programs - A list of executeable program names. E.g. ['dx','ua'] - these are commands that
            would execute on the command line.
    """
    logger = logging.getLogger('backup_runfolder.find_executables')
    # all() returns True if all items in a list evaluate True. Used here to raise error if any calls
    # to find_executable() fail. This function uses the distutils.spawn.find_executable package to
    # assert the programs are callable by parsing the directories in the system PATH variable (i.e. bash `which` command).
    if not all([find_executable(program) for program in programs]):
        logger.exception('Could not find one of the following programs: %s', programs)
    else:
        logger.info('Found programs: %s', ",".join(programs))

class UAcaller():
    """Uploads a runfolder to DNA Nexus.
    Attributes:
        runfolder: Runfolder path as given on command line
        runfolder_name: The name of the runfolder without parent directories
        auth_token: DNAnexus api key. Passed as string or filename argument.
        project: DNAnexus project corresponding to the input runfolder
        ignore: A comma-separated string of regular expressions. Used to skip files for upload.
        logger: Class-level logger object

    Methods:
        find_nexus_project(project): Searches DNAnexus for a project matching the input. If the
           input argument is 'None', searches for the first project matching self.runfolder.
        call_upload_agent(): Calls the DNAnexus upload agent using the class attributes
    """
    def __init__(self, runfolder, auth_token, project, ignore):
        # Initiate class-lvel logging object. This object inherits from any root loggers defined using
        # the python logging module. All subsequent calls to self.logger will log as per the root configuration.
        self.logger = logging.getLogger('backup_runfolder.UAcaller')

        # Set runfolder directory path strings
        # Get the full (absolute) path of the input runfolder with os.path.abspath
        self.runfolder = os.path.abspath(runfolder)
        # Check runfolder exists
        if not os.path.isdir(self.runfolder):
            raise IOError('Invalid runfolder given as input')
        self.runfolder_name = os.path.basename(self.runfolder)

        # Set DNAnexus authentication token from input. This function will distinguish between a file or
        # string provided as an argument. If not provided, the crednetials file in the home directory is used.
        self.auth_token = self.read_auth_token(auth_token)
        # Set DNAnexus project. If no project given, search DNAnexus for a project matching the runfolder name.
        self.project = self.find_nexus_project(project)
        # List of patterns to exclude files from upload
        self.ignore = ignore


    def read_auth_token(self, key_input):
        """Return the DNAnexus authentication toxen from the first line of an input file or an input string.
        Args:
            key_file_string: A file or string containing a DNAnexus authentication key."""
        self.logger.info('Reading authentication token...')
        # Attempt to read the auth key from the first line of the input, assuming it is a file
        try:
            with open(key_input, "r") as infile:
                auth_token = infile.readlines()[0].strip()
        # If the file does not exist, use the input auth key as provided
        except FileNotFoundError:
            auth_token = key_input.strip()
        return auth_token

    def find_nexus_project(self, project):
        """Search DNAnexus for the project given as an input argument. If the input is 'None',
        searches for a project matching self.runfolder.
        Args:
            project: The name of a project on DNAnexus. If None, searches using runfolder name.
        """
        self.logger.info('Searching for DNAnexus project...')
        # Get list of projects from DNAnexus as a string. Due to python3's default use of bytestrings
        # from various modules, bytes.decode() must be called to return the output as a pyton str object.
        # This is required for pattern matching with the re module.
        projects = subprocess.check_output(['dx', 'find', 'projects', '--auth',self.auth_token]).decode()
        print(projects)
        # Set the regular expression pattern for asserting that the project exists in DNAnexus.
        # The bytes() function is required to create bytestrings
        if project is None:
        # If no project given, search for one or more word character, using \w+ ([a-zA-Z0-9_]),
        # either side of the runfolder name given to the class
            pattern = r'(\w*{}\w*)'.format(self.runfolder_name)
        else:
        # Else, search for the exact project name passed to the function
            pattern = r'({})'.format(project)

        # List all strings captured by the regular expression pattern defined to match the project
        project_matches = re.findall(pattern, projects)

        # If only one project is found, return this value
        if len(project_matches) == 1:
            return project_matches[0]
        # Else if any other number of matching projects is foud, log this event and raise an Error
        else:
            self.logger.error('DNAnexus projects found: %s', project_matches)
            self.logger.error('%s matching DNAnexus projects were found for pattern: %s. '\
                'Repeat script by giving explicit project to -p/--project flag', len(project_matches), pattern)
            raise ValueError('Invalid DNAnexus project name. 0 or >1 matching projects found.')

    def get_nexus_filepath(self, folder_path):
        """
        To recreate the directory structure in DNA Nexus need to take relative path of each the subfolder.
        This subfolder path is prefixed with the top level folder in DNA Nexus(the project name without the first four characters (002_)).
        Returns a tuple (DNAnexus upload folder path, full DNAnexus file path)
        DNAnexus upload folder path is used in the upload agent's '--folder' argument.
        Args:
            folder_path - The path of a local folder containing files to be uploaded to DNAnexus.
        Returns:
            A tuple: (DNAnexus upload folder path, full DNAneuxs file path)
        Example:
            self.get_nexus_filepath('/media/data1/share/runfolder/RTALogs/')
            >>> (runfolder/RTALogs, PROJECT:/runfolder/RTALogs/)
        """
        # Clean the runfolder name and parent folders from the input file path. Features of the regular expression below:
        #    {} - Replaced with the runfolder name by call to str.format(self.runfolder)
        #    [\/] - Looks a forward or backward slash in this position, accounting for linux or windows filesystems
        #    (.*)$ - Capture all characters to the end of the line.
        #    Parentheses in regular expressions capture a group, the first of which can be returned from re.search().group(1)
        # if we are uploading files in the root of a runfolder need to skip this step
        if folder_path == self.runfolder:
            clean_runfolder_path = ""
        else:
            clean_runfolder_path = re.search(r'{}[\/](.*)$'.format(self.runfolder), folder_path).group(1)
            
        # Prepend the nexus folder path to cleaned path. the nexus folder path is the project name without the first four characters (002_).
        nexus_path = "'/" + os.path.join(self.project[4:],clean_runfolder_path) + "'"
        
        # Return the nexus folder and full project filepath
        return nexus_path, "{}:{}".format(self.project, nexus_path)
    
    def ignore_file(self,filepath):
        # if an ignore pattern was specified
        if self.ignore:
            # split this string on comma and loop through list
            for pattern in self.ignore.split(","):
                # make ignore pattern and filepath upper case and search filepath for the pattern
                if pattern.upper() in filepath.upper(): 
                    # if present return True to indicate the file should not be uploaded
                    return True
        # if no search patterns given, or pattern not found in filepath return False to say file can be uploaded
        return False
        

    def call_upload_agent(self):
        """
        Loop through the runfolder and build the upload agent command.
        It is quicker to upload files in paralell so all files in a folder are added to a list and a single command issued per folder
        """
        # create a dictionary to hold the directories as a key, and the list of files as the value
        file_dict = {}
        # walk through run folder
        for root, subfolders, files in os.walk(self.runfolder):
            # for any subfolders
            for folder in subfolders:
                # build path to the folder
                folderpath = os.path.join(root, folder)
                # create a dictionary entry for this folder
                file_dict[folderpath] = []
                # create a list of filepaths for all files in the folder
                filepath_list = [os.path.join(folderpath,file) for file in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath, file))]
                # loop through this list
                for filepath in filepath_list:
                    # test filepath for ignore patterns
                    if not self.ignore_file(filepath):
                        # if ignore pattern not found add filepath to list
                        file_dict[folderpath].append(filepath)
    
        # report the folders and files to be uploaded
        self.logger.info('Files for upload: %s', file_dict)

        # call upload agent on each folder
        for path in file_dict:
            # if there are any files to upload
            if file_dict[path]:
                # create the nexus path for each dir
                nexus_path, project_filepath = self.get_nexus_filepath(path)
                self.logger.info('Calling upload agent on %s to location %s', path, project_filepath)
                # upload agent has a max number of uploads of 1000 per command
                # count number of files in list and divide by 500.0 eg 20/500.0 = 0.04. ceil rounds up to the nearest integer (0.04->1). If there are 500, ceil(500/500.0)=1.0 if there are 750 ceil(750/500.0)=2.0
                iterations_needed = math.ceil(len(file_dict[path]) / 500.0)
                # set the iterations count to 1
                iteration_count = 1
                # will pass a slice of the file list to the upload agent so set variables for start and stop so it uploads files 0-999
                start = 0
                stop = 500
                # while we haven't finished the iterations
                while iteration_count <= iterations_needed:
                    # if it's the last iteration, set stop == length of list so not to ask for elements that aren't in the list  (if 4 items in list len(list)=4 and slice of 0:4 won't miss the last element)
                    if iteration_count == iterations_needed:
                        stop = len(file_dict[path])
                    self.logger.info('uploading files %d to %d', start, stop)
                    # the upload agent command can take multiple files seperated by a space. the full file path is required for each file
                    files_string = ""
                    # take a slice of list using from and to
                    for file in file_dict[path][start:stop]:
                        files_string = files_string + " '" + os.path.join(path, file) + "'"
                    
                    # increase the iteration_count and start and stop by 1000 for the next iteration so second iteration will do files 1000-1999 
                    iteration_count += 1
                    start += 500
                    stop += 500

                    # Create DNAnexus upload command
                    nexus_upload_command = ('ua --auth-token {auth_token} --project {nexus_project} --folder {nexus_folder} --do-not-compress --upload-threads 10 --tries 100 {files}'.format(
                        auth_token=self.auth_token, nexus_project=self.project, nexus_folder=nexus_path, files=files_string))

                    # Mask the autentication key in the upload command and log
                    masked_nexus_upload_command = nexus_upload_command.replace(self.auth_token, "")
                    self.logger.info(masked_nexus_upload_command)
                    # Call upload command redirecting stderr to stdout
                    proc = subprocess.Popen([nexus_upload_command], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
                    # Capture output streams (err is redirected to out above)
                    (out, err) = proc.communicate()
                    # Write output stream to logfile and terminal
                    self.logger.debug(out.decode())


def main(args):
    """Uploads runfolder to DNAnexus by passing given arguments to the DNAnexus upload agent."""
    # Get command line arguments
    parsed_args = cli_arguments(args)
    # Set up logger
    log_setup(parsed_args)
    logger = logging.getLogger('backup_runfolder')
    logger.info('Parsed args: %s', args)

    # Check DNAnexus utilities exist in system path.
    logger.info('Searching for executables...')
    find_executables(['ua', 'dx'])

    # Create an object to set up the upload agent command
    logger.info('Creating UAcaller object with the following arguments: %s', vars(parsed_args))
    ua_object = UAcaller(runfolder=parsed_args.runfolder, project=parsed_args.project, auth_token=parsed_args.auth_token, ignore=parsed_args.ignore)
    # Call upload agent on runfolder
    logger.info('Arguments read to object. Calling upload agent for input files.')
    ua_object.call_upload_agent()

    logger.info('END.')

if __name__ == '__main__':
    main(sys.argv[1:])
