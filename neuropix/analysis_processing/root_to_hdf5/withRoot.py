#######################
#
#   Run like:
#       
#   Input = 
#
#   Output =
#
#######################

import sys, argparse
import functions

import h5py

#################
# methods
#################

#################
# main
#################

def main(args):

    print("Reading input")
    #read input file
    if args.fileIn[-4:]=='root':
        print("Converting ROOT to HDF5")
        hdf_success = functions.rootToHDF5(args.fileIn, lib_path=args.libAllpixObjects)
        if hdf_success:
            print("Created output HDF5 file")
        else:
            print("Error occured with HDF5 conversion")
    else:
        print("Unknown input file type")
        sys.exit()

    #test output hdf5
    fin = h5py.File(f'{args.fileIn[:-5]}.hdf5', 'r')
    print(fin.keys())
    print(fin['metadata'].keys())
    print(fin['data'].keys())
    for i in fin['metadata'].keys():
        print(fin['metadata'][i][()])

#################
# call to main
#################
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='rootToHdf5',
        description='Convert ROOT output from Allpix-squared to HDF5 file with only NEUROPix-relevant variables retained')
    parser.add_argument('-f', '--fileIn', default='./gamma_50kev_100k.root')    
    parser.add_argument('-o', '--dirOut', default='./')  
    parser.add_argument("-l", '--libAllpixObjects', required=False,
                    help="specify path to the libAllpixObjects library (generally in allpix-squared/lib/)) ")

    args = parser.parse_args()
    args.dirOut = functions.outputCheck(args.dirOut)
        
    main(args)