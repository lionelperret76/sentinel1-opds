#!/usr/bin/env python

# Author: Nina Lin

import csv
from urllib.request import urlopen
import shutil
import argparse
import sys
import os
import multiprocessing as mp

def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser(description='Download AWS S1 SLC OPDS by using csv file generated by ASF',
             formatter_class=argparse.RawDescriptionHelpFormatter,
             epilog='''


Example:
    To do 16 parallel downloads (at 16 different processors) at the same time:
    aws_get_s1a.py -i asf_generated.csv -n 16

''')


    parser.add_argument('-i', '--csv_file', type=str, required=True, dest='fcsv',
            help = 'csv file directly out from ASF Vertex')
    parser.add_argument('-n', '--nproc', type=int, required=False, dest='nproc',
            help='number of processor to be used. default: 1')
    if len(sys.argv) < 1:
        print
        parser.print_help()
        print
        sys.exit(1)
    inps = parser.parse_args()
    return inps

def downloadGranule(fullpath):
    url = 'http://sentinel1-slc-seasia-pds.s3-website-ap-southeast-1.amazonaws.com/datasets/slc/v1.1/'+fullpath
    fzip = fullpath.split('/')[-1]
    if os.path.isfile(fzip) == False:
        print("Start downloading "+url)
        with urlopen(url) as response, open(fzip, 'wb') as ofile:
            shutil.copyfileobj(response, ofile)

if __name__ == '__main__':

    inps = cmdLineParse()
    if inps.nproc == None:
        nproc = 1
    else:
        nproc = inps.nproc

    with  open(inps.fcsv, newline='') as csvfile:
        rows = csv.DictReader(csvfile)

        fullpathlist = []
        for row in rows:
            gname = row['Granule Name']
            year  = gname[17:21]
            mm    = gname[21:23]
            dd    = gname[23:25]
            dirpath = str(year)+'/'+str(mm)+'/'+str(dd)+'/'
            fullpath = dirpath+gname+'/'+gname+'.zip'
            fullpathlist.append(fullpath)
    
	pool = mp.Pool(processes=nproc)
    pool.map_async(downloadGranule, fullpathlist, chunksize=1)
    pool.close()
    pool.join()
    print('Parallel download completed!')
