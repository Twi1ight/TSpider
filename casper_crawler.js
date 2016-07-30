/**
 * Created by John on 2016/7/28.
 * http://blog.wils0n.cn/?post=18
 */
var utils = require('utils');

var casper = require('casper').create({
    //clientScripts: [
    //    'jquery-2.2.4.min.js'      // These two scripts will be injected in remote
    //    'includes/underscore.js'   // DOM on every request
    //],
    pageSettings: {
        loadImages: false,        // The WebPage instance used by Casper will
        loadPlugins: false         // use these settings
    },
    logLevel: "info",              // Only "info" level messages will be logged
    verbose: false                  // log messages will be printed out to the console
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
    var exclude_stastics = ['https?://hm.baidu.com/', ''];
    var url = requestData.url;
    //console.log(JSON.stringify(requestData));
    //console.log('page.resource.requested');
    //this.echo(requestData.url);
});
var requested_count = 0;
casper.on('resource.requested', function (request) {
    //console.log(JSON.stringify(request));
    console.log('resource.requested');
    requested_count++;
    this.echo(request.method + '|||' + request.url + '|||' + request.postData)
});

casper.on('remote.alert', function (message) {
    //this.echo('alert message: ' + message);
});

casper.on('remote.message', function (msg) {
    this.echo('remote message caught: ' + msg);
});

//casper.start('http://demo.aisec.cn/demo/aisec/');
//casper.start('http://192.168.88.128/test.html');
if (casper.cli.has(0)) {
    var init_url = casper.cli.get(0)
} else {
    console.log('usage: crawler.js url');
    casper.exit()
}
casper.start(init_url);

casper.then(function () {
    var ret = [];


    console.log('parent evaluate');
    var urls = this.evaluate(dirtywork);
    console.log('fuckthisparent' + urls.length);
    for (var i = 0; i < urls.length; i++) {
        console.log('fuckthisparent ' + urls[i]);
    }

    var iframe_amount = this.evaluate(function () {
        return window.frames.length
    });
    for (var index = 0; index < iframe_amount; index++) {
        this.withFrame(index, function () {
            var test = this.evaluate(dirtywork);
            console.log('fuck' + test.length);
            for (var i = 0; i < test.length; i++) {
                console.log('fuckthischilden ' + test[i]);
            }
        })
    }

});


function dirtywork() {
    var urls = [];
    //var retvar = [];
    function getForms() {
        var f = document.forms;
        var count = 0;
        for (var i = 0; i < f.length; i++) {
            console.log('form ' + i + ' total:' + f.length);
            count++;
            if (count == 10) {
                break
            }
            var form = f[i];
            var url = form.action;
            //if (urls.indexOf(url) >= 0) {
            //    continue
            //}
            //urls.push(url);
            var inputs = form.getElementsByTagName('input');
            console.log('get inputs length: ' + inputs.length);
            var requestdata = {};
            var has_button = false, has_submit = false, buttons = [];
            var length, submit, radio = false;
            for (var j = 0; j < inputs.length; j++) {
                var obj = inputs[j];
                //console.log(obj.name + ' ' + obj.type + ' ' + obj.value);
                if (!obj.hasAttribute('type')) {
                    continue
                }
                switch (obj.type) {
                    case 'radio':
                        if (!radio) {
                            radio = true;
                            obj.click();
                            requestdata[obj.name] = obj.value
                        }
                        continue;
                    case 'checkbox':
                        obj.click();
                        requestdata[obj.name] = obj.value;
                        continue;
                    case 'submit':
                        has_submit = true;
                        submit = obj;
                        if (obj.value) {
                            requestdata[obj.name] = obj.value;
                        }
                        continue;
                    case 'button':
                        has_button = true;
                        buttons.push(obj);
                        continue;
                }
                // use default value
                if (obj.value) {
                    requestdata[obj.name] = obj.value;
                    continue
                }
                // fill the form
                switch (obj.type) {
                    case 'text':
                        // username, email, address, checkcode etc.
                        if (obj.name.indexOf('user') >= 0) {
                            requestdata[obj.name] = 'mazafaka';
                            obj.value = 'mazafaka'
                        } else if (obj.name.indexOf('mail') >= 0) {
                            requestdata[obj.name] = 'fakamaza@yopmail.com';
                            obj.value = 'fakamaza@yopmail.com'
                        } else {
                            length = obj.maxLength > 0 ? obj.maxLength : 10;
                            var value = Math.random().toString(36).slice(2).substring(0, length);
                            requestdata[obj.name] = value;
                            obj.value = value
                        }
                        break;
                    case 'password':
                        requestdata[obj.name] = 'Passw0rd!@#';
                        obj.value = 'Passw0rd!@#';
                        break;
                    case 'email':
                        requestdata[obj.name] = 'fakamaza@yopmail.com';
                        obj.value = 'fakamaza@yopmail.com';
                        break;
                    // todo html5 input type
                    default:
                        length = obj.maxLength > 0 ? obj.maxLength : 10;
                        value = Math.random().toString(36).slice(2).substring(0, length);
                        requestdata[obj.name] = value;
                        obj.value = value
                }
            }
            var querystring = param(requestdata);
            var action = form.action ? form.action : form.baseURI;
            var formdata = form.method + '|||' + action + '|||' + querystring;
            console.log(formdata);
            if (querystring) {
                urls.push(formdata);
            }
            //if (urls.indexOf(res) < 0) {
            //    urls.push(res);
            //    console.log(res);
            //}
            for (var k = 0; k < buttons.length; k++) {
                buttons[k].click()
            }
            form.submit();
            //submit.click();
        }
    }

    function getEvents() {
        var events = [];
        var allElements, len;
        allElements = document.getElementsByTagName('*');
        len = allElements.length;// allElements will change,len will change
        for (var i = 0; i < len; i++) {
            //js_code
            if (allElements[i].href) {
                jscode = allElements[i].href.match("javascript:(.*)");
                if (jscode) {
                    if (events.indexOf(jscode[0]) < 0) {
                        events.push(jscode[0]);
                    }
                }
            }
            attrs = allElements[i].attributes;
            for (var j = 0; j < attrs.length; j++) {
                var name = attrs[j].name;
                var value = allElements[i][name];
                if (startsWith(name, 'on') && typeof(value) === 'function') {
                    //console.log(name);
                    if (events.indexOf(value) < 0) {
                        events.push(value)
                    }
                }
            }
        }
        for (var k = 0; k < events.length; k++) {
            try {
                if (typeof events[k] === 'string') {
                    eval(events[k])
                } else if (typeof events[k] === 'function') {
                    events[k]();
                }
                getStaticUrls()
            } catch (exception) {
                //console.log('getEvents exception:' + exception)
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
    function getStaticUrls() {
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
            //if (url.startsWith(schemes[i])) {
            if (startsWith(url, schemes[i])) {
                return true
            }
        }
        return false
    }

    function startsWith(str, sub) {
        return str.lastIndexOf(sub, 0) === 0
    }

    // Serialize an array of form elements or a set of
    // key/values into a query string
    function param(obj) {
        var str = [];
        for (var p in obj)
            if (obj.hasOwnProperty(p)) {
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
            }
        return str.join("&");
    }

    try {
        getStaticUrls();
        getEvents();
        getForms();
    } catch (exception) {
        console.log(exception)
    }
    return urls;
}

casper.then(function () {
    console.log('requested ' + requested_count);
});
casper.run();


