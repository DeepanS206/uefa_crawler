var system = require('system')
var page = require('webpage').create()

setTimeout(function() {
  page.open(system.args[1], function()
    {
      console.log(page.content);
      phantom.exit();
    }
)}(), 20000);