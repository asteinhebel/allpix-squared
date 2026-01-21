import ROOT
import uproot as up
import awkward as ak
import numpy as np 
import os
import h5py
from particle import Particle

def outputCheck(directory_name):
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    if directory_name[-1]!='/':
        directory_name+='/'
    return directory_name

def get_allpixLib(lib_path):
    #get allpix library
    if lib_path is not None:  # Try to find Allpix Library
        lib_file_name = (str(lib_path))
        if (not os.path.isfile(lib_file_name)):
            print("WARNING: ", lib_file_name, " does not exist, exiting")
            exit(1)
    elif os.path.isfile(os.path.abspath(os.path.join(__file__ ,"..","..","opt","allpix-squared","lib","libAllpixObjects.so"))): # For native installs
        lib_file_name = os.path.abspath(os.path.join(__file__ ,"..","..","opt","allpix-squared","lib","libAllpixObjects.so"))
    elif os.path.isfile(os.path.join(os.path.sep, "opt","allpix-squared","lib","libAllpixObjects.so")): # For Docker installs
        lib_file_name = os.path.join(os.path.sep, "opt","allpix-squared","lib","libAllpixObjects.so")
    else:
        print("WARNING: No Allpix Objects Library found, exiting")
        exit(1)

    #load library
    ROOT.gSystem.Load(lib_file_name)

def getMetadata_fromRoot(hdf_out, config_dir):

    #create hdf5 group
    metadata_group = hdf_out.create_group("metadata")

    #Pull metadata variables and insert into metadata dataset. ROOT contents are type cppyy.gbl.std.string
    number_of_events_dataset = metadata_group.create_dataset("number_of_events", (1,), data=float(str(config_dir.Get('Allpix').Get('number_of_events'))))
    number_of_particles_dataset = metadata_group.create_dataset("number_of_particles", (1,), data=float(str(config_dir.Get('DepositionGeant4').Get('number_of_particles'))))
    particle_type_dataset = metadata_group.create_dataset("particle_type", (1,), data=str(config_dir.Get('DepositionGeant4').Get('particle_type')))
    source_energy_value_dataset = metadata_group.create_dataset("source_energy_value", (1,), data=float(''.join(filter(str.isdigit, config_dir.Get('DepositionGeant4').Get('source_energy')))))
    source_energy_units_dataset = metadata_group.create_dataset("source_energy_units", (1,), data=str(''.join(filter(str.isalpha,config_dir.Get('DepositionGeant4').Get('source_energy')))))
    threshold_value_dataset = metadata_group.create_dataset("threshold_value", (1,), data=float(''.join(filter(str.isdigit, config_dir.Get('DefaultDigitizer:timepix').Get('threshold')))))
    threshold_units_dataset = metadata_group.create_dataset("threshold_units", (1,), data=str(''.join(filter(str.isalpha,config_dir.Get('DefaultDigitizer:timepix').Get('threshold')))))
    threshold_smearing_dataset = metadata_group.create_dataset("threshold_smearing", (1,), data=float(str(config_dir.Get('DefaultDigitizer:timepix').Get('threshold_smearing'))))
    tdc_offset_dataset = metadata_group.create_dataset("tdc_offset", (1,), data=str(config_dir.Get('DefaultDigitizer:timepix').Get('tdc_offset')))

    return metadata_group

def getData_fromRoot(hdf_out, rootObj, detector):
    #create hdf5 group
    data_group = hdf_out.create_group("data")

    #Get data information from ROOT file
    MCTrack = rootObj.Get('MCTrack')
    MCParticle = rootObj.Get('MCParticle')
    DepositedCharge = rootObj.Get('DepositedCharge')
    PixelCharge = rootObj.Get('PixelCharge')
    PixelHit = rootObj.Get('PixelHit')

    #Define lists to eventually store in HDF5
    list_event=[]
    list_pdg=[]
    list_hit_x=[]
    list_hit_y=[]
    list_hit_t=[]

    #Loop over PixelHit branch and get all relevant information
    for iev in range(0, PixelHit.GetEntries()):
        #Get all info from same event
        PixelHit.GetEntry(iev)
        PixelCharge.GetEntry(iev)
        MCParticle.GetEntry(iev)
        MCTrack.GetEntry(iev)
        PixelCharge_branch = PixelCharge.GetBranch(detector)
        PixelHit_branch = PixelHit.GetBranch(detector)
        McParticle_branch = MCParticle.GetBranch(detector)
        McTrack_branch = MCTrack.GetBranch("global")
        if (not PixelCharge_branch):
            Warning("WARNING: cannot find PixelCharge branch in the TTree with detector name: " + detector + ",  exiting")
            exit(1)

        #Get allpix-squared vectors associated with ROOT branches
        br_pix_charge = getattr(PixelCharge, PixelCharge_branch.GetName())
        br_pix_hit = getattr(PixelHit, PixelHit_branch.GetName())
        br_mc_part = getattr(MCParticle, McParticle_branch.GetName())
        br_mc_track = getattr(MCTrack, McTrack_branch.GetName())

        #Pull variables for saving and hold in arrays
        for pix_hit in br_pix_hit:
            list_event.append(iev)
            #list_pdg.append(id)
            list_hit_x.append(pix_hit.getPixel().getIndex().x())
            list_hit_y.append(pix_hit.getPixel().getIndex().y())
            list_hit_t.append(pix_hit.getGlobalTime())

    #Insert variable arrays into data dataset. ROOT contents are type cppyy.gbl.std.string
    dataLength = len(list_event)
    event_number_dataset = data_group.create_dataset("event_number", (dataLength,), data=list_event)
    #hit_pdg_dataset = data_group.create_dataset("hit_pdg", (dataLength,), data=list_pdg)
    hit_x_dataset = data_group.create_dataset("hit_x", (dataLength,), data=list_hit_x)
    hit_y_dataset = data_group.create_dataset("hit_y", (dataLength,), data=list_hit_y)
    hit_time_dataset = data_group.create_dataset("hit_time", (dataLength,), data=list_hit_t)

    return data_group


def rootToHDF5(root_file_in, detector:str='timepix', lib_path:str=None):
    #track success
    bool_success = True

    #get allpix library
    get_allpixLib(lib_path)

    #create output HDF5 object
    try:
        #name created file identically to the original ROOT file, just change the extension. Requires creation of a new file
        hdf_out = h5py.File(f'{root_file_in[:-5]}.hdf5', 'x')
    except FileExistsError:
        #Avoid accidental file trunctation by prompting user confirmation
        print(f"Output file f'{root_file_in[:-5]}.hdf5 already exists. Press enter to truncate or exit program with ctl+c")
        try:
            input()
            hdf_out = h5py.File(f'{root_file_in[:-5]}.hdf5', 'w') 
        except KeyboardInterrupt:
            return False

    #get inputs from ROOT file
    rootObj = ROOT.TFile(root_file_in)

    #get and store metadata
    metadata_group = getMetadata_fromRoot(hdf_out, rootObj.Get('config'))

    #get and store data
    data_group = getData_fromRoot(hdf_out, rootObj, detector)

    #Save groups to output HDF5
    hdf_out.flush()
    return bool_success
