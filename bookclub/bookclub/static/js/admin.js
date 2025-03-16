function groupSelector(groups) {
  const categorySelect = document.getElementById("group");

  groups.forEach((group) => {
    const option = document.createElement("option");
    option.value = group.group_name;
    option.textContent = group.group_name;
    categorySelect.appendChild(option);
  });
}

function createGroupTable(groups) {
  const container = document.createElement("div");
  container.className = "grid-container"; // Add a class for styling

  groups.forEach((group) => {
    const groupDiv = document.createElement("div");
    groupDiv.className = "grid-item"; // Add a class for styling
    console.log(group);
    const groupContent = `
      <div class="group-name">
        <strong>${group.group_name}</strong>
      </div>
      <button class="toggle-button">Mitglieder</button>
      <div class="details" style="display: none;">
        <h3 class="label-title">Mitglieder</h3></br>
        <ul style="list-style-type: none; padding-left: 0;">
          ${group.members
            .map(
              (member) => `
              <li class="group-members">
                ${member.username} <italic>${member.email}</italic></br>
                <i class="fas fa-trash-alt delete-icon" data-username="${member.username}" data-group="${group.group_name}" style="cursor: pointer;"></i>
              </li>
            `
            )
            .join("")}
        </ul>
          <hr class="section-divider-small-margin">
          <h3 class="label-title">Eingeladen</h3></br>
          <ul style="list-style-type: none; padding-left: 0;">
            ${group.pending_invites
              .map(
                (email) => `
                <li class="group-members">
                  ${email}</br>
                  <i class="fas fa-trash-alt delete-icon-allowed-email" data-email="${email}" data-group="${group.group_name}" style="cursor: pointer;"></i>
                </li>
              `
              )
              .join("")}
        </ul>
      </div>
    `;
    groupDiv.innerHTML = groupContent;

    // Add click event to toggle details visibility
    const toggleButton = groupDiv.querySelector(".toggle-button");
    const detailsDiv = groupDiv.querySelector(".details");

    toggleButton.addEventListener("click", () => {
      const isVisible = detailsDiv.style.display === "block";
      detailsDiv.style.display = isVisible ? "none" : "block";
      toggleButton.textContent = isVisible ? "Show Members" : "Hide Members";
    });

    container.appendChild(groupDiv);
  });

  // Clear the container before appending new content
  const groupContainer = document.getElementById("groupContainer");
  groupContainer.innerHTML = "";
  groupContainer.appendChild(container);

  document.querySelectorAll(".delete-icon").forEach((icon) => {
    icon.addEventListener("click", (event) => {
      const username = event.target.getAttribute("data-username");
      const group = event.target.getAttribute("data-group");
      fetch(`/group/${group}/user/${username}`, {
        method: "DELETE",
      }).then((response) => {
        if (response.ok) {
          // Optionally, remove the user or invite from the UI
          const parentElement = event.target.parentElement;
          const nextSibling = parentElement.nextSibling;
          if (nextSibling && nextSibling.nodeName === "BR") {
            nextSibling.remove();
          }
          parentElement.remove();
        } else {
          console.error("Error deleting user");
        }
      });
    });
  });
  document.querySelectorAll(".delete-icon-allowed-email").forEach((icon) => {
    icon.addEventListener("click", (event) => {
      const email = event.target.getAttribute("data-email");
      const group = event.target.getAttribute("data-group");
      fetch(`/group/${group}/invite/${email}`, {
        method: "DELETE",
      }).then((response) => {
        if (response.ok) {
          // Optionally, remove the user or invite from the UI
          const parentElement = event.target.parentElement;
          const nextSibling = parentElement.nextSibling;
          if (nextSibling && nextSibling.nodeName === "BR") {
            nextSibling.remove();
          }
          parentElement.remove();
        } else {
          console.error("Error allowed email");
        }
      });
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  fetch("/group/my")
    .then((response) => response.json())
    .then((groups) => {
      createGroupTable(groups);
      groupSelector(groups);
    })
    .catch((error) => console.error("Error fetching groups:", error));
});
