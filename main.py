import ctypes
import os
import json
import random
import pathlib

'''
	For the given path, get the List of all files in the directory tree 
'''
def getListOfFiles(dirName):
	# create a list of file and sub directories 
	# names in the given directory 
	listOfFile = os.listdir(dirName)
	allFiles = list()
	# Iterate over all the entries
	for entry in listOfFile:
		# Create full path
		fullPath = os.path.join(dirName, entry)
		# If entry is a directory then get the list of files in this directory 
		if os.path.isdir(fullPath):
			allFiles = allFiles + getListOfFiles(fullPath)
		else:
			allFiles.append(fullPath)
				
	return allFiles        

def recursive_items(dictionary, current_path):
	if type(dictionary) is dict:
		for key, value in dictionary.items():
			if type(value) is dict or type(value) is list:
				yield (current_path + "[" + repr(key) + "]", value, key)
				yield from recursive_items(value, current_path + "[" + repr(key) + "]")
			else:
				yield (current_path + "[" + repr(key) + "]", value, key)
	elif type(dictionary) is list:
		for index, value in enumerate(dictionary):
			if type(value) is dict or type(value) is list:
				yield (current_path + "[" + repr(index) + "]", value, index)
				yield from recursive_items(value, current_path + "[" + repr(index) + "]")
			else:
				yield (current_path + "[" + repr(index) + "]", value, index)




	
dirName = 'input\\maps\\'
	
# Get the list of all files in directory tree at given path
listOfFiles = getListOfFiles(dirName)

for i in range(len(listOfFiles)):
	b = pathlib.PureWindowsPath(listOfFiles[i])
	listOfFiles[i] = b.as_posix()

mapsLoaded = 0
totalMaps = len(listOfFiles)
currentMap = 0
dataPath = []

messages = 0
texts = 0
labels = 0
faces = 0

print("Loading dialogueData.json...")
with open("data/dialogueData.json") as file:
	dialogueData = json.load(file)
print("dialogueData.json loaded!\n")

seed = ""

while True:
	print(
		"Seed?",
		"Yes or No",
		sep="\n"
	)
	x = input("> ")
	x = x.lower()
	print()
	if x == "no":
		seed = random.randint(0,999999999)
		break
	elif x == "yes":
		try:
			seed = input("seed > ")
			seed = int(seed)
		except:
			seed = list(seed)
			temp = []
			for i in range(seed.__len__()):
				temp.append(str(ord(seed.pop().lower())))
			seed = int("".join(temp))
		break

random.seed(seed)

print("Randomizing dialogueData...")
random.shuffle(dialogueData["labels"][0])
random.shuffle(dialogueData["messages"][0])
random.shuffle(dialogueData["texts"][0])
i = 0
for key, value in dialogueData["faces"][0].items():
	random.shuffle(value)
	i += 1
print("dialogueData randomized!\n")

data = {}
outputPath = []
filePath = ""

for i in range(len(listOfFiles)):
	filePath = listOfFiles.pop(0)
	print("Loading "+ filePath.split("/")[-1])
	with open(filePath) as file:
		dataPath.append(filePath)
		temp = ""
		for obj in filePath.split("/"):
			if obj == "input":
				temp = "output/RandomizedDialogue/assets/data"
			else:
				temp += "/" + str(obj)
		outputPath.append(temp)
		exec("global data, json, file; data['"+filePath+"'] = json.load(file)", globals(), {"data": data, "json":json, "file": file})
		print("Loaded "+ filePath.split("/")[-1]+"\n")
print("Has loaded all maps!\n")
		
for key, value in dialogueData.items():
	if key == "faces":
		for key2, value2 in value[0].items():
			i = 0
			for obj in value2:
				exec("global data; data['" + dialogueData["faces"][1][key2][i].split("[")[0] + "']["+dialogueData["faces"][1][key2][i].split("[", 1)[1]+" = " + str(obj), globals(), {"data": data})
			i += 1
	elif key == "labels":
		for i in range(len(value[0])):
			exec("global data, value, i; data['" + dialogueData["labels"][1][i].split("[")[0] + "']["+dialogueData["labels"][1][i].split("[", 1)[1]+" = value[0][i]", globals(), {"data": data, "value": value, "i": i})
	elif key == "messages":
		for i in range(len(value[0])):
			exec("global data, value, i; data['" + dialogueData["messages"][1][i].split("[")[0] + "']["+dialogueData["messages"][1][i].split("[", 1)[1]+" = value[0][i]", globals(), {"data": data, "value": value, "i": i})
	elif key == "texts":
		for i in range(len(value[0])):
			exec("global data, value, i; data['" + dialogueData["texts"][1][i].split("[")[0] + "']["+dialogueData["texts"][1][i].split("[", 1)[1]+" = value[0][i]", globals(), {"data": data, "value": value, "i": i})

c = 0

ctypes.windll.kernel32.SetConsoleTitleW("Maps saved - {} of {}".format(0, len(outputPath)))
for i in range(len(outputPath)):
	print("Saving "+dataPath[i].split("/")[-1]+"...")
	c = 0
	while True:
		c += 1
		try:
			with open(outputPath[i], 'w') as outfile:
				exec("global data, json, outfile; json.dump(data['"+dataPath[i]+"'], outfile, sort_keys=True, indent=4)", globals(), {"data": data, "json":json, "outfile": outfile})
			break;
		except:
			cPath = ""
			for a in range(c):
				if a == 0:
					cPath += outputPath[i].split('/')[0]
				else:
					cPath += "/" + outputPath[i].split('/')[a]
			print(cPath)
			try:
				os.mkdir(cPath)
			except:
				None
	print("Saved "+dataPath[i].split("/")[-1]+"\n")
	ctypes.windll.kernel32.SetConsoleTitleW("Maps saved - {} of {}".format(i+1, len(outputPath)))
with open("output/RandomizedDialogue/package.json", "w") as outfile:
	json.dump({"name": "Randomized dialogue"}, outfile, sort_keys=True, indent=4)

print("Data randomized!\n")

print("done")

while True:
	None