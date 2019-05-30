"""generate.py

Generates dummy data for testing.
"""

import pathlib

def data_test_runfolders():
    """A fixture that returns a list of tuples containing (runfolder_name, fastq_list_file)."""
    return [
        ('190408_NB551068_0234_AHJ7MTAFXY_NGS265B', 'test/test_dir_1_fastqs.txt'),
        ('190410_NB551068_0235_AHKGMGAFXY_NGS265C', 'test/test_dir_2_fastqs.txt')
        ]

def create_test_dirs(test_data):
    """Create test data for testing.
    
    This is an autouse fixture with session scope, meaning it is run once before any tests are collected.
    """  
    for runfolder_name, fastq_list_file in test_data:
        # Create the runfolder directory as per Illumina spec
        test_path = f'test/data/{runfolder_name}/Data/Intensities/BaseCalls'
        pathlib.Path(test_path).mkdir(parents=True, exist_ok=True)
        # Generate empty fastqfiles in runfolder
        with open(fastq_list_file) as f:
            fastq_list = f.read().splitlines()
            for fastq_file in fastq_list:
                pathlib.Path(test_path, fastq_file).touch(mode=777, exist_ok=True)

create_test_dirs(data_test_runfolders())