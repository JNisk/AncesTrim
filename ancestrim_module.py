#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Tools for trimming and writing pedigree data.
"""

from datetime import datetime
import time,sys,os,math
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

########## custom exit function

def func_exit():
	"""Print an exit message and exit script."""
	print("exiting...")
	exit(0)

########## unicode handling

output_chars = ['À','Á','Â','Ã','Ä','Å','Æ','Ç','È','É','Ê','Ë','Ì','Í','Î','Ï','Ð','Ñ','Ò','Ó','Ô','Õ','Ö','×','Ø','Ù','Ú','Û','Ü','Ý','Þ','ß','à','á','â','ã','ä','å','æ','ç','è','é','ê','ë','ì','í','î','ï','ð','ñ','ò','ó','ô','õ','ö','÷','ø','ù','ú','û','ü','ý','þ','ÿ','Ř','Ů','´']
input_chars = [u'\xc3\x80',u'\xc3\x81',u'\xc3\x82',u'\xc3\x83',u'\xc3\x84',u'\xc3\x85',u'\xc3\x86',u'\xc3\x87',u'\xc3\x88',u'\xc3\x89',u'\xc3\x8a',u'\xc3\x8b',u'\xc3\x8c',u'\xc3\x8d',u'\xc3\x8e',u'\xc3\x8f',u'\xc3\x90',u'\xc3\x91',u'\xc3\x92',u'\xc3\x93',u'\xc3\x94',u'\xc3\x95',u'\xc3\x96',u'\xc3\x97',u'\xc3\x98',u'\xc3\x99',u'\xc3\x9a',u'\xc3\x9b',u'\xc3\x9c',u'\xc3\x9d',u'\xc3\x9e',u'\xc3\x9f',u'\xc3\xa0',u'\xc3\xa1',u'\xc3\xa2',u'\xc3\xa3',u'\xc3\xa4',u'\xc3\xa5',u'\xc3\xa6',u'\xc3\xa7',u'\xc3\xa8',u'\xc3\xa9',u'\xc3\xaa',u'\xc3\xab',u'\xc3\xac',u'\xc3\xad',u'\xc3\xae',u'\xc3\xaf',u'\xc3\xb0',u'\xc3\xb1',u'\xc3\xb2',u'\xc3\xb3',u'\xc3\xb4',u'\xc3\xb5',u'\xc3\xb6',u'\xc3\xb7',u'\xc3\xb8',u'\xc3\xb9',u'\xc3\xba',u'\xc3\xbb',u'\xc3\xbc',u'\xc3\xbd',u'\xc3\xbe',u'\xc3\xbf',u'\xc5\x98',u'\xc5\xae',u'\xc2\xb4']

### handle unicode better
def handle_unicode(name):
	"""A custom function for formatting special characters."""
	name = name.decode('utf-8')
	for i in input_chars:
		if i in name:
			name = name.replace(i, output_chars[input_chars.index(i)])
	name = name.strip(" ")
	return name

########## command line parser

def parse_commandline():
	"""Parse parameters from command line with syntax --option [filename] and return a dict object."""
	def_args = {"--out":"output file name", "--folder":"subfolder"}
	if "ancestrim" in sys.argv[0]:
		def_args["--raw"] = "raw file"
		def_args["--register"] = "register file"
		def_args["--gen"] = "number of generations"
	del sys.argv[0]
	arguments = [sys.argv[i:i + 2] for i in xrange(0, len(sys.argv), 2)]
	arg_keys = [item[0] for item in arguments]
	#check that obligatory options exist
	for d in def_args:
		if d not in arg_keys:
			print("missing option " + str(d))
			print("please specify " + str(def_args[d]) + " with " + str(d))
			func_exit()
	arg_options = {}
	for i in arguments:
		#assign options as keys and file names as values in dict arg_options
		try:
			for j in ["--out","--folder","--gen","--raw","--register"]:
				if str(i[0]) == j:
					arg_options[j] = str(i[1])
		except IndexError:
			print("error in options, please check command line")
			func_exit()
        forbidden_characters = ["\\","/",":","*","?",'"',"<",">","|","#"]
	for i in forbidden_characters:
		if i in arg_options["--out"]:
			print('invalid outfile name: file names cannot contain \/:*?"<>|#')
			print("please use another name")
			func_exit()

	return arg_options

########## open raw file

def open_rawfile(rawfile,folder):
	"""Open raw file and write its contents to a dict object."""
	o = open((str(folder) + str(rawfile)),"r")
	header = o.readline().strip().split("\t")
	dog_data = {}
	for line in o:
		line = line.rstrip("\n").split("\t")
		line = [i.rstrip() for i in line]
		tmp = {}
		for i in header:
			tmp[i] = handle_unicode(line[header.index(i)])
		dog_data[tmp["REGISTER_NUMBER"]] = tmp
	return dog_data

########## open register file

def open_registerfile(regfile,folder):
	"""Open register file and write its contents to a list object."""
	o = open((str(folder) + str(regfile)),"r")
	o.next()
	register_data = []
	for line in o:
		line = line.rstrip("\n").split("\t")
		if len(line) == 2:
			register_data.append([handle_unicode(line[0]),handle_unicode(line[1])])
	return register_data

########## write to gedcom file

def write_gedcom(outfile,folder,dog_list,clean=""):
	"""Take a filename, folder and list of pedigree data dicts and write to GEDCOM file format (.ged)."""
	ind_count = 0
	o = open(str((folder + outfile) + str(clean) +  ".ged"), "w")

	### write initial lines to file
	o.write("0 HEAD\n")
	o.write("1 SOUR (c) Niskanen, J. 2017\n")
	o.write("2 VERS 1.0\n")
	o.write("2 DATE 03.01.2017\n")
	o.write("1 DEST GenoPro 2011\n")
	o.write("1 FILE " + str(outfile) + "\n")
	o.write("2 TIME " + str(time.strftime("%d.%m.%Y %H:%M:%S")) + "\n")
	o.write("1 GEDC\n")
	o.write("2 VERS 5.5\n")
	o.write("1 CHAR UTF-8\n")

	### write individuals
	for a in dog_list:
		o.write("0 " + a["genopro_id"] + "  INDI\n")
		for i in a:
			if i == "DOGNAME":
				o.write("1 NAME " + a["DOGNAME"] + "\n")
			elif i == "SEX":
				if str(a["SEX"]) == "1":
					o.write("1 SEX M\n")
				if str(a["SEX"]) == "2":
					o.write("1 SEX F\n")
			elif i == "genopro_id":
				pass
			else:
				o.write("1 " + str(i) + " " + a[i] + "\n")
	### form mates
	families = []
	for a in dog_list:
		# form mates only if dog has both parents
		if a["SIRE_REG_NUMBER"] != "" and a["DAM_REG_NUMBER"] != "":
			# check if parents already exist
			if [a["SIRE_REG_NUMBER"],a["DAM_REG_NUMBER"]] in [f[0] for f in families]:
				for f in families:
					# identify correct family and add new child
					if [a["SIRE_REG_NUMBER"],a["DAM_REG_NUMBER"]] == f[0]:
						f[1].append(a["REGISTER_NUMBER"])
			# make new family if parents not found
			else:
				families.append([[a["SIRE_REG_NUMBER"],a["DAM_REG_NUMBER"]],[a["REGISTER_NUMBER"]]])
	### write families
	fam_count = 0
	found_dogs = [item["REGISTER_NUMBER"] for item in dog_list]
	for f in families:
		# only write families if both parents are in all_dogs
		# some families exist where parents are known but data was not gathered due to threshold limit
		if f[0][0] in found_dogs and f[0][1] in found_dogs:
			fam_count += 1
			o.write("0 @F" + str(fam_count) + "@ FAM\n")
			# iterate parents first
			for a in dog_list:
				if a["REGISTER_NUMBER"] == f[0][0]:
					o.write("1 HUSB " + a["genopro_id"] + "\n")
				if a["REGISTER_NUMBER"] == f[0][1]:
					o.write("1 WIFE " + a["genopro_id"] + "\n")
			# iterate children
			for i in f[1]:
				for a in dog_list:
					if a["REGISTER_NUMBER"] == i:
						o.write("1 CHIL " + a["genopro_id"] + "\n")
	o.close()

	return o	

########## write to raw file

def write_raw(outfile,folder,dog_list,config=[],pruned=""):
	"""Take a filename, folder, a list of pedigree data dicts and optionally list of config options and write data to raw file."""
	if pruned == "":
		suffix = "_raw.txt"
	else:
		suffix = "_pruned.txt"
	o = open(str(folder + outfile + suffix), "w")
	header = ["DOGID","DOGNAME","REGISTER_NUMBER","SEX","SIREID","SIRE_REG_NUMBER","SIRENAME","DAMID","DAM_REG_NUMBER","DAMNAME"]
	for i in config:
		if i not in header:
			header.append(i)
	for i in header[:-1]:
		o.write(i + "\t")
	o.write(header[-1] + "\n")
	for a in dog_list:
		for i in header[:-1]:
			try:
				o.write(a[i] + "\t")
			except KeyError:
				o.write("\t")
		try:
			o.write(a[header[-1]] + "\n")
		except KeyError:
			o.write("\n")
	o.close()

########## write to log file

def write_log(outfile,raw_file,register_file,folder,raw_data,minimum_data,discarded,register_list,gen):
	"""Write information about the run to a log file."""
	minimum_regs = [i["REGISTER_NUMBER"] for i in minimum_data]
	minimum_regs.sort()
	discarded.sort()
	o = open(str((folder + outfile) + ".log"),"w")
	o.write("finished run at " + str(time.strftime("%d.%m.%Y %H:%M:%S")) + "\n")
	o.write("read data from folder: " + str(folder) + "\n")
	o.write("read raw file from: " + str(raw_file) + "\n")
	o.write("read register file from: " + str(register_file) + "\n\n")
	o.write("constructed pedigree for " + str(len(register_list)) + " dogs:\n")
	for i in register_list[:-1]:
		o.write(i + ", ")
	o.write(register_list[-1] + "\n")
	o.write("\ntrimmed for " + str(gen) + " generations\n")
	o.write("found " + str(len(raw_data)) + " dogs in raw data\n")
	o.write(" " + str(len(minimum_data)) + "/" + str(len(raw_data)) + " dogs were kept\n")
	o.write(" " + str(len(discarded)) + "/" + str(len(raw_data)) + " dogs were discarded\n\n")
	o.write("kept the following " + str(len(minimum_data)) + " register numbers:\n")
	for i in minimum_regs[:-1]:
		o.write(i + ", ")
	o.write(str(minimum_regs[-1]) + "\n")
	o.write("\ndiscarded the following " + str(len(discarded)) + " register numbers:\n")
	for i in discarded[:-1]:
		o.write(i + ", ")
	o.write(discarded[-1] + "\n")
	o.write("\nwrote gedcom file to: " + str(outfile) + "_clean.ged\n")
	o.write("wrote pruned data file to: " + str(outfile) + "_pruned.txt\n")
	o.write("wrote log file to: " + str(outfile) + ".log\n")
	o.close()
