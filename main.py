import sys
import os
import json
import random
import pathlib

def main():
	
	dirName = 'input\\maps\\'
	listOfMaps = getListOfFiles(dirName)

	for i in range(len(listOfMaps)):
		b = pathlib.PureWindowsPath(listOfMaps[i])
		listOfMaps[i] = b.as_posix()
	print("Loading dialogueData.json...")
	with open("data/dialogueData.json") as file:
		dialogueData = json.load(file)
	print("dialogueData.json loaded!\n")

	
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
			seed = random.randint(100000000,999999999)
			break
		elif x == "yes":
			try:
				seed = input("seed > ")
				seed = int(seed)
			except ValueError:
				seed = list(seed)
				temp = list()
				for i in range(len(seed)):
					temp.append(str(ord(seed.pop().lower())))
				seed = int("".join(temp))
				del temp
			break
	random.seed(seed)


	print("Randomizing dialogueData...")
	random.shuffle(dialogueData["labels"][0])
	random.shuffle(dialogueData["messages"][0])
	random.shuffle(dialogueData["texts"][0])
	random.shuffle(dialogueData["texts"][0])
	for key, value in dialogueData["faces"][0].items():
		random.shuffle(value)
	print("dialogueData randomized!\n")


	dataPaths = list()
	data = dict()
	outputPaths = list()

	for i in range(len(listOfMaps)):
		filePath = listOfMaps.pop(0)
		print("Loading "+ filePath.split("/")[-1])
		with open(filePath) as file:
			dataPaths.append(filePath)
			for obj in filePath.split("/"):
				if obj == "input":
					temp = "output/RandomizedDialogue/assets/data"
				else:
					temp += "/" + str(obj)
			outputPaths.append(temp)

			print(type(file))
			exec(
				"data['"+filePath+"'] = json.load(file)",
				globals(),
				{"data": data, "json":json, "file": file}
			)
			print("Loaded "+ filePath.split("/")[-1]+"\n")

	del temp

	print("Has loaded all maps!\n")
	

	for key, value in dialogueData.items():
		if key == "faces":
			for key2, value2 in value[0].items():
				i = 0
				for obj in value2:
					exec(
						"data['" + dialogueData["faces"][1][key2][i].split("[")[0] + "']["+dialogueData["faces"][1][key2][i].split("[", 1)[1] +
						" = " + str(obj),
						globals(),
						{"data": data}
					)
					i += 1
		
		elif key == "labels":
			for i in range(len(value[0])):
				exec(
					"data['" + dialogueData["labels"][1][i].split("[")[0] + "']["+dialogueData["labels"][1][i].split("[", 1)[1] +
					" = value[0][i]",
					globals(),
					{"data": data, "value": value, "i": i}
				)
		
		elif key == "messages":
			for i in range(len(value[0])):
				exec(
					"data['" + dialogueData["messages"][1][i].split("[")[0] + "']["+dialogueData["messages"][1][i].split("[", 1)[1] +
					" = value[0][i]",
					globals(),
					{"data": data, "value": value, "i": i}
				)
		
		elif key == "texts":
			for i in range(len(value[0])):
				exec(
					"data['" + dialogueData["texts"][1][i].split("[")[0] + "']["+dialogueData["texts"][1][i].split("[", 1)[1]+
					" = value[0][i]",
					globals(), {"data": data, "value": value, "i": i}
				)


	ChangeTitle("Maps saved - {} of {}".format(0, len(outputPaths)))


	for i in range(len(outputPaths)):
		mapName = dataPaths[i].split("/")[-1]
		print("Saving "+mapName+"...")
		c = 0

		while True:
			c += 1
			try:
				with open(outputPaths[i], 'w') as outfile:
					exec(
						"json.dump(data['"+dataPaths[i]+"'], outfile, sort_keys=True, indent=4)",
						globals(),
						{"data": data, "json":json, "outfile": outfile}
					)
				break;
			
			except:
				pathToCreate = ""
				
				for a in range(c):
					if a == 0:
						pathToCreate += outputPaths[i].split('/')[0]
					else:
						pathToCreate += "/" + outputPaths[i].split('/')[a]
				print(pathToCreate)
				
				try:
					os.mkdir(pathToCreate)
				except:
					None

		print("Saved "+mapName+"\n")
		ChangeTitle("Maps saved - {} of {}".format(i+1, len(outputPaths)))


	with open("output/RandomizedDialogue/package.json", "w") as outfile:
		json.dump({"name": "Randomized dialogue"}, outfile, sort_keys=True, indent=4)

	print("Data randomized!\n")

	while True:
		None


def ChangeTitle(title):
	os.system("title "+title)


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


if __name__ == '__main__':
	main()