#make a qchem input file from an xyz

import argparse
import sys
import numpy as np
import os 

parser=argparse.ArgumentParser(add_help=True, description = 'takes an xyz file and sets up a calc ')
parser.add_argument('-i', action='store', dest='infile', type=str, required=False, help='input xyz file in standard form')
parser.add_argument('-multi', action='store_true', dest='multi', required=False,help='operate on all .XYZ files in the current directory with the same set of parameters')
parser.parse_args()

def tryint(s):
    try:
        return int(s)
    except:
        return s

def get_environment():
    dct = {}
    needed = "HOME REMOTE_DIR RJ_UNAME".split()
    for n in needed:
        dct[n] = os.environ.get(n)
    if dct["RJ_UNAME"] is None:
        dct["RJ_UNAME"] = os.environ.get("REMOTE_USER")
    return dct


def ask_default(ask, default=None):
    while True:
        msg = "{} [{}]:  ".format(ask, default)
        answer = input(msg)
        if not answer:
            answer = default
        if answer:
            return answer

def to_rassolov(basis):
    out = []
    for c in list(basis):
        if c == "+":
            out.append('p')
        elif c == "*":
            out.append('d')
        elif c not in ["(", ")"]:
            out.append(c)
    return "".join(out)

def diffuse(diff):
    if diff == False:
        return "6-31G(d)", "6-31Gd"
    return "6-31+G(d)", "6-31pGd"


       
class qjob(object):
    mode = None
    coords = None
    def __init__(self, infile):
        """initialises all the params and sets up filenames"""
        self.infile = infile
        self.outfile = ''
        self.params =  dict(
        method ="",
        opt="",
        freq="",
        zm="",
        scrf="",
        cm="",
        solvent="",
        algorithm="DIIS",
        conv_thresh="",
        ts = "",)
        self.add_environment()
        self.xyz_geometry()



    def xyz_geometry(self):
        """find the molecule specification section"""
        geometry = []
        with open(self.infile, 'r') as f:
            contents = f.readlines()
            for line in contents:
                pot_line = '[a-zA-Z][a-zA-Z][ \t]+[0-9.\-]+[ \t]+[0-9.\-]+[ \t]+[0-9.\-]+.*'
                if re.match(pot_line, line) is not None:
                geometry.append(line)
        self.coords = geometry

    def add_environment(self):
        self.params.update(get_environment())

    def get_outstr(self):
        self.outfile += ".{level}.{basis}".format(**self.params) #solvent and scrf


    def ask_qns(self):
        charge = ask_default("What is the charge of this molecule?","0")
        multi = ask_default("What is the multiplicity of this molecule?","1")

        self.params["cm"] = "{} {}".format(charge, multi)
        self.params["method"] = ask_default("What level of theory do you want to use?", "M062X")
        self.params["basis"] = ask_default("Which basis do you want to use?","6-31+G*")
        
        solv = ask_bool("Do you want to use a solvent model?", "N")
        if solv:
            self.params["scrf"] = ask_default("What solvent model do you want?","SMD")
            self.params["solvent"] = ask_default("What is the solvent you want to use (toluene,etac,h2o)?","h2o")
        
        opt_geom = ask_bool("Do you want to optimise the geometry?","N")
        if opt_geom:
            self.params['opt'] = True
            self.params["freq"] = True
            zmat = ask_bool("Optimise with Z matrix ?", "N")
            if zmat:
                self.params['zmat'] = True

        self.params["conv_thresh"] = ask_default("Required convergence threshold", "Tight")
         
        elec_field = ask_bool("Do you want to use an external electric field?","N")
        if elec_field:
            raise ValueError("I haven't done this yet.")


        
class gaujob(qjob):
    """gaussian job"""
    if self.params["method"].lower() in "csd qci mp2 hf".split():
        self.params["grid"] = ""
    else:
        self.params["grid"] = "INT(grid=ultrafine)"

    if self.params["basis"] in "6-31G* 6-31+G* 6-31G(d) 6-31+G(d)".split():
        rassolov =  ask_bool("Do you want to use the Rassolov version?","Y")
        if rassolov:
            self.params["genbasis"] = to_rassolov(self.params["basis"])
            self.params["basis"] = "Gen 6D"
            self.params["basfooter"] = "@/home/{REMOTE_DIR}/{RJ_UNAME}/Basis/{genbasis}.gbs/N\n\n".format(**self.params)
        else:
            self.params["genbasis"] = self.params["basis"]

    if self.params["opt"]:
        self.params["optstr"] = "OPT IOP(2/17=4)"

    if self.params["zmat"]:
        


    

    ### Templates ###
    link = "\n--Link1--\n"
    name = "\n\n{fname}{jobid}\n\n"
    new = "%chk={fname}{jobid}.chk\n\# {level}/{basis} SCF=Tight {grid} {scrf2} {fld}"
    header = "%chk={fname}{jobid}.chk\n\# {level}/{basis} SCF=Tight {grid} {opt} {freq} {scrf_} {fld} "
    footer = "{basfooter}{solfooter}{fieldfooter}"
    gfooter = "{solfooter}{nl}{basfooter}{fieldfooter}"
    geom = "geom=check guess=read IOP(2/17=4)\n\n{fname}{jobid}\n\n{cm}\n\n"

    dct["foot"] = footer.format(**dct)
    if opt_geom:
        dct["head"] = header.format(scrf_=dct["scrf2"], **dct)
        dct["foot"] += (link+header+geom+footer).format(scrf_=dct["scrf"], **dct)
        if calc_gsolv:
            dct["foot"] += (link+new+geom+gfooter).format(**dct)
    else:
        dct["head"] = header.format(scrf_=dct["scrf"], **dct)


    com_file_lines = "{head}\n{geometry}\n{foot}".format(**dct)
    print("\nPrinting to {fname}{jobid}.com\n".format(**dct))
    with open("{fname}{jobid}.com".format(**dct), 'w') as f:
        f.write(com_file_lines)




class qchemjob(qjob):
    """qchem job"""
    def __init__(self):

class molprojob(qjob):
    """molpro job"""
    def __init__(self):

        






