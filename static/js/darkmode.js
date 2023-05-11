const moonPath = "M18 27.5C18 42.6878 27.5 55 27.5 55C12.3122 55 0 42.6878 0 27.5C0 12.3122 12.3122 0 27.5 0C27.5 0 18 12.3122 18 27.5Z";
const circlePath = "M55 27.5C55 42.6878 42.6878 55 27.5 55C12.3122 55 0 42.6878 0 27.5C0 12.3122 12.3122 0 27.5 0C42.6878 0 55 12.3122 55 27.5Z";

const darkMode = document.querySelector("#darkMode");
let toggleStatus = JSON.parse(localStorage.getItem("darkMode")) || false;

setMode(toggleStatus);

darkMode.addEventListener("click", () => {
  const timeline = anime.timeline({
    duration: 750,
    easing: "easeOutExpo"
  });

  toggleStatus = !toggleStatus;
  setMode(toggleStatus);
  localStorage.setItem("darkMode", toggleStatus);
});

window.addEventListener("DOMContentLoaded", () => {
  setMode(toggleStatus);
});

function setMode(status) {
  const timeline = anime.timeline({
    duration: 750,
    easing: "easeOutExpo"
  });

  morphTo(timeline, status);
}

function morphTo(timeline, toggler) {
  timeline
    .add({
      targets: ".circle",
      d: [{ value: toggler ? circlePath : moonPath }]
    })
    .add(
      {
        targets: "#darkMode",
        rotate: toggler ? 40 : 320
      },
      "-=700"
    )
    .add(
      {
        targets: ".card",
        backgroundColor: toggler ? "#ffffff" : "#A9A9A9"
      },
      "-=700"
    )
    .add(
      {
        targets: "header",
        backgroundColor: toggler ? "#ffffff" : "#333"
      },
      "-=1200"
    )
    .add(
      {
        targets: "aside",
        backgroundColor: toggler ? "#ffffff" : "#333"
      },
      "-=1200"
    )
    .add(
      {
        targets: "body",
        backgroundColor: toggler ? "#f6f9ff" : "#333"
      },
      "-=700"
    );
}
