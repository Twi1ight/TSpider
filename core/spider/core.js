/**
 * Created by John on 2016/7/30.
 */
var require = patchRequire(require);
var utils = require('utils');
var fs = require('fs');

exports.evilResource = function (url) {
    "use strict";
    var parser = document.createElement('a');
    parser.href = url;
    var filename = parser.pathname.replace(/^.*[\\\/]/, '');
    var extension = utils.fileExt(filename);
    var hostname = parser.hostname;
    //todo stastic urls / ad urls
    if (hostname.match('hm\.baidu\.com|googleads\.g\.doubleclick\.net')) {
        return true
    }
    var exclude = ['a3c', 'ace', 'aif', 'aifc', 'aiff', 'arj', 'asf', 'asx', 'attach', 'au',
        'avi', 'bin', 'cab', 'cache', 'class', 'djv', 'djvu', 'dwg', 'es', 'esl',
        'exe', 'fif', 'fvi', 'gz', 'hqx', 'ice', 'ief', 'ifs', 'iso', 'jar', 'kar',
        'mid', 'midi', 'mov', 'movie', 'mp', 'mp2', 'mp3', 'mp4', 'mpeg',
        'mpeg2', 'mpg', 'mpg2', 'mpga', 'msi', 'pac', 'pdf', 'ppt', 'pptx', 'psd',
        'qt', 'ra', 'ram', 'rm', 'rpm', 'snd', 'svf', 'tar', 'tgz', 'tif',
        'tiff', 'tpl', 'uff', 'wav', 'wma', 'wmv', 'doc', 'docx', 'db', 'jpg'];
    return extension && exclude.indexOf(extension) >= 0
};

exports.saveFile = function (static_urls, requested_urls, filename) {
    "use strict";
    if (!filename) {
        console.log('saveFile failed! no filename found!');
        //for (var j = 0; j < requested_urls.length; j++) {
        //    console.log(requested_urls[j])
        //}
        //for (j = 0; j < static_urls.length; j++) {
        //    console.log(static_urls[j])
        //}
        return
    }
    var f = fs.open(filename, 'w');
    for (var i = 0; i < requested_urls.length; i++) {
        f.write(requested_urls[i] + '\n');
    }
    for (i = 0; i < static_urls.length; i++) {
        f.write(static_urls[i] + '\n');
    }
    f.close();
};

exports.FireintheHole = function () {
    "use strict";
    var urls = [];
    //var retvar = [];

    function fillInputs() {
        var inputs = document.getElementsByTagName('input');
        console.log('get all inputs length: ' + inputs.length);
        //var requestdata = {};
        var buttons = [];
        for (var j = 0; j < inputs.length; j++) {
            var obj = inputs[j];
            console.log(obj.name + ' ' + obj.type + ' ' + obj.id + ' ' + obj.value);
            if (!obj.hasAttribute('type')) {
                continue
            }
            switch (obj.type) {
                //case 'hidden':
                case 'submit':
                    continue;
                // Click all the radio buttons and checkboxes
                case 'radio':
                case 'checkbox':
                    obj.click();
                    continue;
                case 'button':
                    buttons.push(obj);
                    continue;
            }
            // exist default value
            if (obj.name && obj.value) {
                continue
            }
            // fill each input
            var length, value;
            switch (obj.type) {
                case 'text':
                    // username, email, address, checkcode etc.
                    if (obj.name.indexOf('user') >= 0) {
                        value = 'mazafaka';
                    } else if (obj.name.indexOf('mail') >= 0) {
                        value = 'fakamaza@yopmail.com';
                    } else if (obj.name.indexOf('phone') >= 0 || obj.name.indexOf('mobile') >= 0) {
                        value = '13800138000';
                    } else {
                        length = obj.maxLength > 0 && obj.maxLength != 524288 ? obj.maxLength : 10;
                        value = rndStr(length);
                    }
                    break;
                case 'password':
                    value = 'Passw0rd!@#';
                    break;
                case 'email':
                    value = 'fakamaza@yopmail.com';
                    break;
                // todo html5 input type
                default:
                    length = obj.maxLength > 0 && obj.maxLength != 524288 ? obj.maxLength : 10;
                    value = rndStr(length);
            }
            obj.value = value;
        }
        //click all buttons
        //for (var i = 0; i < buttons.length; i++) {
        //    buttons[i].click()
        //}
        return buttons
    }

    function getForms() {
        var buttons = fillInputs();
        var f = document.forms;
        for (var i = 0; i < f.length; i++) {
            console.log('form ' + i + ' total:' + f.length);
            var form = f[i];
            var inputs = form.getElementsByTagName('input');
            console.log('get form inputs length: ' + inputs.length);
            var formdata = {};
            for (var j = 0; j < inputs.length; j++) {
                var obj = inputs[j];
                console.log(obj.name + ' ' + obj.type + ' ' + obj.id + ' ' + obj.value);
                if (!obj.hasAttribute('type')) {
                    continue
                }
                if (obj.name && obj.value) {
                    formdata[obj.name] = obj.value;
                }
            }
            var querystring = param(formdata);
            if (querystring) {
                var action = form.action ? form.action : form.baseURI;
                var request = form.method.toUpperCase() + '|||' + rmFragment(action) + '|||' + querystring + '|||' + rmFragment(form.baseURI);
                if (urls.indexOf(request) < 0) {
                    urls.push(request);
                }

            }
            form.submit();
        }
        //click all buttons
        for (i = 0; i < buttons.length; i++) {
            buttons[i].click()
        }
    }

    function getEvents() {
        var events = [];
        var events_func_str = [];
        var allElements, len;
        allElements = document.getElementsByTagName('*');
        len = allElements.length;// allElements will change,len will change
        for (var i = 0; i < len; i++) {
            //js_code
            if (allElements[i].href) {
                var jscode = allElements[i].href.match("javascript:(.*)");
                if (jscode) {
                    if (events.indexOf(jscode[0]) < 0) {
                        events.push(jscode[0]);
                    }
                }
            }
            var attrs = allElements[i].attributes;
            var func_str;
            for (var j = 0; j < attrs.length; j++) {
                if (typeof allElements[i].onclick === 'function') {
                    func_str = String(allElements[i].onclick);
                    if (events_func_str.indexOf(func_str) < 0) {
                        events.push(allElements[i]);
                    }
                } else {
                    // todo ugly hack events here, trigger event like onclick
                    var name = attrs[j].name;
                    var value = allElements[i][name];
                    if (startsWith(name, 'on') && typeof(value) === 'function') {
                        console.log(name + '   ' + value + '    ' + events.indexOf(value));
                        func_str = String(value);
                        if (events_func_str.indexOf(func_str) < 0) {
                            events.push(value)
                        }
                    }
                }
            }
        }
        for (var k = 0; k < events.length; k++) {
            try {
                if (typeof events[k] === 'string') {
                    eval(events[k]);
                } else if (typeof events[k] === 'object') {
                    events[k].click();
                } else if (typeof events[k] === 'function') {
                    console.log(events[k]);
                    events[k]();
                } else {
                    continue
                }
                //setTimeout(function () {
                //    getStaticUrls()
                //}, 1000);
                sleep(500);
                getStaticUrls();
            } catch (exception) {
                console.log('getEvents exception:' + exception)
            }
        }
    }

    function handleTag(tag, src) {
        var elements = document.getElementsByTagName(tag);
        for (var i = 0; i < elements.length; i++) {
            var method, referer, url, request;
            method = 'GET';
            referer = window.location.href;
            url = elements[i][src];
            if (url && urls.indexOf(url) < 0 && validScheme(url) && url.length < 1024) {
                request = method + '|||' + rmFragment(url) + '|||null|||' + rmFragment(document.baseURI);
                if (urls.indexOf(request) < 0) {
                    urls.push(request);
                }
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

    function validScheme(url) {
        var schemes = ['http', 'https'];
        for (var i = 0; i < schemes.length; i++) {
            if (startsWith(url, schemes[i])) {
                return true
            }
        }
        return false
    }

    function startsWith(str, sub) {
        return str.lastIndexOf(sub, 0) === 0
    }

    function rmFragment(url) {
        return url ? url.split('#')[0] : ''
    }

    function rndStr(length) {
        var text = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

        //make sure starts with alpha
        text += possible.charAt(Math.floor(Math.random() * (possible.length - 10)));
        for (var i = 0; i < length - 1; i++)
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        return text;
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

    function sleep(milliseconds) {
        var start = new Date().getTime();
        for (var i = 0; i < 1e7; i++) {
            if ((new Date().getTime() - start) > milliseconds) {
                break;
            }
        }
    }

    try {
        getStaticUrls();
    } catch (exception) {
        console.log('getStaticUrls ' + exception)
    }
    try {
        getEvents();
    } catch (exception) {
        console.log('getEvents ' + exception)
    }
    try {
        getForms();
    } catch (exception) {
        console.log('getForms ' + exception)
    }
    return urls;
};