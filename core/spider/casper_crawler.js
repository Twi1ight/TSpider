/**
 * Created by John on 2016/7/28.
 * http://blog.wils0n.cn/?post=18
 *
 *  casperjs --ignore-ssl-errors=true --ssl-protocol=any casper_crawler.js http://foo.bar outfile
 */
'use strict';
var user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11"
var core = require('./core');
var utils = require('utils');
var fs = require('fs');
var init_url, result_file, cookie_file, requested_count = 0, static_urls = [], requested_urls = [];
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
        userAgent: user_agent
    },
    logLevel: "info",               // Only "info" level messages will be logged
    verbose: false                   // log messages will be printed out to the console
});


if (casper.cli.args.length === 1) {
    init_url = casper.cli.get(0);
    if (casper.cli.has('output-file')) {
        result_file = casper.cli.get('output-file');
    }
    if (casper.cli.has('cookie-file')) {
        cookie_file = casper.cli.get('cookie-file')
    }
} else {
    console.log('usage: crawler.js http://foo.bar [--output-file=output.txt] [--cookie-file=cookie.txt]');
    casper.exit()
}

if (!!cookie_file) {
    try {
        if (fs.exists(cookie_file)) {
            var content = fs.read(cookie_file);
            var cookies = JSON.parse(content);
            cookies.forEach(function (cookie) {
                //console.log(JSON.stringify(cookie));
                var ret = phantom.addCookie(cookie);
                if (ret === false) {
                    casper.echo('addCookie failed: ' + JSON.stringify(cookie), 'INFO')
                }
            });
        } else {
            casper.echo('cookie file ' + filename + 'not found!', 'ERROR');
            casper.exit();
        }
    } catch (exception) {
        casper.echo(exception, 'ERROR')
    }
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
casper.on('popup.created', function (popup) {
    this.echo("url popup created", "INFO");
    // casperjs setting user-agent not working in popups
    // https://github.com/casperjs/casperjs/issues/1662
    popup.settings.userAgent = user_agent;
    popup.onResourceRequested = function (requestData, request) {
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
    if (!!result_file) {
        this.echo('save urls to ' + result_file, 'INFO');
    }
    core.saveFile(static_urls, requested_urls, result_file)
});

casper.start(init_url);

casper.then(function () {
    var urls = [];
    var iframe_count = this.page.childFramesCount();
    console.log('find ' + iframe_count + ' iframes');
    var max_frames = iframe_count < 100 ? iframe_count : 100;
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

casper.wait(1000, function () {
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

casper.wait(1000, function () {
    console.log('wait for mainframe ends');
    console.log('requested count ' + requested_count);
});

casper.run();