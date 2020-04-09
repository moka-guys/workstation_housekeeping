# Workstation Cleaner Design Document

Owner: Nana Mensah
Date: 30/05/19
Status: Draft

## Brief

The Viapath Genome Informatics team use a linux workstation to manage sequencing files. These files are uploaded to the DNAnexus service for storage, however clearing the workstation is time intensive.

## User Story

As a Clinical Bioinformatician, I need to automate the deletion of sequencing folders that have been successfuly backed up, so that I can free up time for other duties.

## Functional requirements

FR1. Accurately detect sequencing folders have been successfully backed up
FR2. Delete old sequencing folders that are successfully backed up
FR3. Log all activity to a local logfile

## Non-functional requirements

NF1. Run from the Linux command line
NF2. Process runfolders within 24 hours
NF3. Use any available DNAnexus SDKs
NF4. Attempt to process all folders at least once

## Design Summary

A RunFolderManager class will instatiate objects for local Runfolders, each of which has an associated DNA Nexus project object. The manager loops over the runfolders and deletes them if all checks pass.

DNA Nexus projects are accessed with the dxpy module, a python wrapper for the DNA Nexus API.
