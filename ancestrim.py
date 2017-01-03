#!/usr/bin/python
# -*- coding: utf-8 -*-

from ancestrim_module import handle_unicode,parse_commandline,open_rawfile,open_registerfile,func_exit,write_gedcom,write_log,write_raw
import sys, copy, time, os, operator

print("imported functions from ancestrim module")
print("----------\n")

########## open files

### parse file names from command line
file_names = parse_commandline()
current_dir = str(os.getcwd() + "/")
work_dir = str(current_dir + file_names["--folder"] + "/")

### parse generation parameter
try:
	gen_threshold = int(file_names["--gen"])
except ValueError:
	print("error in option --gen")
        print("please provide numerical value that is > 0")
	func_exit()

### open raw file
raw_data = open_rawfile(file_names["--raw"],work_dir)

raw_columns = []
for i in raw_data:
	for j in raw_data[i].keys():
		if j not in raw_columns:
			raw_columns.append(j)
print(raw_columns)

### open register file
register_list = open_registerfile(file_names["--register"],work_dir)
# discard old registers if a two-column register list is used
try:
	register_list = [item[1] for item in register_list]
except KeyError:
	pass

print("constructing pedigree for these " + str(len(register_list)) + " dogs:")
print(register_list)

########## visual progression function

def print_progress(count):
	"""Print ellipsis onscreen while iterating."""
	if count % 5 == 0:
		print("...")

########## form links

print("\nforming links")

links = []
dog_pool = copy.deepcopy(register_list)
new_pool = []
iterations = 0

while len(dog_pool) > 0:

	for p in dog_pool:
		iterations += 1
		if iterations % 50 == 0:
			print("...")
		try:
			dog = raw_data[p]
		except KeyError:
			# dog not in raw data file if this error is triggered (but can be someone's parent and hence in the pool)
			dog_pool.remove(p)
			continue
		# require both parents for pedigree purposes
		if dog["SIRE_REG_NUMBER"] != "" and dog["DAM_REG_NUMBER"] != "":
			if [dog["REGISTER_NUMBER"],dog["SIRE_REG_NUMBER"]] not in links:
				links.append([dog["REGISTER_NUMBER"],dog["SIRE_REG_NUMBER"]])
			if [dog["REGISTER_NUMBER"],dog["DAM_REG_NUMBER"]] not in links:
				links.append([dog["REGISTER_NUMBER"],dog["DAM_REG_NUMBER"]])
			dog_pool.remove(dog["REGISTER_NUMBER"])
			if dog["SIRE_REG_NUMBER"] not in new_pool:
				new_pool.append(dog["SIRE_REG_NUMBER"])
			if dog["DAM_REG_NUMBER"] not in new_pool:
				new_pool.append(dog["DAM_REG_NUMBER"])
		else:
			dog_pool.remove(dog["REGISTER_NUMBER"])

	if len(dog_pool) == 0:
		dog_pool = copy.deepcopy(new_pool)
		new_pool = []

print("formed links")

########## form paths from links

print("\nforming paths from links")
path_pool = []

iterations = 0
for r in register_list:
	iterations += 1
	print_progress(iterations)
	# gather a pool of starting links
	tmp_pool = []
	for i in links:
		if i[0] == r:
			tmp_pool.append(i)
	# iterate through growing paths until no more links can be added
	while len(tmp_pool) > 0:
		for t in tmp_pool:
			# see if last individual of path is first in a link
			if t[-1] in [j[0] for j in links[:]]:
				for j in links[:]:
					if j[0] == t[-1]:
						tmp = copy.deepcopy(t)
						# extend if link has more than 2 parts; redudant?
						if len(j) > 2:
							tmp.extend(j[:-1])
						# append last piece of link if link has two parts
						else:
							tmp.append(j[-1])
						tmp_pool.append(tmp)
			# if not, there are no further links and path is ready
			else:
				path_pool.append(t)

			tmp_pool.remove(t)

print("formed paths")

########## trim paths with generation threshold

print("\ntrimming paths for " + str(gen_threshold) + " generations")

path_pool = [p[:(gen_threshold + 1)] for p in path_pool]
path_pool = list(set([';'.join(p) for p in path_pool]))
print("...")
path_pool = [p.split(";") for p in path_pool]
path_pool = sorted(path_pool, key=operator.itemgetter(0))

print("trimmed paths")

########## create dict object from paths

path_dict = {}
for r in register_list:
	tmp_pool = []
	for p in path_pool:
		if p[0] == r:
			tmp_pool.append(p)
	path_dict[r] = tmp_pool

########## detect self-relatedness

print("\ndetecting self-relatedness")

dict_registers = [raw_data[r]["REGISTER_NUMBER"] for r in raw_data]
self_paths = {}
self_ancestors = {}
iterations = 0

# count ancestors in recursive child-parent loop
for i in register_list:
	iterations += 1
	print_progress(iterations)
	tmp_pool = []
	tmp_pool.append(i)
	tmp_ancestors = []
	tmp_paths = []
	new_pool = []
	gens = 0
	duplicate_ancestors = []

	# construct ancestor pool and limit ancestors to generation threshold
	while len(tmp_pool) > 0:
		
		for j in tmp_pool:

			if j in dict_registers:
				for r in raw_data:
					dog = raw_data[r]
					if dog["REGISTER_NUMBER"] == j:
						if dog["SIRE_REG_NUMBER"] != "" and dog["DAM_REG_NUMBER"] != "":
							new_pool.extend([dog["SIRE_REG_NUMBER"],dog["DAM_REG_NUMBER"]])
							tmp_ancestors.extend([dog["SIRE_REG_NUMBER"],dog["DAM_REG_NUMBER"]])
			tmp_pool.remove(j)

			if len(tmp_pool) == 0:
				gens += 1
				# limit to generation threshold
				# if threshold is fulfilled, do not copy ancestors to pool anymore
				if gens == gen_threshold:
					pass
				else:
					tmp_pool = copy.deepcopy(new_pool)
					new_pool = []

	# identify duplicate ancestors
	for a in tmp_ancestors:
		if tmp_ancestors.count(a) > 1:
			if [a,tmp_ancestors.count(a)] not in duplicate_ancestors:
				duplicate_ancestors.append([a,tmp_ancestors.count(a)])
	ancestor_list = [a[0] for a in duplicate_ancestors]
	self_ancestors[i] = ancestor_list

	# identify paths with duplicate ancestors
	for a in duplicate_ancestors:
		for p in path_dict[i]:
			if a[0] in p:
				if p not in tmp_paths:
					tmp_paths.append(p)
	self_paths[i] = tmp_paths

	# fix for problems caused by missing relatedness info (due to exact generation threshold)
	for p in path_dict[i]:
		for r in raw_data:
			dog = raw_data[r]
			# check if last dog from a path has an ancestor in duplicate ancestor list
			if p[-1] == dog["REGISTER_NUMBER"]:
				for k in [dog["SIRE_REG_NUMBER"],dog["DAM_REG_NUMBER"]]:
					if k in ancestor_list:
						p.append(k)
						self_paths[i].append(p)

print("finished self-relatedness")

########## trim self-related paths

print("\ntrimming self-related paths")
self_ancestors_trimmed = {}

iterations = 0
for i in register_list:
	iterations += 1
	print_progress(iterations)
	self_ancestors_trimmed[i] = []
	for p in self_paths[i]:
		binary_index = []
		for q in p:
			if q in self_ancestors[i]:
				binary_index.append("1")
			else:
				binary_index.append("0")
		binary_index = ''.join(binary_index)
		binary_index = (binary_index.rstrip("0").rstrip("1")) + "1"
		if p[:len(binary_index)] not in self_ancestors_trimmed[i]:
			self_ancestors_trimmed[i].append(p[:len(binary_index)])

print("finished trimming")

########## detect direct ancestors

print("\ndetecting direct ancestors")
direct_ancestors = {}

iterations = 0
for i in path_dict:
	direct_ancestors[i] = []
	iterations += 1
	print_progress(iterations)
	other_registers = list(path_dict.keys())
	other_registers.remove(i)
	for p in path_dict[i]:
		for q in p:
			if q in other_registers:
				if p[:p.index(q)+1] not in direct_ancestors[i]:
					direct_ancestors[i].append(p[:p.index(q)+1])

print("finished direct ancestors")

########## detect pairwise common ancestors

print("\ndetecting pairwise common ancestors")
common_ancestors = {}

iterations = 0
for i in path_dict:
	iterations += 1
	print_progress(iterations)
	other_registers = list(path_dict.keys())
	other_registers.remove(i)
	for p in path_dict[i]:
		for q in p:
			for j in other_registers:
				# check all other paths from other register numbers if they contain current path's current dog
				for k in path_dict[j]:
					if q in k:
						pair_key = (';').join(sorted([i,j]))

						# construct binary indexes for trimming
						path1_binary = []
						for x in p:
							if x in k:
								path1_binary.append("1")
							else:
								path1_binary.append("0")
						path1_binary = ''.join(path1_binary)
						path2_binary = []
						for y in k:
							if y in p:
								path2_binary.append("1")
							else:
								path2_binary.append("0")
						path2_binary = ''.join(path2_binary)
						[path1_binary,path2_binary] = [(item.rstrip("0").rstrip("1") + "1") for item in [path1_binary,path2_binary]]
						pair_path = sorted([p[:len(path1_binary)],k[:len(path2_binary)]], key=operator.itemgetter(0))
						
						# add to dictionary in fashion dict[dog1;dog2] = [dog1path,dog2path]
						try:
							if pair_path not in common_ancestors[pair_key]:
								common_ancestors[pair_key].append(pair_path)
						except KeyError:
							common_ancestors[pair_key] = []
							if pair_path not in common_ancestors[pair_key]:
								common_ancestors[pair_key].append(pair_path)

print("finished common ancestors")

########## gather minimum paths

print("\ngathering minimum dogs")

# minimum_paths contains all necessary paths to draw pedigree
minimum_paths = []

for i in common_ancestors:
	for j in common_ancestors[i]:
		minimum_paths.extend(j)

for i in self_ancestors_trimmed:
	if len(i) != 0:
		minimum_paths.extend(self_ancestors_trimmed[i])

for i in direct_ancestors:
	if len(i) != 0:
		minimum_paths.extend(direct_ancestors[i])

# minimum dogs contains necessary dogs, including mates
minimum_dogs = []

iterations = 0
for i in minimum_paths:
	iterations += 1
	if iterations % 10 == 0:
		print("...")
	# search parent-mate relations for every dog but last in path
	for j in i[:-1]:
		if j not in minimum_dogs:
			minimum_dogs.append(j)
		for r in raw_data:
			dog = raw_data[r]
			if dog["REGISTER_NUMBER"] == j:
				if dog["SIRE_REG_NUMBER"] not in minimum_dogs:
					minimum_dogs.append(dog["SIRE_REG_NUMBER"])
				if dog["DAM_REG_NUMBER"] not in minimum_dogs:
					minimum_dogs.append(dog["DAM_REG_NUMBER"])
	if i[-1] not in minimum_dogs:
		minimum_dogs.append(i[-1])

# minimum_data contains a subset of data with minimum dogs
minimum_data = {}
for i in minimum_dogs:
	try:
		minimum_data[i] = raw_data[i]
	# if this error is triggered, a dog is in a minimum path as parent
	# but was beyond threshold -> no entry in raw data
	except KeyError:
		pass

discarded_dogs = []
for i in raw_data:
	if i not in minimum_dogs:
		if i not in discarded_dogs:
			discarded_dogs.append(i)

print("finished collecting dogs")

print("finished analysis")

########## write to gedcom file

print("")

# convert dict to list of dicts
minimum_data = [minimum_data[item] for item in minimum_data]
# assign genopro id's
genopro_id = 0
for i in minimum_data:
	genopro_id += 1
	i["genopro_id"] = str("@I" + str(genopro_id) + "@")

write_gedcom(file_names["--out"],work_dir,minimum_data,"_clean")
print("wrote gedcom file to " + str(file_names["--out"] + "_clean.ged"))

write_raw(file_names["--out"],work_dir,minimum_data,raw_columns,"pruned")
print("wrote pruned data file to " + str(file_names["--out"] + "_pruned.txt"))

write_log(file_names["--out"],file_names["--raw"],file_names["--register"],work_dir,raw_data,minimum_data,discarded_dogs,register_list,file_names["--gen"])
print("wrote log file to " + str(file_names["--out"] + ".log"))

