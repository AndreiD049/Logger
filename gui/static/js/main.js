"use strict";

var Logger = {
  labels: [],

  unread_messages: {},

  addNewLabel: function(label) {
    let myTab = document.getElementById("myTab");
    let labels_count = this.labels.length
    // add the tab
    let navItem = document.createElement("li");
    navItem.classList.add("nav-item");
    let a = document.createElement("a");
    a.className = "nav-link"
    a.id = label + "-tab";
    a.href = "#" + label;
    a.setAttribute("data-toggle", "tab");
    a.setAttribute("role", "tab");  
    a.setAttribute("aria-controls", label);
    if (labels_count === 0) {
      a.className += " active";
      a.setAttribute("aria-selected", "true");
    }

    a.addEventListener("click", this.readMessages, true);

    let b = document.createElement("b");
    b.textContent = label;
    a.appendChild(b);
    navItem.appendChild(a);
    myTab.appendChild(navItem);

    // add the textbox
    let tab_content = document.getElementById("myTabContent");

    let tabPane = document.createElement("div");
    tabPane.className = "tab-pane fade";
    if (labels_count === 0) {
      tabPane.className += " show active";
    }
    tabPane.id = label;
    tabPane.setAttribute("role", "tabpanel");
    tabPane.setAttribute("aria-labelledby", label + "-tab");

    let inner_cont = document.createElement("div");
    inner_cont.className = "container-fluid main";

    let text_cont = document.createElement("div");
    text_cont.className = "container mt-5 mb-5";

    let text_area = document.createElement("textarea");
    text_area.name = label;
    text_area.id = label + "-result";
    text_area.setAttribute("cols", "30");
    text_area.setAttribute("rows", "10");
    text_area.setAttribute("style", "min-width: 100%;");

    text_cont.appendChild(text_area);
    inner_cont.appendChild(text_cont);
    tabPane.appendChild(inner_cont);
    tab_content.appendChild(tabPane);

    this.labels.push(label);
    this.unread_messages[label] = 0;
  },

  addUnreadMessages: function(label, num) {
    let tab = document.getElementById(label + "-tab");
    let b = tab.getElementsByTagName("B")[0];

    if (tab.className.indexOf("active") === -1) {
      this.unread_messages[label] += num;
      
      var badge = tab.getElementsByTagName("SPAN")[0];
      
      if (badge === undefined) {
        var badge = document.createElement("SPAN");
        badge.className = "badge badge-pill badge-danger";
        tab.appendChild(badge);
      }
      b.textContent = label + " ";
      badge.textContent = this.unread_messages[label];
    }
  },

  readMessages: function(event) {
    let b = this.getElementsByTagName("B")[0];
    let span = this.getElementsByTagName("SPAN")[0];
    if (event.target !== this) {
      this.click();
    }
    let label = this.getAttribute("aria-controls");
    b.textContent = label;
    this.removeChild(span);
    log.unread_messages[label] = 0;
  }
};


function test(event)
{
  var xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == XMLHttpRequest.DONE) {   // XMLHttpRequest.DONE == 4
       if (xhttp.status == 200) {
           if (xhttp.responseText.length !== 0)
           {
                var response = JSON.parse(xhttp.responseText);
                var labels = Object.keys(response);
                for (let l = 0; l < labels.length;l++)
                {
                  let label = labels[l];
                  if (log.labels.indexOf(label) === -1) {
                    log.addNewLabel(label);
                  }
                  var txt = document.getElementById(label + "-result")
                  log.addUnreadMessages(label, response[label].length)
                  for (let m = 0; m < response[label].length; m++) {
                    let message = response[label][m];
                    txt.innerHTML += message["message"] + '\n';
                    txt.scrollTop = txt.scrollHeight;
                  }
                }
           }
       }
    }
};
  xhttp.open("POST", "/getinfo", true);
  xhttp.send();
}

var log = Object.create(Logger);

setInterval(test, 100)