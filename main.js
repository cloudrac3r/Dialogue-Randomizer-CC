const fs = require("fs");;
const path = require("path");
const pj = path.join;

class File {
    constructor(filename, parent) {
        this.filename = filename;
        this.parent = parent;
    }
    lowername() {
        return this.filename.toLowerCase();
    }
    path() {
        if (!this.parent) return [this.filename];
        else return this.parent.path().concat([this.filename]);
    }
    pathString() {
        return pj(...this.path());
    }
}

class Directory extends File {
    constructor(filename, parent) {
        super(filename, parent);
        this.children = [];
    }
    populateChildren() {
        let subs = fs.readdirSync(this.pathString());
        for (let s of subs) {
            if (fs.statSync(pj(this.pathString(), s)).isDirectory()) {
                let newObject = new Directory(s, this);
                this.children.push(newObject);
                newObject.populateChildren();
            } else {
                let newObject = new File(s, this);
                this.children.push(newObject);
            }
        }
	}
	allChildren() {
		let result = [];
		for (let child of this.children) {
			if (child.constructor.name == "File") {
				result.push(child.pathString());
			} else {
				result.push(...child.allChildren());
			}
		}
		return result;
	}
}

Object.prototype.recursiveItems = function(path) {
	if (!path) path = "";
	let result = [];
	for (let key of Object.keys(this)) {
		result.push([path+"."+key, this[key], key]);
		if (typeof(this[key]) == "object" && this[key]) {
			result = result.concat(this[key].recursiveItems(path+"."+key));
		}
	}
	return result;
}

Array.prototype.shuffle = function(generator) {
	let result = [];
	let copy = [...this];
	while (copy.length) {
		result.push(copy.splice(generator.range(copy.length), 1)[0]);
	}
	return result;
}

function propertyPathToList(p) {
	let list = [];
	let i = 0;
	let word = "";
	let quotesOpen = false;
	while (i < p.length) {
		if (p[i] == ".") {
			list.push(word);
			word = "";
			i++;
		} else if (p[i] == "[") {
			list.push(word);
			word = "";
			i++;
			if (p[i] == `"` || p[i] == `'`) {
				quotesOpen = true;
				i++;
			}
		} else if (quotesOpen && (p[i] == `"` || p[i] == `'`)) {
			quotesOpen = false;
			i++;
		} else if (p[i] == "]") {
			if (p[i+1] != "[") {
				list.push(word);
				word = "";
			}
			i++;
		} else {
			word += p[i];
			i++;
		}
	}
	if (word) list.push(word);
	return list;
}

Object.prototype.sp = function(p) {
	let list = propertyPathToList(p).slice(0, -1);
	let result = this;
	list.forEach(p => {
		if (result) result = result[p];
		else result = undefined;
	});
	return result;
}

function log(text, type, newline) {
	let enabledLogs = ["process"];
	if (!type || enabledLogs.includes(type)) {
		if (newline !== false) console.log(text);
		else process.stdout.write(text);
	}
}

(async function() {
	console.log("Type a seed to use, or just press enter for a random seed.");
	log("> ", undefined, false);
	let seed = await new Promise(resolve => {
		let resolver = data => {
			process.stdin.removeListener("data", resolver);
			resolve(data.toString().split("\n")[0]);
		}
		process.stdin.on("data", resolver);
		//resolver("\n");
	});
	let rs = require("random-seed");
	let gen;
	if (!seed) gen = rs.create();
	else gen = rs.create(seed);
	log("Loading dialogue data... ", "process", false);
	let dialogueData = require("./data/dialogueData.json");
	log("done.", "process");
	log("Shuffling... ", "process", false);
	dialogueData.labels[0] = dialogueData.labels[0].shuffle(gen);
	dialogueData.messages[0] = dialogueData.messages[0].shuffle(gen);
	dialogueData.texts[0] = dialogueData.texts[0].shuffle(gen);
	// should probably shuffle faces as well
	log("done.", "process");

	let dirName = './input/maps/';
	let base = new Directory(dirName, null);
	base.populateChildren();
	let listOfFiles = base.allChildren();

	let mapsLoaded = 0;
	let totalMaps = listOfFiles.length;
	let currentMap = 0;
	let dataPath = [];
	let messages = 0;
	let texts = 0;
	let labels = 0;
	let faces = 0;
	let data = {}
	let outputPath = []
	let filePath = ""

	log("Loading maps... ", "process", false);
	for (let filePath of listOfFiles) {
		dataPath.push(filePath);
		temp = "";
		for (let obj of filePath.split("/")) {
			if (obj == "input") temp = "output/RandomizedDialogue/assets/data";
			else temp += "/" + obj;
		}
		outputPath.push(temp)
		data[filePath] = require("./"+filePath);
	}
	log("done.", "process");

	log("Rewriting... ", "process", false);
	for (let key of Object.keys(dialogueData)) {
		let value = dialogueData[key];
		/*if (key == "faces") {
			for key2, value2 in value[0].items():
				i = 0
				for obj in value2:
					exec("global data; data['" + dialogueData["faces"][1][key2][i].split("[")[0] + "']["+dialogueData["faces"][1][key2][i].split("[", 1)[1]+" = " + str(obj), globals(), {"data": data})
				i += 1
		} else*/
		for (let i = 0; i < value[0].length; i++) {
			let location = dialogueData[key][1][i];
			let path = location.split(".json.")[0]+".json";
			let keys = location.split(".json.")[1];
			if (data[path]) {
				if (keys.endsWith("]")) debugger;
				data[path].sp(keys)[propertyPathToList(keys).slice(-1)[0]] = value[0][i];
			} else {
				console.log("data[path] is undefined: ", path, location);
			}
		}
	}
	log("done.", "process");

	log("Saving... ", "process", false);
	let exists = [];
	await Promise.all(Object.keys(data).map(key =>
		new Promise((resolve, reject) => {
			let outputKey = key.replace("input", "output/RandomizedDialogue/assets/data")
			let path = outputKey.split("/");
			for (let i = 1; i < path.length; i++) {
				let sub = path.slice(0, i).join("/");
				if (!exists.includes(sub)) {
					if (!fs.existsSync(sub)) fs.mkdirSync(sub);
					exists.push(sub);
				}
			}
			fs.writeFile(outputKey, JSON.stringify(data[key]), err =>
				err ? reject() : resolve()
			)
		})
	));
	log("done.", "process");
	setTimeout(() => process.exit(), 500); // something about process.stdin makes it not exit on its own idk
})();