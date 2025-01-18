function createUsersCustomCategoriesTable(data) {
  const container = document.createElement("div");
  container.className = "grid-container"; // Add a class for styling

  const myBooksContainer = document.getElementById("myCustomCategories");
  myBooksContainer.innerHTML = "";

  data.forEach((item, index) => {
    const itemDiv = document.createElement("div");

    const itemContent = `
      <div class="item-content">
        <p><span class="label label-title">${item}</span></p>
      </div>
    `;
    itemDiv.innerHTML = itemContent;
    container.appendChild(itemDiv);

    const deleteIcon = document.createElement("span");
    deleteIcon.className = "delete-icon";
    deleteIcon.innerHTML = "🗑️"; // Use trash can emoji or icon
    deleteIcon.title = "Delete this category";

    deleteIcon.addEventListener("click", () => {
      const url = `/profile/custom_category/${userId}/category/${item}`;
      fetch(url, {
        method: "DELETE",
      })
        .then((response) => {
          if (response.ok) {
            alert(`Custom category "${item}" deleted successfully!`);
            itemDiv.remove(); // Remove the item from the DOM
          } else if (response.status === 403) {
            alert("Cannot delete category as it has submissions");
          } else {
            alert("Failed to delete category");
          }
        })
        .catch((error) => {
          console.error("Error deleting category:", error);
        });
    });

    itemDiv.appendChild(deleteIcon);
    container.appendChild(itemDiv);
  });
  document.getElementById("myCustomCategories").appendChild(container);
}

function fetchChallengeData() {
  // Replace the URL with your backend API endpoint
  const apiUrl = `/profile/custom_category/${localStorage.getItem("userId")}`;

  fetch(apiUrl, {
    method: "GET",
  })
    .then((response) => response.json()) // Parse the JSON data from the response
    .then((data) => {
      createUsersCustomCategoriesTable(data);
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

fetchChallengeData();

document.addEventListener("DOMContentLoaded", function () {
  const newsletterEmail = localStorage.getItem("newsletterEmail");
  console.log(newsletterEmail);
  if (newsletterEmail && newsletterEmail !== "None") {
    document.getElementById("newsletterForm").style.display = "none";
    document.getElementById("unsubscribeButton").style.display = "block";
  } else {
    document.getElementById("newsletterForm").style.display = "block";
    document.getElementById("unsubscribeButton").style.display = "none";
  }
});

document
  .getElementById("newsletterForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
      credentials: "include",
    })
      .then((response) => {
        if (response.ok) {
          location.reload();
        } else {
          throw new Error("Network response was not ok");
        }
      })
      .catch((error) => {
        console.error(
          "There was a problem with the subscription operation:",
          error
        );
      });
  });

function unsubscribe() {
  fetch("/profile/unsubscribe", {
    method: "POST",
    credentials: "include",
  })
    .then((response) => {
      if (response.ok) {
        location.reload();
      } else {
        throw new Error("Network response was not ok");
      }
    })
    .catch((error) => {
      console.error(
        "There was a problem with the unsubscription operation:",
        error
      );
    });
}
