function next() {
    var d = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
    var loc = d.getMonth() + "-" + d.getDate() + ".html";
    window.location.href = loc;
}

function prev() {
    var d = new Date(new Date().getTime() - 24 * 60 * 60 * 1000);
    var loc = d.getMonth() + "-" + d.getDate() + ".html";
    window.location.href = loc;
}

function today() {
    var d = new Date();
    var loc = d.getMonth() + "-" + d.getDate() + ".html";
    window.location.href = loc;
}

function setupNav(){
    var logo = document.getElementById('logo');
    logo.onclick = toggleNav;
}

function toggleNav(){
    let navPane = document.getElementById('navPane');
    if (navPane.style.left === '0px') {
        navPane.style.left = '-200px';
    } else {
        navPane.style.left = '0px';
    }
}
