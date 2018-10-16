import ctypes
import os
import json
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



def main():
	
	dirName = 'input\\maps\\';
	
	# Get the list of all files in directory tree at given path
	listOfFiles = getListOfFiles(dirName)


	for i in range(len(listOfFiles)):
		b = pathlib.PureWindowsPath(listOfFiles[i])
		listOfFiles[i] = b.as_posix()

	mapsLoaded = 0
	totalMaps = len(listOfFiles)
	currentMap = 0
	messages = 0
	faces = 0
	labels = 0
	texts = 0
	data = []
	dataPath = []
	dialogueData = {
		"messages": [[], []],
		"texts": [[], []],
		"faces": [{}, {}],
		"labels": [[], []]
	}

	while len(listOfFiles) != 0:
		if len(listOfFiles) < 50:
			times = len(listOfFiles)
		else:
			times = 50
		for i in range(times):
			filePath = listOfFiles.pop(0)
			print("Loading " + filePath.split("/")[-1])
			with open(filePath) as file:
				data.append(json.load(file))
				dataPath.append(filePath)
		mapsLoaded += times
		print("Has loaded " + str(mapsLoaded) + " maps!\n")
		for i in range(times):
			currentMap += 1
			progress = ((currentMap - 1) / totalMaps) * 100
			ctypes.windll.kernel32.SetConsoleTitleW("Map {0} of {1} - {2}%".format(currentMap, totalMaps, progress))
			for path, value, key in recursive_items(data[i], dataPath[i]):
				if key == "message":
					messages += 1
					print("Found message: " + str(messages) + "!")
					print(key + ":", value["en_US"])
					dialogueData["messages"][0].append(value); dialogueData["messages"][1].append(path)
					print(dialogueData["messages"][1][-1] + "\n")
				if key == "text":
					if type(value) is dict:
						texts += 1
						print("Found text: " + str(texts) + "!")
						print(key + ":", value["en_US"])
						dialogueData["texts"][0].append(value); dialogueData["texts"][1].append(path)
						print(dialogueData["texts"][1][-1] + "\n")
				elif key == "options":
					a = -1
					for obj in value:
						a += 1
						if "label" in obj:
							labels += 1
							print("Found label: " + str(labels) + "!")
							print("label" + ":", obj["label"]["en_US"])
							dialogueData["labels"][0].append(obj["label"]); dialogueData["labels"][1].append(path + "[" + str(a) +"]['label']")
							print(dialogueData["labels"][1][-1] + "\n")
				elif key == "person":
					if type(value) is dict:
						person = value["person"]
						if (person in dialogueData["faces"][0]) == False:
							faces += 1
							print("Found face: " + str(faces) + "!")
							print(key + ": " + person)
							dialogueData["faces"][0][person] = []
							dialogueData["faces"][1][person] = []
						dialogueData["faces"][0][person].append(value); dialogueData["faces"][1][person].append(path)
						print(dialogueData["faces"][1][person][-1] + "\n")
		data = []
		dataPath = []			

		print("Data extracted!\n")

	try:
		with open('data/dialogueData.json', 'w') as outfile:
			json.dump(dialogueData, outfile, sort_keys=True, indent=4)
	except:
		os.mkdir("data")
		with open('data/dialogueData.json', 'w') as outfile:
			json.dump(dialogueData, outfile, sort_keys=True, indent=4)

	print("done")

	while True:
		None
		
		
if __name__ == '__main__':
	main()
