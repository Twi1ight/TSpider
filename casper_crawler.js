/**
 * Created by John on 2016/7/28.
 * http://blog.wils0n.cn/?post=18
 */
var casper = require('casper').create({
    //clientScripts:  [
    //    'includes/jquery.js',      // These two scripts will be injected in remote
    //    'includes/underscore.js'   // DOM on every request
    //],
    pageSettings: {
        loadImages: false,        // The WebPage instance used by Casper will
        loadPlugins: false         // use these settings
    },
    logLevel: "info",              // Only "info" level messages will be logged
    verbose: true                  // log messages will be printed out to the console
    //onAlert: function (message) {
    //}
});

//navigation.requested   //Available navigation types are: LinkClicked, FormSubmitted, BackOrForward, Reload, FormResubmitted and Other.
//page.resource.requested   //Emitted when a new HTTP request is performed to open the required url.
//resource.requested    //Emitted when any resource has been requested.
casper.on('page.resource.requested', function (requestData, request) {
    //if (requestData.url.indexOf('http://adserver.com') === 0) {
    //    request.abort();
    //}
    //todo filter black extension
    //console.log(JSON.stringify(requestData));
    //console.log('page.resource.requested');
    //this.echo(requestData.url);
});

casper.on('resource.requested', function (request) {
    //console.log(JSON.stringify(request));
    console.log('resource.requested');
    this.echo(request.method + '|||' + request.url + '|||' + request.postData)
});

casper.on('remote.alert', function (message) {
    this.echo('alert message: ' + message);
});

casper.start('http://demo.aisec.cn/demo/aisec/');

casper.then(function () {
    var urls = this.evaluate(function () {
        var urls = [];

        function handle_tag(tag, src) {
            var elements = document.getElementsByTagName(tag);
            console.log(elements);
            for (var i = 0; i < elements.length; i++) {
                //res = "hook_url:{\"url\":\"" + elements[i][src] + "\",\"method\":\"get\",\"post\":\"\"" + ",\"Referer\":\"" + window.location.href + "\"}hook_url_end";
                res = elements[i][src];
                if (urls.indexOf(res) < 0 && elements[i][src].indexOf("javascript:") < 0 && elements[i][src].indexOf("mailto:") < 0) {
                    urls.push(res);
                    //console.log(res);
                }
            }
        }

        //get href
        function getallurl() {
            //GetForm();
            handle_tag('a', 'href');
            handle_tag('link', 'href');
            handle_tag('area', 'href');
            handle_tag('img', 'src');
            handle_tag('embed', 'src');
            handle_tag('video', 'src');
            handle_tag('audio', 'src');
        }

        getallurl();
        return urls;
    });
    for (var url in urls) {
        console.log(urls[url]);
    }
});

casper.run();