function createUsersBooksTable(data) {
  const container = document.createElement("div");
  container.className = "grid-container"; // Add a class for styling
  console.log(data);
  const myBookmarksContainer = document.getElementById("myBookmarks");
  myBookmarksContainer.innerHTML = "";

  data.forEach((item, index) => {
    const itemDiv = document.createElement("div");

    const itemContent = `
    <div class="item-content">
      <p><span class="label">Kategorie:</span> "${item.category_name}"</p></br>
      <p><span class="label label-title">${item.author_title}</span></p>
    </div>
  `;
    itemDiv.innerHTML = itemContent;
    container.appendChild(itemDiv);

    const deleteIcon = document.createElement("span");
    deleteIcon.className = "delete-icon";
    deleteIcon.innerHTML = "🗑️";
    deleteIcon.title = "Delete this bookmark";

    deleteIcon.addEventListener("click", () => {
      const url = `/bookmarks/${item.bookmark_id}`;
      fetch(url, {
        method: "DELETE",
      })
        .then((response) => {
          if (response.ok) {
            alert("Bookmark deleted successfully!");
            itemDiv.remove(); // Remove the item from the DOM
          } else {
            alert("Failed to delete the book. Please try again.");
          }
        })
        .catch((error) => {
          console.error("Error deleting book:", error);
        });
    });

    itemDiv.appendChild(deleteIcon);
    container.appendChild(itemDiv);
  });
  document.getElementById("myBookmarks").appendChild(container);
}

function fetchChallengeData() {
  // Replace the URL with your backend API endpoint
  const apiUrl = `/bookmarks/${localStorage.getItem("userId")}`;

  fetch(apiUrl, {
    method: "GET",
  })
    .then((response) => response.json()) // Parse the JSON data from the response
    .then((data) => {
      createUsersBooksTable(data);
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

fetchChallengeData();
