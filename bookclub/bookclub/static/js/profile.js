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
    deleteIcon.title =
      "Du kannst nur die Wunschkategorien löschen, die noch niemand benutzt hat.";

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

function fetchCustomCategories() {
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

fetchCustomCategories();

document.addEventListener("DOMContentLoaded", function () {
  const newsletterEmail = localStorage.getItem("newsletterEmail");
  if (newsletterEmail && newsletterEmail !== "None") {
    document.getElementById("newsletterForm").style.display = "none";
    document.getElementById("unsubscribeButton").style.display = "block";
  } else {
    document.getElementById("newsletterForm").style.display = "block";
    document.getElementById("unsubscribeButton").style.display = "none";
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("trophies-container");
  const encodedTrophies = localStorage.getItem("trophies");
  if (encodedTrophies) {
    const decodedTrophies = decodeURIComponent(encodedTrophies);
    const trophies = JSON.parse(decodedTrophies);
    if (
      (trophies.monthly && trophies.monthly.length > 0) ||
      (trophies.yearly && trophies.yearly.length > 0)
    ) {
      let row;
      trophies.monthly.forEach((trophy, index) => {
        if (index % 3 === 0) {
          row = document.createElement("div");
          row.className = "trophy-row";
          container.appendChild(row);
        }
        const trophyDiv = document.createElement("div");
        trophyDiv.className = "trophy";
        trophyDiv.innerHTML = `
          <img src="/static/images/month.png" alt="trophy" />
          <p><strong>Leser:in des Monats<br> ${trophy.month}</strong> </p>
          <p>(${trophy.number_of_books_read} Bücher)</p>
        `;
        row.appendChild(trophyDiv);
      });
      trophies.year.forEach((trophy, index) => {
        if (index % 3 === 0) {
          row = document.createElement("div");
          row.className = "trophy-row";
          container.appendChild(row);
        }
        const trophyDiv = document.createElement("div");
        trophyDiv.className = "trophy";
        trophyDiv.innerHTML = `
          <img src="/static/images/year.png" alt="trophy" />
          <p><strong>Popsugar Gewinnerin des Jahres ${trophy.year}</strong> </p>
          <p>(${trophy.number_of_books_read} Bücher)</p>
        `;
        row.appendChild(trophyDiv);
      });
    }
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
