window.onload = function() {
    var hcaptcha = document.forms["contactform"]["h-captcha-response"];
    hcaptcha.required = true;
    hcaptcha.oninvalid = function(e) {
        alert("Please complete the captcha.");
    }
}
