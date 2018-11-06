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

function log(text, type, newline) {
	let enabledLogs = ["progress", "labels", "faces"];
	if (enabledLogs.includes(type)) {
		if (newline !== false) console.log(text);
		else process.stdout.write(text);
	}
}

let dirName = './input/maps/';

// Get the list of all files in directory tree at given path;
let base = new Directory(dirName, null);
base.populateChildren();
let listOfFiles = base.allChildren();

let mapsLoaded = 0;
let totalMaps = listOfFiles.length;
let currentMap = 0;
let messages = 0;
let faces = 0;
let labels = 0;
let texts = 0;
let data = [];
let dataPath = [];
let dialogueData = {
	"messages": [[], []],
	"texts": [[], []],
	"faces": [{}, {}],
	"labels": [[], []]
};

const batchSize = 50;

while (listOfFiles.length != 0) {
	if (listOfFiles.length < batchSize) {
		times = listOfFiles.length;
	} else {
		times = batchSize;
	}
	log("Loading... ", "process", false);
	for (let i = 0; i < times; i++) {
		filePath = listOfFiles.pop();
		data.push(require("./"+filePath));
		dataPath.push(filePath);
	}
	log(`done. (${data.length}, ${mapsLoaded += times})`, "process");
	for (let i = 0; i < times; i++) {
		currentMap++;
		progress = ((currentMap - 1) / totalMaps) * 100;
		log(`Map ${currentMap} of ${totalMaps} - ${progress.toFixed(2)}%`, "progress");
		log("Recursing... ", "process", false);
		let recursiveItems = data[i].recursiveItems(dataPath[i]);
		log("done.", "process");
		log("Searching... ", "process", false);
		for (let [path, value, key] of recursiveItems) {
			if (key == "message") {
				messages += 1;
				log("Found message: "+messages+"!", "messages");
				log(key + ":", value["en_US"], "messages");
				dialogueData["messages"][0].push(value); dialogueData["messages"][1].push(path);
				log(dialogueData["messages"][1].slice(-1)[0] + "\n", "messages");
			} else if (key == "text") {
				if (typeof(value) == "object" && value.constructor.name == "Object") {
					texts += 1;
					log("Found text: "+texts+"!", "texts");
					log(key + ":", value["en_US"], "texts");
					dialogueData["texts"][0].push(value); dialogueData["texts"][1].push(path);
					log(dialogueData["texts"][1].slice(-1)[0] + "\n", "texts");
				}
			} else if (key == "options") {
				a = -1;
				for (let obj of value) {
					a += 1;
					if (obj.label) {
						labels += 1;
						log("Found label: "+labels+"!", "labels");
						log("label" + ":", obj["label"]["en_US"], "labels");
						dialogueData["labels"][0].push(obj["label"]); dialogueData["labels"][1].push(path + "["+a+"]['label']");
						log(dialogueData["labels"][1].slice(-1)[0] + "\n", "labels");
					}
				}
			} else if (key == "person") {
				if (typeof(value) == "object" && value.constructor.name == "Object") {
					person = value["person"];
					if (!Object.values(dialogueData["faces"][0]).includes(person)) {
						faces += 1;
						log("Found face: "+faces+"!", "faces");
						log(key + ": " + person, "faces");
						dialogueData["faces"][0][person] = []
						dialogueData["faces"][1][person] = []
					}
					dialogueData["faces"][0][person].push(value); dialogueData["faces"][1][person].push(path);
					log(dialogueData["faces"][1][person].slice(-1)[0] + "\n", "faces");
				}
			}
		}
		log("done.", "process");
	}
	data = []
	dataPath = []
}
if (!fs.existsSync("data")) fs.mkdirSync("data");
fs.writeFile("data/dialogueData.json", JSON.stringify(dialogueData, null, 4), err => {
	if (!err) console.log("All done!");
	else throw err;
});