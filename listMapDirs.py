import os
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


def recursive_items(dictionary):
	for key, value in dictionary.items():
		if type(value) is dict:
			yield (key, value)
			yield from recursive_items(value)
		elif type(value) is list:
			yield (key, value)
			yield from recursive_items(value)
		else:
			yield (key, value)


def main():

	dirName = 'input/maps/'

	# Get the list of all files in directory tree at given path
	listOfFiles = getListOfFiles(dirName)

	for i in range(len(listOfFiles)):
		b = pathlib.PureWindowsPath(listOfFiles[i])
		listOfFiles[i] = b.as_posix()

	# Print the files
	for elem in listOfFiles:
		print(elem)
	print()
	print(
		"The",
		dirName.split("\\")[-2],
		"folder contains",
		listOfFiles.__len__(),
		"files",
		sep = " ",
		end="\n\n"
	)

	while True:
		None


if __name__ == '__main__':
	main()
