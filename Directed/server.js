var express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
var cors = require('cors')
let {PythonShell} = require('python-shell')
var app = express();
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true }));
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');
app.use(cors())


app.listen(5000, function () {
  console.log('server running on port 5000');
})

app.get('/', function (req, res) {
  res.render('dashboard.html');
})

app.post('/api/googleSEO', googleCall);

function googleCall(req, res) {

  let options = {
    mode: 'text',
    pythonOptions: ['-u'], // get print results in real-time
    args: [req.body.post]
  };
  PythonShell.run('googleSEO.py', options, function (err,results) {
    if (err) throw err;
    console.log('finished');
    console.log(results);
    res.send(results);
  });
}


app.post('/api/LSI', lsiCall);

function lsiCall(req, res) {

  let options = {
    mode: 'text',
    pythonOptions: ['-u'], // get print results in real-time
    args: [req.body.post]
  };
  PythonShell.run('LSI.py', options, function (err,results) {
    if (err) throw err;
    console.log('finished');
    console.log(results);
    res.send(results);
  });
}

