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
            sys.exit()
    else:
        print("Unknown input file type")
        sys.exit()

    if args.diagnostics:
        import h5py
        #test output hdf5 by printing to terminal
        fin = h5py.File(f'{args.fileIn[:-5]}.hdf5', 'r')
        print("Found HDF5 contents: ")
        print(fin.keys())
        print("in METADATA:")
        for i in fin['metadata'].keys():
            print(i)
            print(fin['metadata'][i][()])
        print("in DATA:")
        for j in fin['data'].keys():
            print(j)
            print(fin['data'][j][()])
        print(f"{len(fin['data']['hit_x'])} pixel hit events")

#################
# call to main
#################
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='rootToHdf5',
        description='Convert ROOT output from Allpix-squared to HDF5 file with only NEUROPix-relevant variables retained')
    parser.add_argument('-f', '--fileIn', required=True, help="Path to input ROOT file. Only accepts one file at a time.")    
    parser.add_argument('-o', '--dirOut', default='./', help="Path to output directory where HDF5 will be saved. Defaults to directory where this script lives.")  
    parser.add_argument('-l', '--libAllpixObjects', required=False, help="Path to the libAllpixObjects library (generally in allpix-squared/lib/)) ")
    parser.add_argument('-d','--diagnostics', required=False, action='store_true', help="If given, will run diagnostics on the output HDF5 to confirm that it was created and populated as expected.")

    args = parser.parse_args()
    args.dirOut = functions.outputCheck(args.dirOut)
        
    main(args)