#!/usr/bin/env python3

# Processing the JSON files in this folder
# Chris Cheng 2019

import os
import os.path as op
import json
import csv
import re
import datetime
import time

import sys
from optparse import OptionParser, Option
from glob import glob

# FILE PATHS TO BE ESTABLISHED
bids_subject = 'qa'
bids_ds_path = op.join('data', 'QA')

mriqc_path = op.join(bids_ds_path, 'derivatives', 'mriqc', 'derivatives')
ses_path = op.join(bids_ds_path, 'sub-qa', 'ses-*')


def get_opt_parser():
    # use module docstring for help output
    p = OptionParser()

    p.add_options([
        Option("-o", "--output",
               dest="output_csv",
               #required=True,
               help="Where do you want the extraction to be written to"),

        Option("-t", "--type",
               dest="type", default="func",
               help="Is the final an anat or func?"),

    ])

    return p


def seconds(input):
    x = time.strptime(input.split('.')[0],'%H:%M:%S')
    return int(datetime.timedelta(hours = x.tm_hour, minutes = x.tm_min, seconds = x.tm_sec).total_seconds())


def qa_metric_producer(source, output_csv):
    
    # opening destination CSV file
    destination = open(output_csv, "a")

    # fires up the CSV writer module
    product = csv.writer(destination)
    
    # WRITES THE HEADER ROW for the CSV
    product.writerow(["Date", "sid", "ses", "Filetype", "tsnr", "SAR", "AcquisitionTime", "TxRefAmp", "SoftwareVersions", "CSV", "RepetitionTime", 
        "Shim1", "Shim2", "Shim3", "Shim4", "Shim5", "Shim6", "Shim7", "Shim8", "IOPD1", "IOPD2", "IOPD3", "IOPD4", "IOPD5", "IOPD6"])

    for item in source:  # os.listdir(os.fsencode("derivatives")):          # for each
        info = re.search('.*/ses-(?P<date>[0-9]+)/.*', item).groupdict()
        ses = re.search('.*?ses-(?P<ses>[\w]+)_.*', item).groupdict()       # getting session id
        sid = re.search('.*?sid-(?P<sid>[0-9]+)_.*', item).groupdict()      # getting subject id

        # merging dicts for easy access
        info.update(ses)
        info.update(sid)
       
        # FUNC: abbreviations for easier access to certain dicts in the func/.json files
        func_json = open(os.fsdecode(item), "r").read()  # open sesameeee
        loaded_func = json.loads(func_json)
        func_bids = loaded_func["bids_meta"]
        shim = func_bids["ShimSetting"]
        IOPD = func_bids["ImageOrientationPatientDICOM"]

        # ANAT: modifying the func code to access the anatomical JSON
#        if int(info["date"]) >= 20171030:
#            anat_item = str(item)
#            anat_item = anat_item[:34] + "anat" + anat_item[38:]
#            anat_item = anat_item[:59] + "acq-MPRAGE_T1w.json"
            
#            print(anat_item)
            
#            anat_json = open(os.fsdecode(anat_item), "r").read()
#            loaded_anat = json.loads(anat_json)

        print(item); # debugging, indicator that a file's been processed

        # 2018 and later conditions
        if 'SAR' and "AcquisitionTime" and "TxRefAmp" in loaded_func:
            product.writerow([info["date"], info["sid"], info["ses"],
                os.fsdecode(item)[59:], loaded_func["tsnr"], loaded_func["SAR"],
                seconds(loaded_func["AcquisitionTime"]), loaded_func["TxRefAmp"], func_bids["SoftwareVersions"],
                func_bids["ConversionSoftwareVersion"], func_bids["RepetitionTime"], 
                shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7], IOPD[0], IOPD[1], IOPD[2], IOPD[3], IOPD[4], IOPD[5]])

        # pre 2018 conditions, DOESN'T have TxRefAmp and different location for the other parameters
        else:
            if 'tsnr' in loaded_func and 'SAR' and 'AcquisitionTime' and 'TxRefAmp' in func_bids:
                content = [info["date"], info["sid"], info["ses"], os.fsdecode(item)[59:], loaded_func['tsnr'], func_bids["SAR"],
                    seconds(func_bids["AcquisitionTime"]), func_bids['TxRefAmp'], func_bids["SoftwareVersions"],
                    func_bids["ConversionSoftwareVersion"], func_bids["RepetitionTime"], 
                    shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7],
                    IOPD[0], IOPD[1], IOPD[2], IOPD[3], IOPD[4], IOPD[5]] 
                
                if int(info["date"]) < 20171030:
                    product.writerow(content)
                else:
                    product.writerow(content)
            else:
                print("tsnr, SAR or TxRefAmp are not present.")

    destination.close()


def anat_metric_producer(source, output_csv):
    
    # opening destination CSV file
    destination = open(output_csv, "a")

    # fires up the CSV writer module
    product = csv.writer(destination)
    
    # WRITES THE HEADER ROW for the CSV
    product.writerow(["Date", "sid", "ses", "Filetype", "snr_total", "SAR", "AcquisitionTime", "TxRefAmp", "SoftwareVersions", "CSV", "RepetitionTime", 
        "Shim1", "Shim2", "Shim3", "Shim4", "Shim5", "Shim6", "Shim7", "Shim8", "IOPD1", "IOPD2", "IOPD3", "IOPD4", "IOPD5", "IOPD6"])

    for item in source:  # os.listdir(os.fsencode("derivatives")):          # for each 
        info = re.search('.*?ses-(?P<date>[0-9]+).*', item).groupdict()
        ses = re.search('.*?ses-(?P<ses>[\w]+)_.*', item).groupdict()       # getting session id
        sid = re.search('.*?sid(?P<sid>[0-9]+)_.*', item).groupdict()      # getting subject id

        # merging dicts for easy access
        info.update(ses)
        info.update(sid)

        # FUNC: abbreviations for easier access to certain dicts in the func/.json files
        func_json = open(os.fsdecode(item), "r").read()  # open sesameeee
        loaded_func = json.loads(func_json)
        func_bids = loaded_func["bids_meta"]
        shim = func_bids["ShimSetting"]
        IOPD = func_bids["ImageOrientationPatientDICOM"]

        print(item); # debugging, indicator that a file's been processed

        # 2018 and later conditions
        if 'SAR' and "AcquisitionTime" and "TxRefAmp" in func_bids:
            product.writerow([info["date"], "sub-sid" + info["sid"], info["ses"], 
                os.fsdecode(item)[59:], loaded_func["snr_total"], func_bids["SAR"],
                seconds(func_bids["AcquisitionTime"]), func_bids["TxRefAmp"], func_bids["SoftwareVersions"],
                func_bids["ConversionSoftwareVersion"], func_bids["RepetitionTime"], 
                shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7],
                IOPD[0], IOPD[1], IOPD[2], IOPD[3], IOPD[4], IOPD[5]])
        
        # pre 2018 conditions, DOESN'T have TxRefAmp and different location for the other parameters
        else:
            if 'snr_total' in loaded_func and 'SAR' and 'AcquisitionTime' and 'TxRefAmp' in func_bids:
                content = [info["date"], "sub-sid" + info["sid"], info["ses"], 
                        os.fsdecode(item)[59:], func_bids['snr_total'], func_bids["SAR"],
                    seconds(func_bids["AcquisitionTime"]), func_bids['TxRefAmp'], func_bids["SoftwareVersions"],
                    func_bids["ConversionSoftwareVersion"], func_bids["RepetitionTime"], 
                    shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7],
                    IOPD[0], IOPD[1], IOPD[2], IOPD[3], IOPD[4], IOPD[5]] 
                
                if int(info["date"]) < 20171030:
                    product.writerow(content)
                else:
                    content.append(loaded_anat["snr_total"])
                    product.writerow(content)
            else:
                print("snr_total, SAR or TxRefAmp are not present.")

    destination.close()


def main(args=None):
    parser = get_opt_parser()

    (options, source) = parser.parse_args(args)

    if options.type == "func":
        qa_metric_producer(source, options.output_csv)
    elif options.type == "anat":
        anat_metric_producer(source, options.output_csv)
    else:
        print("TYPE provided MUST be either anat or func")


if __name__ == '__main__':
    main()
