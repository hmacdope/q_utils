#comify
import argparse
import numpy as np
import os 

parser=argparse.ArgumentParser(add_help=True, description = 'takes an xyz file and sets up a DFT calc ')
parser.add_argument('-i', action='store', dest='infile', type=str, required=False, help='input xyz file in standard form')
parser.add_argument('-o', action='store', dest='outfile', type=str, required=False, default=None, help='output com file name, defaults to the prefix of xyz file ')
parser.add_argument('-r', action='store_true', dest='runf', required=False, help='make raijin runfile with default settings')
parser.add_argument('-f', action='store_true', dest='freq', required=False, help='run frequncy calculation with same basis set etc')
parser.add_argument('-multi', action='store_true', dest='multi', required=False,help='operate on all .XYZ files in the current directory with the same set of parameters')

args = parser.parse_args()


def tryint(s):
    try:
        return int(s)
    except:
        return s

        
class comfile(object):
    """comfile for setting up and manipulating gaussian jobs
    at the moment I have it set up for my M06 job defaults,
     but adding other stuff can be v easy"""
    def __init__(self, infile, outfile):
        """initialises all the params and sets up filenames"""
        super(comfile, self).__init__()
        self.infile = infile
        self.outfile = outfile
        self.runfile = 'gjob_' + outfile.split('.')[0] + '.run'
        self.logfile = outfile.split('.')[0] + '.log'
        self.title = outfile.split('.')[0]
        self.basis = None
        self.functional = None
        self.charge = None
        self.multiplicity = None
        self.solventmodel = None
        self.body = None
        self.atom_list = None
        self.coords = None
        self.read_params()



    def write_output(self):
        """master control for writing output"""
        self.write_header()
        self.find_molspec()
        self.write_body()
        if args.freq:
            self.write_freqjob()
        self.write_tail
        self.write_runfile()

    def find_molspec(self):
        """find the molecule specification section"""
        with open(self.infile, 'r') as f:
            lines = f.readlines()
            counter = 0
            for line in lines:
                tokens = line.split()
                if len(tokens) == 1:
                    atmn = tryint(tokens[0])
                    if atmn is int:
                        return counter
                        break
            else:
                counter += 1
            self.molspec = lines[counter +1:-1]

    def write_header(self):
        """write the header, this is my custom setup but
         many of these could become self.arg options if
          required to be readin by read_params"""
        with open(self.outfile, 'w') as o:
            o.write('%mem=4Gb\n')
            o.write('%NprocShared=16\n')
            o.write('%chk={}.chk\n'.format(self.title))
            o.write('# {}/{} SCF=(Tight,XQC,MaxConventionalCycles=400) INT(grid=ultrafine) OPT SCRF=(SMD,Solvent=h2o) Maxdisk=100Gb\n'.format(self.functional, self.basis))
            o.write('\n')
            o.write('{}\n'.format(self.title))
            o.write('\n')
            o.write('{} {}'.format(self.charge, self.multiplicity))
            o.write('\n')

    def write_body(self):
        """write the molecule specification"""
        with open(self.outfile, 'a') as o:
            for line in self.molspec:
                o.write(line)
            o.write('\n')

    def write_freqjob(self):
        """run a frequency calc, again my setup but easily changed """
        with open(self.outfile, 'a') as o:
            o.write('--Link1--\n')
            o.write('%chk={}\n'.format(self.title))
            o.write('# {}/{} SCF=(Tight,XQC,MaxConventionalCycles=400) INT(grid=ultrafine) Freq=noraman geom=check guess=read\n'.format(self.functional, self.basis))
            o.write('{} {}'.format(self.charge, self.multiplicity))
    def write_tail(self):
        """write the annoying tail element"""
        with open(self.outfile, 'a') as o:
            o.write('\n')

    def read_params(self):
        """readin params for job, basis charge and multiplicity """
        print('############################')
        print('# Start Gaussian Job Setup #')
        print('############################')
        print('\n')
        print('specify basis set [ 6-31+G** ]')
        self.basis = str(input())
        print('specify functional [ M06L ]')
        self.fn = str(input())
        print('what is the total charge [ 0 ]')
        self.charge =  input()
        print('what is the multiplicity [ 1 ]')
        self.multiplicity = input()
        
        if self.basis is '':
            self.basis = '6-31+G**'
        if self.fn is '':
            self.fn = 'M06L'        
        if self.multiplicity is '':
            self.multiplicity = 1
        if  self.charge is '':
            self.charge = 1
        
        #check for errors
        try:
          int(self.multiplicity)
        except:
            raise Exception(' Your multiplicity is not an integer')
                #check for errors
        try:
          int(self.charge)
        except:
            raise Exception('Your charge is not an integer')

    def assign_coords(self):
        self.atom_list = self.molspec[0::4]
        xcoords = self.molspec[1::4]
        ycoords = self.molspec[2::4]
        z_coords = self.molspec[3::4]
        self.coords = np.vstack([np.asarrray(xcoords), np.asarrray(ycoords), np.asarrray(zcoords)], dtype=np.float64)
        # where are the heavy atoms
    
    def find_heavy_atoms(self):
            idx_list = []
            counter = 0
            for atm in self.atom_list:
                if atm == 'C' or 'N' or 'O':
                    idx_list.append(counter)
            heavy_atm_coord = self.coords[idx_list,:]
            return  idx_list, heavy_atm_coord

    def furthest_atom(self):
        blah = "blah"
    
    def write_runfile(self):
        if args.runf:
            with open(self.runfile, 'w') as rf:
                rf.write('#!/bin/bash\n')
                rf.write('#PBS -l walltime=24:00:00\n')
                rf.write('#PBS -l ncpus=16\n')
                rf.write('#PBS -l mem=5GB\n')
                rf.write('#PBS -l jobfs=100GB\n')
                rf.write('#PBS -l software=g16\n')
                rf.write('#PBS -l wd\n')
                rf.write('#PBS -q normal\n')
                rf.write('\n')
                rf.write('module load gaussian/g16a03\n')
                rf.write('g16 < {}  > {} 2>&1\n'.format(self.outfile, self.logfile))
                rf.write('\n')



fl = os.listdir()
xyz_l = [f for f in fl if '.xyz' in f]

for file in xyz_l:
    outfile = args.outfile
    if outfile is None:
        outfile = file.split('.')[0] + '.com'
    print('FILENAME {}'.format(file))
    cf = comfile(file, outfile)
    cf.write_output()




            















