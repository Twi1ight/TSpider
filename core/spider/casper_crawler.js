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
var init_url, result_file, cookie_file, requested_count = 0, static_urls = [], requested_urls = [];
var first_page_request = true;
var max_frames = 0;
var done_frames = 0;
var timeout = 90000;
var casper = require('casper').create({
    //clientScripts: [
    //    'jquery-2.2.4.min.js'      // These two scripts will be injected in remote
    //    'includes/underscore.js'   // DOM on every request
    //],
    viewportSize: {width: 800, height: 600},
    timeout: timeout,
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
    if (casper.cli.has('output-file')) {
        result_file = casper.cli.get('output-file');
    }
    if (casper.cli.has('cookie-file')) {
        cookie_file = casper.cli.get('cookie-file')
    }
} else {
    casper.echo('usage: crawler.js http://foo.bar [--output-file=output.txt] [--cookie-file=cookie.txt]', 'INFO');
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

//page.resource.requested   Emitted when a new HTTP request is performed to open the required url.
//resource.requested        Emitted when any resource has been requested.
casper.on('page.resource.requested', function (requestData, request) {
    if (first_page_request) {
        first_page_request = false
    } else {
        request.abort();
    }
    //will continue to trigger resource.requested
});

casper.on('resource.requested', function (requestData, request) {
    requested_count++;
    //this.echo(JSON.stringify(requestData),'INFO');
    //utils.dump(requestData);
    requested_urls.push(JSON.stringify(requestData));
    var url = requestData.url;
    if (core.evilResource(url)) {
        this.echo(url + ' forbiden', 'ERROR');
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
    var prefix = 'tspider://';
    if (msg.substr(0, prefix.length) === prefix) {
        var data = JSON.parse(msg.substr(prefix.length));
        var frame = data['frame'];
        var urls = data['urls'];
        this.echo(frame + ' got ' + urls.length + ' urls.', 'INFO');
        for (var i = 0; i < urls.length; i++) {
            static_urls.push(urls[i])
        }
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
    this.evaluate(core.FireintheHole, 'mainframe')
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
                this.evaluate(core.FireintheHole, 'iframe')
            })
        }
    }
});

casper.wait(timeout, function () {
    this.echo('casper_crawler timeout!', 'ERROR');
});

casper.run();