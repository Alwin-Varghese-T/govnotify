
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


//dropdown list new text field
/*
function yesnoCheck(that) {
    if (that.value == "Student") {
        document.getElementById("ifStudent").style.display = "block";
    } else {
        document.getElementById("ifStudent").style.display = "none";
    }
}
*/

//otp verification box

function verify(that) {
   
        document.getElementById("ifVerify").style.display = "block";
}

//dropdown list new text field for category
function categoryCheck(that) {
  // Get all elements with class "category-block"
  var categoryBlocks = document.getElementsByClassName("category-block");
  
  // Hide all category blocks
  for (var i = 0; i < categoryBlocks.length; i++) {
    categoryBlocks[i].style.display = "none";
  }
  
  // Show the selected category block
  if (that.value == "agriculture") {
    document.getElementById("ifagriculture").style.display = "block";
  } else if (that.value == "education") {
    document.getElementById("ifeducation").style.display = "block";
  }
  else if (that.value == "health") {
    document.getElementById("ifhealth").style.display = "block";
  }
  else if (that.value == "social welfare") {
    document.getElementById("ifsocialwelfare").style.display = "block";
  }
}






  /**
   * Search bar toggle
   */
$('input.single-checkbox').on('change', function(evt) {
   if($(this).siblings(':checked').length >= 5) {
       this.checked = false;
   }
});



