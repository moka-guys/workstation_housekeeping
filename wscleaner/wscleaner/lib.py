#!/usr/bin/env python3
"""lib.py

Utlily classes for the workstation cleaner module.

Classes:
    RunFolder: A local directory containing files with the 'fastq.gz' extension
    DxProjectRunFolder: A DNAnexus project
    RunFolderManager: Contains methods for finding, checking and deleting runfolders in a root directory.
"""
import logging
import shutil
import time
from pathlib import Path

import dxpy


logger = logging.getLogger(__name__)

class RunFolder():
    """A local directory containing files with the 'fastq.gz' extension

    Arguments:
        path (str): The path of a local directory
    Attributes:
        path (Pathlib.Path): A path object created from the input directory
        name (str): The runfolder/directory name
        dx_project (DxProjectRunfolder): A DX Project object
        age (int): Age of the runfolder in days
    Methods:
        find_fastqs: Returns a list of local files with the 'fastq.gz' extension
    """
    def __init__(self, path):
        self.logger = logging.getLogger(__name__ + '.RunFolder')
        self.path = Path(path)
        self.name = self.path.name
        self.logger.debug(f'Initiating RunFolder instance for {self.name}')
        self.dx_project = DxProjectRunFolder(self.name)

    @property
    def age(self):
        """Returns runfolder age in days"""
        age_in_seconds = time.time() - self.path.stat().st_mtime
        age_in_days = age_in_seconds // (24 * 3600)
        self.logger.debug(f'{self.name} age is {age_in_days}')
        return age_in_days

    def find_fastqs(self, count=False):
        """Returns a list or count of local files with the 'fastq.gz' extension
        Args:
            count(bool): Returns number of fastqs if True.
        """
        # Find paths of files with fastq.gz extension
        fastq_paths = self.path.rglob('*.fastq.gz')
        # Sort fastq filenames for cleaner logfile outputs
        fastq_filenames_unsorted = [ path.name for path in fastq_paths ]
        fastq_filenames = sorted(fastq_filenames_unsorted)
        # Return number of fastqs if count is True, otherwise return fastq file names
        if count:
            self.logger.debug(f'{self.name} contains {len(fastq_filenames)} fastq files')
            return len(fastq_filenames)
        else:
            self.logger.debug(f'{self.name} contains {len(fastq_filenames)} fastq files: {fastq_filenames}')
            return fastq_filenames


class DxProjectRunFolder():
    """A DNAnexus project.

    Arguments:
        runfolder_name (str): The name of a local runfolder    
    Attributes:
        runfolder (str): Runfolder name
        id (str): Project ID of the matching runfolder project in DNANexus.
    Methods:
        find_fastqs: Returns a list of files in the DNAnexus project (self.id) with the fastq.gz extension
        count_logfiles: Count logfiles in the DNAnexus project (self.id). Logfiles are in an expected location
    """
    def __init__(self, runfolder_name):
        self.logger = logging.getLogger(__name__ + '.DXProjectRunFolder')
        self.runfolder = runfolder_name
        self.id = self.__dx_find_one_project()

    def find_fastqs(self):
        """Returns a list of files in the DNAnexus project (self.id) with the fastq.gz extension"""
        # Search dnanexus for files with the fastq.gz extension.
        # name_mode='regexp' tells dxpy to look for any occurence of 'fastq.gz' in the filename
        search_response = dxpy.find_data_objects(
            project=self.id, classname='file', name='fastq.gz', name_mode='regexp'
            )
        file_ids = [ result['id'] for result in search_response ]
        
        # Gather a list of uploaded fastq files with the state 'closed', indicating a completed upload.
        fastq_filenames_unsorted = []
        for dx_file in file_ids:
            file_description = dxpy.describe(dx_file)
            if file_description['state'] == 'closed':
                fastq_filenames_unsorted.append(file_description['name'])
        # Sort fastq filenames for cleaner logfile output
        fastq_filenames = sorted(fastq_filenames_unsorted)
        self.logger.debug(f'{self.id} contains {len(fastq_filenames)} "closed" fastq files: {fastq_filenames}')
        return fastq_filenames
    
    def count_logfiles(self):
        """Count logfiles in the DNAnexus project (self.id). Logfiles are in an expected location.
        Returns:
            logfile_count (int): A count of logfiles"""
        # Set uploaded runfolder name. Runfolder is renamed upon upload to the DNANexus project
        # without the first four characters
        uploaded_runfolder = dxpy.describe(self.id)['name'][4:]
        # Set logfile location in DNANexus project. This is expected in 'Logfiles/', a subdirectory of the uploaded runfolder 
        logfile_dir = str(Path('/',uploaded_runfolder,'Logfiles'))
        logfile_list = dxpy.find_data_objects(project=self.id, folder=logfile_dir, classname='file')
        logfile_count = len(list(logfile_list))
        return logfile_count

    def __dx_find_one_project(self):
        """Find a single DNAnexus project from the input runfolder name

        Returns:
            A DNAnexus project ID. If the search fails, returns None.
        """
        try:
            # Search for the project matching self.runfolder.
            # name_mode='regexp' - look for any occurence of the runfolder name in the project name.
            # Setting more_ok/zero_ok to False ensures only one project is succesfully returned.
            project = dxpy.find_one_project(name=self.runfolder, name_mode='regexp', more_ok=False, zero_ok=False)
            self.logger.debug(f'{self.runfolder} DNAnexus project: {project["id"]}')
            return project['id']
        except dxpy.exceptions.DXSearchError:
            # Catch exception and raise none
            self.logger.debug(f'0 or >1 DNAnexus projects found for {self.runfolder}')
            return None
    
    def __bool__(self):
        """Allows boolean expressions on class instances which return True if a single DNAnexus project was found."""
        if self.id:
            return True
        else:
            return False

class RunFolderManager():
    """Contains methods for finding, checking and deleting runfolders in a root directory.

    Args:
        directory (str): A parent directory containing runfolders to process
        dry_run (bool): Do not delete directories
    Attributes:
        root(pathlib.Path): A path object to the root directory
        deleted(List): A list of deleted runfolders populated by calls to self.delete()
    Methods:
        find_runfolders(): Search the parent directory for subdirectories containing fastq.gz files.
            Returns wscleaner.lib.RunFolder objects.
        check_fastqs(): Returns true if a runfolder's fastq.gz files match those in it's DNAnexus project.
        check_logfiles(): Returns true if a runfolder's DNAnexus project contains 6 logfiles in the
            expected location
        delete(): Delete the local runfolder from the root directory and append name to self.deleted.
    Raises:
        __validate():ValueError: The directory passed to the class instance does not exist.
    """
    def __init__(self, directory, dry_run=False):
        self.logger = logging.getLogger(__name__ + '.RunFolderManager')
        self.__validate(directory)
        self.root = Path(directory)
        self.__dry_run = dry_run
        self.deleted = [] # Delete runfolders appended here by self.deleted

    def __validate(self, directory):
        """Check that input directory exists. Log and raise error if otherwise."""
        try:
            assert Path(directory).is_dir()
        except AssertionError:
            self.logger.error(f'Directory does not exist: {directory}', exc_info=True)
            raise

    def find_runfolders(self, min_age=None):
        """Search the parent directory for subdirectories containing fastq.gz files.
        Args:
            min_age(int): Minimum age in days of runfolders returned.
        Returns:
            runfolder_objects(list): List of wscleaner.lib.RunFolder objects.
        """
        subdirectories = self.root.iterdir()
        runfolder_objects = []
        for directory in subdirectories:
            rf = RunFolder(directory)
            # Criteria for runfolder: Older than or equal to min_age and contains fastq.gz files
            if (rf.age >= min_age) and (rf.find_fastqs(count=True) > 0):
                self.logger.debug(f'{rf.name} IS RUNFOLDER.')
                runfolder_objects.append(rf)
            else:
                self.logger.debug(f'{rf.name} IS NOT RUNFOLDER.')
        return runfolder_objects

    def check_fastqs(self, runfolder):
        """Returns true if a runfolder's fastq.gz files match those in it's DNAnexus project."""
        dx_fastqs = runfolder.dx_project.find_fastqs()
        local_fastqs = runfolder.find_fastqs()
        fastq_bool = all([fastq in dx_fastqs for fastq in local_fastqs])
        self.logger.debug(f'{runfolder.name} FASTQ BOOL: {fastq_bool}')
        return fastq_bool
    
    def check_logfiles(self, runfolder):
        """Returns true if a runfolder's DNAnexus project contains 6 logfiles in the
            expected location"""
        dx_logfiles = runfolder.dx_project.count_logfiles()
        logfile_bool = dx_logfiles >= 6
        self.logger.debug(f'{runfolder.name} LOGFILE BOOL: {logfile_bool}')
        return logfile_bool
    
    def delete(self, runfolder):
        """Delete the local runfolder from the root directory and append name to self.deleted."""
        if self.__dry_run:
            self.logger.info(f'DRY RUN DELETE {runfolder.name}')
        else:
            self.deleted.append(runfolder.name)
            shutil.rmtree(runfolder.path)
            self.logger.info(f'{runfolder.name} DELETED.')
