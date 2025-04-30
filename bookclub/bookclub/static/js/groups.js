document.addEventListener("DOMContentLoaded", function () {
  fetch("/group")
    .then((response) => response.json())
    .then((groups) => {
      const groupDropdown = document.getElementById("groupDropdown");

      groups.forEach((group) => {
        const form = document.createElement("form");
        form.action = "/group/select";

        const groupLink = document.createElement("a");
        groupLink.href = "javascript:void(0)";
        groupLink.textContent = group.group_name;
        if (group.is_default) {
          groupLink.style.fontWeight = "bold";
        }
        groupLink.onclick = () => form.submit();

        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "group_name";
        hiddenInput.value = group.group_name;

        form.appendChild(groupLink);
        form.appendChild(hiddenInput);
        groupDropdown.appendChild(form);
      });
    })
    .catch((error) => console.error("Error fetching groups:", error));
});

function toggleDropdown() {
  const dropdownContent = document.getElementById("groupDropdown");
  if (dropdownContent.style.display === "block") {
    dropdownContent.style.display = "none";
  } else {
    dropdownContent.style.display = "block";
  }
}

// Close the dropdown if the user clicks outside of it
window.onclick = function (event) {
  if (!event.target.matches(".dropbtn")) {
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let i = 0; i < dropdowns.length; i++) {
      const openDropdown = dropdowns[i];
      if (openDropdown.style.display === "block") {
        openDropdown.style.display = "none";
      }
    }
  }
};
