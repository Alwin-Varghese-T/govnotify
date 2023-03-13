
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach(e => e.addEventListener(type, listener))
    } else {
      select(el, all).addEventListener(type, listener)
    }
  }

 
  /**
   * Sidebar toggle
   */
  if (select('.toggle-sidebar-btn')) {
    on('click', '.toggle-sidebar-btn', function(e) {
      select('body').classList.toggle('toggle-sidebar')
    })
  }

  /**
   * Search bar toggle
   */
  if (select('.search-bar-toggle')) {
    on('click', '.search-bar-toggle', function(e) {
      select('.search-bar').classList.toggle('search-bar-show')
    })
  }



})();

//password_validation

var password = document.getElementById("password")
  , reTypePassword = document.getElementById("reTypePassword");

function validatePassword(){
  if(password.value != reTypePassword.value) {
    reTypePassword.setCustomValidity("Passwords Don't Match");
  } else {
    reTypePassword.setCustomValidity('');
  }
}

password.onchange = validatePassword;
reTypePassword.onkeyup = validatePassword;

//age

$(function(){
    var $select = $(".1-100");
    for (i=1;i<=100;i++){
        $select.append($('<option></option>').val(i).html(i))
    }
});

//age another demoregistration.html
window.onload = function () {
  var ddl = document.getElementById('mycontainer').getElementsByTagName("select")[0];
  for (var i = 1; i <= 115; i++) {
      var theOption = new Option;
      theOption.text = i;
      theOption.value = i;
      ddl.options[i] = theOption;
  }
}
