document
  .getElementById("airline-select")
  .addEventListener("change", function () {
    const selected = this.value;
    const logoDiv = document.getElementById("airline-logo");
    let logoUrl = "";

    switch (selected) {
      case "Vietnam Airlines":
        logoUrl = "/static/images/Vietnam_Airlines_logo.png";
        break;
      case "Bamboo Airways":
        logoUrl = "/static/images/Bamboo_Airways_Logo.png";
        break;
      case "VietJet Air":
        logoUrl = "/static/images/VietJet_Air_logo.png";
        break;
      case "Vietravel Airlines":
        logoUrl = "/static/images/Vietravel_Airlines_Logo.png";
        break;
      default:
        logoUrl = "";
    }

    logoDiv.style.backgroundImage = logoUrl ? `url('${logoUrl}')` : "";
  });

document.addEventListener("DOMContentLoaded", function () {
  const selects = document.querySelectorAll("select");

  function updatePlaceholderColor(select) {
    if (select.value === "") {
      select.classList.add("placeholder");
    } else {
      select.classList.remove("placeholder");
    }
  }

  selects.forEach((select) => updatePlaceholderColor(select));

  selects.forEach((select) => {
    select.addEventListener("change", () => updatePlaceholderColor(select));
  });
});
