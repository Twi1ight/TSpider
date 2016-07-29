/**
 * Created by John on 2016/7/28.
 * http://blog.wils0n.cn/?post=18
 */
var utils = require('utils');

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
    var exclude_filter = ['a3c', 'ace', 'aif', 'aifc', 'aiff', 'arj', 'asf', 'asx', 'attach', 'au',
        'avi', 'bin', 'cab', 'cache', 'class', 'djv', 'djvu', 'dwg', 'es', 'esl',
        'exe', 'fif', 'fvi', 'gz', 'hqx', 'ice', 'ief', 'ifs', 'iso', 'jar', 'kar',
        'mid', 'midi', 'mov', 'movie', 'mp', 'mp2', 'mp3', 'mp4', 'mpeg',
        'mpeg2', 'mpg', 'mpg2', 'mpga', 'msi', 'pac', 'pdf', 'ppt', 'pptx', 'psd',
        'qt', 'ra', 'ram', 'rm', 'rpm', 'snd', 'svf', 'tar', 'tgz', 'tif',
        'tiff', 'tpl', 'uff', 'wav', 'wma', 'wmv', 'doc', 'docx', 'db', 'jpg'];
    var url = requestData.url;
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
    var ret = [];

    var urls = this.evaluate(function () {
        var urls = [];

        function fillForm(form) {

        }

        function getForm() {
            var f = document.forms;
            for (var i = 0; i < f.length; i++) {
                var form = f[i];
                var url = form.action;
                var inputs = form.getElementsByTagName('input');
                var requestdata = {};
                //without submit
                var len = inputs.length - 1;
                var has_button = false, has_submit = false;
                for (var j = 0; j < inputs.length; j++) {
                    var obj = inputs[j];
                    if (!obj.hasAttribute('type')) {
                        continue
                    }
                    if (obj.type == 'submit') {
                        has_submit = true;
                        continue
                    }
                    //if (inputs[j].type == 'button') {
                    //    inputs[j].click();
                    //    hash_button = true;
                    //}
                    if (obj.hasAttribute('value') && obj.value) {
                        requestdata[obj.name] = obj.value;
                        continue
                    }
                    switch (obj.type) {
                        case 'text':
                            // todo username, email, address, checkcode etc.
                            if (obj.name.indexOf('user') >= 0) {
                                requestdata[obj.name] = 'mazafaka'
                            } else if (obj.name.indexOf('mail') >= 0) {
                                requestdata[obj.name] = 'fakamaza@yopmail.com'
                            } else {
                                var length = 10;
                                if (obj.maxlength > 0) {

                                    requestdata[obj.name] = Math.random().toString(36).slice(2).substring(0, 10)
                                } else {

                                }
                            }
                            break;
                        case 'password':
                            break;
                        case 'email':
                            requestdata[obj.name] = 'fakamaza@yopmail.com';
                            break;
                        case ''

                    }
                    if (j < len - 1) {
                        requestdata = requestdata + inputs[j].name + "=" + inputs[j].value + "&";
                    }
                    if (j == len - 1) {
                        requestdata = requestdata + inputs[j].name + "=" + inputs[j].value;
                    }
                }
                res = "hook_url:{\"url\":\"" + url + "\",\"method\":\"post\"," + "\"post\":\"" + requestdata + "\",\"Referer\":\"" + window.location.href + "\"}hook_url_end";
                if (urls.indexOf(res) < 0) {
                    urls.push(res);
                    console.log(res);
                }
            }
        }

        function handleTag(tag, src) {
            var elements = document.getElementsByTagName(tag);
            for (var i = 0; i < elements.length; i++) {
                var method, referer, value;
                method = 'GET';
                referer = window.location.href;
                value = elements[i][src];
                if (urls.indexOf(value) < 0 && !black_protocol(value)) {
                    urls.push(value);
                }
            }
        }

        //get href
        function getallurl() {
            //GetForm();
            handleTag('a', 'href');
            handleTag('link', 'href');
            handleTag('area', 'href');
            handleTag('img', 'src');
            handleTag('embed', 'src');
            handleTag('video', 'src');
            handleTag('audio', 'src');
        }

        function black_protocol(url) {
            var schemes = ['javascript:', 'mailto:', 'irc:', 'tencent:', 'magnet:', 'thunder:',
                'qqdl:', 'flashget:', 'ed2k:'];
            for (var i = 0; i < schemes.length; i++) {
                if (url.startsWith(schemes[i])) {
                    return true
                }
            }
            return false
        }

        getallurl();
        return urls;
    });
    for (var url in urls) {
        console.log(urls[url]);
    }
});

casper.run();