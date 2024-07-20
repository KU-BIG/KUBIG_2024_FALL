var Links = {
  SetColor(color) {
    var alist = document.querySelectorAll("a");
    var i = 0;
    while (i < alist.length) {
      alist[i].style.color = color;
      i = i + 1;
    }
  },
};
var Body = {
  SetColor: function (color) {
    document.querySelector("body").style.color = color;
  },
  SetBackgroundColor: function (color) {
    document.querySelector("body").style.backgroundColor = color;
  },
};
var Line = {
  SetColor: function (color) {
    document.querySelector("#intro").style.borderBottom = `2px solid ${color}`;
    document.querySelector(".index").style.borderRight = `2px solid ${color}`;
  }
};
function nightDayHandler(self) {
  var target = document.querySelector("body");
  if (self.value === "night") {
    Body.SetBackgroundColor("dimgray");
    Body.SetColor("ivory");
    self.value = "day";

    Links.SetColor("lightyellow");
    Line.SetColor("ivory")
  } else {
    Body.SetBackgroundColor("lavenderblush");
    Body.SetColor("salmons");
    self.value = "night";

    Links.SetColor("lightcoral");
    Line.SetColor("pink")
  }
}
