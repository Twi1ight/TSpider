/**
 * Created by Twi1ight on 2016/7/28.
 * http://blog.wils0n.cn/?post=18
 *
 *  casperjs --ignore-ssl-errors=true --ssl-protocol=any casper_crawler.js http://foo.bar outfile
 */
'use strict';
var user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11";
var core = require('./core');
var utils = require('utils');
var fs = require('fs');
var init_url, result_file, cookie_file, block_navigation_url;
var static_urls = [];
var requested_urls = [];
var max_frames = 0;
var done_frames = 0;
var requested_count = 0;
var time_per_event = 1000;
var casper_timeout = 120000;
var casper = require('casper').create({
    //clientScripts: [
    //    'jquery-2.2.4.min.js'      // These two scripts will be injected in remote
    //    'includes/underscore.js'   // DOM on every request
    //],
    viewportSize: {width: 800, height: 600},
    timeout: casper_timeout,
    pageSettings: {
        loadImages: false,           // The WebPage instance used by Casper will
        loadPlugins: false,          // use these settings
        webSecurity: false,
        userAgent: user_agent
    },
    sslProtocol: 'any',
    logLevel: 'info',                // Only "info" level messages will be logged
    verbose: false                   // log messages will be printed out to the console
});


if (casper.cli.args.length === 1) {
    init_url = casper.cli.get(0);
    if (casper.cli.has('output')) {
        result_file = casper.cli.get('output');
    }
    if (casper.cli.has('cookie')) {
        cookie_file = casper.cli.get('cookie')
    }
    if (casper.cli.has('casper_timeout')) {
        time_per_event = casper.cli.get('casper_timeout')
    }
} else {
    casper.echo('usage: crawler.js http://foo.bar [--output=output.txt] [--cookie=cookie.txt]', 'INFO');
    casper.exit()
}

if (!!cookie_file) {
    try {
        if (fs.exists(cookie_file)) {
            var content = fs.read(cookie_file);
            var cookies = JSON.parse(content);
            cookies.forEach(function (cookie) {
                //this.echo(JSON.stringify(cookie),'INFO');
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
//page.initialized          Emitted when PhantomJS’ WebPage object used by CasperJS has been initialized.
casper.on('page.initialized', function (WebPage) {
    WebPage.evaluate(core.AddMutationObserver)
});
// navigation.requested     Emitted each time a navigation operation has been requested.
// Available navigation types are: LinkClicked, FormSubmitted, BackOrForward, Reload, FormResubmitted and Other.
casper.on('navigation.requested', function (url, navigationType, willNavigate, isMainFrame) {
    if (navigationType !== "Other")
        block_navigation_url = url;
});

casper.on('resource.requested', function (requestData, request) {
    requested_count++;
    //this.echo(JSON.stringify(requestData),'INFO');
    //utils.dump(requestData);
    requested_urls.push(JSON.stringify(requestData));
    if (core.evilResource(requestData.url)) {
        request.abort()
    } else if (block_navigation_url === requestData.url) {
        block_navigation_url = null;
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
    var data_signal_prefix = 'tspider://data/';
    var exit_signal_prefix = 'tspider://exit/';
    if (msg.substr(0, data_signal_prefix.length) === data_signal_prefix) {
        var url = msg.substr(data_signal_prefix.length);
        static_urls.push(url);
    } else if (msg.substr(0, exit_signal_prefix.length) === exit_signal_prefix) {
        var frame = msg.substr(exit_signal_prefix.length);
        this.echo(frame, 'ERROR');
        if (frame === 'iframe') {
            if (++done_frames === max_frames) {
                this.emit('iframe.completed')
            }
        } else {
            casper.exit()
        }
    } else {
        this.echo('remote message caught: ' + msg, 'INFO');
    }
});

casper.on('iframe.completed', function () {
    this.echo('mainframe evaluate', 'INFO');
    this.evaluate(core.FireintheHole, 'mainframe', time_per_event)
});

casper.on('exit', function () {
    var urls_count = static_urls.length + requested_urls.length;
    this.echo('requests: ' + requested_count + ' urls: ' + urls_count, 'INFO');
    if (!!result_file) {
        this.echo('save urls to ' + result_file, 'INFO');
    }
    core.saveFile(static_urls, requested_urls, result_file)
});

casper.start();

casper.open(init_url, {
    method: 'get',
    headers: {
        'Referer': init_url
    }
});

casper.then(function () {
    var iframe_count = this.page.childFramesCount();
    this.echo('find ' + iframe_count + ' iframes', 'INFO');
    max_frames = iframe_count < 100 ? iframe_count : 100;
    if (max_frames === 0) {
        this.emit('iframe.completed')
    } else {
        for (var index = 0; index < max_frames; index++) {
            this.withFrame(index, function () {
                this.evaluate(core.FireintheHole, 'iframe', time_per_event)
            })
        }
    }
});

casper.wait(casper_timeout - 1000, function () {
    // casper.capture('casper_timeout.png');
    this.echo('casper_crawler casper_timeout!', 'ERROR');
});

casper.run();