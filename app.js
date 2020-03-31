var express = require("express")
var fs = require("fs")
var bodyParser = require('body-parser');
var pythonShell = require("python-shell")
var convert = require('xml-js');
var sleep = require('system-sleep');
var path = require('path');
var archiver = require('archiver')
var expZip = require('express-zip');

var app = express();

app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies

// var valueMap;
var xml_result;
var valueMap = "";
var filename;
var projectname;
var folders = "";
var files = "";

app.listen(3030, function () {
    console.log("Listening at port 3030");
})

app.use(express.static(__dirname + "/public"))

app.get("/", function (request, response) {
    response.sendFile(__dirname + "/public/index.html");
})

app.get('/download', function (request, response) {
    // var save_zip_files = __dirname + "/public/files/zipfiles/" + projectname + "_" + filename.slice(0, -4) + ".zip";
    // console.log(save_zip_files);
    // response.download(save_zip_files);

    var save_name_bdd = __dirname + "/public/files/bdd/" + projectname + "_" + filename.slice(0, -4) + ".txt";
    var save_name_pairwise = __dirname + "/public/files/pairwise/" + projectname + "_" + filename.slice(0, -4) + ".txt";

    var file1 = "./public/files/bdd/" + projectname + "_" + filename.slice(0, -4) + ".txt"
    var file2 = "./public/files/pairwise/" + projectname + "_" + filename.slice(0, -4) + ".txt"
    var file3 = "./public/files/pairwise/" + projectname + "_" + filename.slice(0, -4) + ".xml"

    response.zip([
        { path: file1, name: 'bdd.txt' },
        { path: file2, name: 'pairwise.txt' },
        { path: file3, name: 'testValue.xml'}
    ]);

});

app.post('/py', function (request, response) {
    console.log("At py");
    var n = request.body.n_gc;
    var fn = request.body.filename_gc;

    // var fileName = "regexJSON.json"
    //valueMap = request.body.vm;
    //console.log(valueMap);

    var path = __dirname + "/public/files/Graph_json/" + projectname + "_" + fn.slice(0, -4) + ".json";
    var save_name_bdd = __dirname + "/public/files/bdd/" + projectname + "_" + filename.slice(0, -4) + ".txt";
    var save_name_pairwise = __dirname + "/public/files/pairwise/" + projectname + "_" + filename.slice(0, -4) + ".txt";
    var save_xml_files = __dirname + "/public/files/pairwise/" + projectname + "_" + filename.slice(0, -4) + ".xml";

    var options = {
        scriptPath: './public/pythonScript/pairwise',
        args: [path, save_name_bdd, save_name_pairwise, save_xml_files, n]
    };

    pythonShell.run('jsonParser.py', options, function (err, data) {
        if (err) throw err;
        // response.send(data)
    });

});

app.get('/getvalueMap', function (request, response) {
    //console.log(xml_result);
    response.send(valueMap);
})

app.get('/getXMLString', function (request, response) {
    //console.log(xml_result);
    response.send(xml_result);
})

app.get('/getFile', function (request, response) {
    //console.log(xml_result);
    response.send(filename);
})

app.get('/getProject', function (request, response) {
    //console.log(xml_result);
    response.send(projectname);
})

app.post("/save", function (request, response) {
    xml_result = request.body.xml_data;
    xml_result = xml_result.replace(/"/g, "'");
    valueMap = request.body.valuemap;
    console.log("in the save: " + valueMap);
    // console.log(""+xml_result)
    // console.log(close)

    //console.log(""+ projectname+"/"+filename);
    fs.writeFileSync("./public/files/values/" + projectname + "_" + filename.slice(0, -4) + ".txt", valueMap, function (err) {
        if (err) throw err;
    });

    fs.writeFileSync("./public/files/Server/" + projectname + "/" + filename, xml_result, function (err) {
        if (err) throw err;
    });


    var options = { ignoreComment: true, alwaysChildren: false };
    var json_result = convert.xml2json(xml_result, options); // or convert.xml2json(xml, options)
    fs.writeFileSync("./public/files/Graph_json/" + projectname + "_" + filename.slice(0, -4) + ".json", json_result, function (err) {
        if (err) throw err;
    });


})

app.get("/open_folders", function (request, response) {
    folders = fs.readdirSync("./public/files/Server/");
    //console.log(folders);
    response.send(folders);
})

app.get("/open_files", function (request, response) {
    var folder_name = request.query.folder_name;
    files = fs.readdirSync("./public/files/Server/" + folder_name + "/");
    //console.log(files);
    response.send(files);
    
    response.sendFile(__dirname + "/public/index.html");
})

app.get('/close', function (request, response) {
    //console.log("Getting /open");
    filename = request.query.filename;
    projectname = request.query.projectname;
    xml_result = request.query.xmlText;
    response.sendFile(__dirname + "/public/index.html");
});

app.get('/open', function (request, response) {
    //console.log("Getting /open");
    filename = request.query.filename;
    projectname = request.query.projectname;
    try{
        valueMap = fs.readFileSync("./public/files/values/" + projectname + "_" + filename.slice(0, -4) + ".txt");
    }
    catch(error)
    {
        //console.log(error);
    }
    finally{
        xml_result = fs.readFileSync("./public/files/Server/" + projectname + '/' + filename);
        //console.log(xml_result);
        response.sendFile(__dirname + "/public/index.html");
    }
   
    // xml_result = fs.readFileSync("./public/files/Server/" + projectname + '/' + filename);
    // //console.log(xml_result);
    // response.sendFile(__dirname + "/public/index.html");
});

app.post('/new', function (request, response) {
    projectname = request.body.projectname;
    filename = request.body.filename + ".xml"; 
    //console.log(""+projectname+"/"+filename);
    projectpath = "./public/files/Server/" + projectname;
    //console.log(projectpath);
    xml_result = "";
    if (!fs.existsSync(projectpath)) {
        //console.log("New folder");
        fs.mkdirSync(projectpath);
    }
    fs.writeFileSync("./public/files/Server/" + projectname + "/" + filename, xml_result, function (err) {
        if (err) throw err;
    });
    response.sendFile(__dirname + "/public/index.html");
})

//creating a new shared file
app.post('/shared_new', function (request, response) {
    var s_projectname = request.body.projectname;
    var s_filename = request.body.filename + ".xml"; 
    //console.log(""+projectname+"/"+filename);
    var s_projectpath = "./public/files/Server/" + s_projectname;
    //console.log(projectpath);
    var s_xml_result = "";
    if (!fs.existsSync(s_projectpath)) {
        //console.log("New folder");
        fs.mkdirSync(s_projectpath);
    }
    fs.writeFileSync("./public/files/Server/" + s_projectname + "/" + s_filename, s_xml_result, function (err) {
        if (err) throw err;
    });
    //response.sendFile(__dirname + "/public/index.html");
})