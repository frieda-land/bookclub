function createUsersCustomCategoriesTable(data) {
  const container = document.createElement("div");
  container.className = "grid-container"; // Add a class for styling

  const myBooksContainer = document.getElementById("myBooksContainer");
  myBooksContainer.innerHTML = "";

  data.forEach((item, index) => {
    const itemDiv = document.createElement("div");

    const itemContent = ` 
    <div class="item-content">
      <p><span class="label">Kategorie:</span> ${item.category_id}</p>
      <p><span class="label label-title">${item.title}</span></p>
      <p><span class="label"></span> <strong>${item.book_name}</strong> von <span class="label"></span> <strong>${item.author}</strong></p>
        <button class="shareButton" id="shareBtn" category="${item.category_id}: ${item.title}" book-name="${item.book_name}" author="${item.author}" data-image-url="https://storage.googleapis.com/shelfie-public-pictures/bookcovers/${item.book_name}-${item.author}.jpg">share</button>  
      </div>
  `;
    itemDiv.innerHTML = itemContent;
    container.appendChild(itemDiv);

    const deleteIcon = document.createElement("span");
    deleteIcon.className = "delete-icon";
    deleteIcon.innerHTML = "🗑️"; // Use trash can emoji or icon
    deleteIcon.title = "Delete this book";

    deleteIcon.addEventListener("click", () => {
      const url = `/my_challenge/books/${userId}/category/${item.category_id}`;
      fetch(url, {
        method: "DELETE",
      })
        .then((response) => {
          if (response.ok) {
            alert(`Book "${item.book_name}" deleted successfully!`);
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
  document.getElementById("myBooksContainer").appendChild(container);
}

function fetchChallengeData() {
  // Replace the URL with your backend API endpoint
  const apiUrl = `/my_challenge/books/${localStorage.getItem("userId")}`;

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

document.addEventListener("DOMContentLoaded", function () {
  fetch(
    `/my_challenge/all_unused_categories/${localStorage.getItem("userId")}`,
    {
      method: "GET",
      credentials: "include",
    }
  )
    .then((response) => response.json())
    .then((data) => {
      const categorySelect = document.getElementById("category");
      data.forEach((category) => {
        const option = document.createElement("option");
        option.value = category.original_number;
        option.textContent = category.title;
        categorySelect.appendChild(option);
      });
    })
    .catch((error) => {
      console.error("Error fetching categories:", error);
    });
});

document
  .getElementById("bookForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const userId = localStorage.getItem("userId");

    let actionUrl = form.action;
    // Needed see https://stackoverflow.com/questions/63511413/fastapi-redirection-for-trailing-slash-returns-non-ssl-link
    fetch(`${actionUrl}/`, {
      method: "POST",
      body: formData,
      credentials: "include", // Include credentials (cookies) in the request
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.text();
      })
      .then((data) => {
        window.location.href = `/my_challenge`;
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  });

fetchChallengeData();

document.addEventListener("click", async (event) => {
  if (event.target && event.target.id === "shareBtn") {
    if (navigator.share) {
      const bookName = event.target.getAttribute("book-name");
      const author = event.target.getAttribute("author");
      const category = event.target.getAttribute("category");
      const response = await fetch(
        event.target.getAttribute("data-image-url"),
        { mode: "cors" }
      );
      const blob = await response.blob();
      const file = new File([blob], "bookcover.jpg", { type: blob.type });
      await navigator
        .share({
          title: "Shelfie Update",
          text: `✨ Kategorie ${category} ✨ "${bookName}" von ${author} 📚🙌`,
          files: [file],
        })
        .then(() => {
          console.log("Thanks for sharing!");
        })
        .catch((err) => console.error(err));
    } else {
      alert(
        "The current browser does not support the share function. Please, manually share the link"
      );
    }
  }
});
