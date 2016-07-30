/**
 * Created by John on 2016/7/29.
 */
switch (obj.type) {
    case 'text':
        // todo username, email, address, checkcode etc.
        if (obj.name.indexOf('user') >= 0) {
            requestdata[obj.name] = 'mazafaka'
        } else if (obj.name.indexOf('mail') >= 0) {
            requestdata[obj.name] = 'fakamaza@yopmail.com'
        } else {
            length = obj.maxLength > 0 ? obj.maxLength : 10;
            requestdata[obj.name] = Math.random().toString(36).slice(2).substring(0, length)
        }
        break;
    case 'password':
        requestdata[obj.name] = 'Passw0rd!@#';
        break;
    case 'email':
        requestdata[obj.name] = 'fakamaza@yopmail.com';
        break;
    // todo html5 input type
    default:
        if (obj.value) {
            requestdata[obj.name] = obj.value;
        } else {
            length = obj.maxLength > 0 ? obj.maxLength : 10;
            requestdata[obj.name] = Math.random().toString(36).slice(2).substring(0, length)
        }
}