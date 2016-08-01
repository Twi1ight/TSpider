/**
 * Created by John on 2016/7/28.
 * http://blog.wils0n.cn/?post=18
 *
 *  casperjs --ignore-ssl-errors=true --ssl-protocol=any casper_crawler.js http://foo.bar outfile
 */
'use strict';
var core = require('./core');
var utils = require('utils');
var result_file, requested_count = 0, static_urls = [], requested_urls = [];
var casper = require('casper').create({
    //clientScripts: [
    //    'jquery-2.2.4.min.js'      // These two scripts will be injected in remote
    //    'includes/underscore.js'   // DOM on every request
    //],
    viewportSize: {width: 800, height: 600},
    timeout: 90000,
    pageSettings: {
        loadImages: false,        // The WebPage instance used by Casper will
        loadPlugins: false,         // use these settings
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11"

    },
    logLevel: "debug",               // Only "info" level messages will be logged
    verbose: false                   // log messages will be printed out to the console
});

if (casper.cli.has(0)) {
    var init_url = casper.cli.get(0);
    if (casper.cli.has(1)) {
        result_file = casper.cli.get(1)
    }
} else {
    console.log('usage: crawler.js url [outfile]');
    casper.exit()
}

//page.resource.requested   //Emitted when a new HTTP request is performed to open the required url.
//resource.requested        //Emitted when any resource has been requested.
casper.on('page.resource.requested', function (requestData, request) {
    var url = requestData.url;
    if (core.evilResource(url)) {
        request.abort()
    }
});

casper.on('resource.requested', function (requestData, request) {
    requested_count++;
    //console.log(JSON.stringify(requestData));
    //utils.dump(requestData);
    requested_urls.push(JSON.stringify(requestData));
    var url = requestData.url;
    if (core.evilResource(url)) {
        this.echo('forbiden', 'ERROR');
        request.abort()
    }
});

// hook window.open
casper.on('popup.created', function (newpage) {
    this.echo("url popup created", "INFO");
    newpage.onResourceRequested = function (requestData, request) {
        requested_count++;
        requested_urls.push(JSON.stringify(requestData));
        casper.echo('popup onResourceRequested: ' + requestData.url, 'INFO');
        //abort current request, important!
        request.abort();
    };
});

casper.on('remote.alert', function (message) {
    //this.echo('alert message: ' + message);
});

casper.on('remote.message', function (msg) {
    this.echo('remote message caught: ' + msg, 'INFO');
});

casper.on('exit', function () {
    if (result_file) {
        this.echo('save urls to ' + result_file, 'INFO');
    }
    core.saveFile(static_urls, requested_urls, result_file)
});

casper.start(init_url);

casper.userAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X)');

casper.then(function () {
    var urls = [];
    var iframe_count = this.page.childFramesCount();
    console.log('find ' + iframe_count + ' iframes');
    var max_frames = iframe_count < 10 ? iframe_count : 10;
    for (var index = 0; index < max_frames; index++) {
        this.withFrame(index, function () {
            urls = this.evaluate(core.FireintheHole);
            console.log('frame got ' + urls.length + ' urls.');
            for (var i = 0; i < urls.length; i++) {
                //console.log('frame[' + index + '] ' + urls[i]);
                static_urls.push(urls[i]);
            }
        })
    }
});

casper.then(function () {
    var urls = [];
    console.log('mainframe evaluate');
    urls = this.evaluate(core.FireintheHole);
    console.log('mainframe got ' + urls.length + ' urls.');
    //utils.dump(urls);
    for (var i = 0; i < urls.length; i++) {
        //console.log('mainframe ' + urls[i]);
        static_urls.push(urls[i]);
    }
});

casper.then(function () {
    console.log('requested count ' + requested_count);
});

casper.run();