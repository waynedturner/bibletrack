function next(path) {
    var d = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
    var loc = (d.getMonth()+1) + "-" + d.getDate() + ".html";
    window.location.href = path + "/" + loc;
}

function prev(path) {
    var d = new Date(new Date().getTime() - 24 * 60 * 60 * 1000);
    var loc = (d.getMonth()+1) + "-" + d.getDate() + ".html";
    window.location.href = path + "/" + loc;
}

function today(path) {
    var d = new Date();
    var loc = (d.getMonth()+1) + "-" + d.getDate() + ".html";
    window.location.href = path + "/" + loc;
}
