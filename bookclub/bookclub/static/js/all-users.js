function createTable(data) {
  const container = document.createElement("div");
  container.className = "grid-container"; // Add a class for styling

  // Loop through the data and create a rounded item for each
  data.forEach((item, index) => {
    const itemDiv = document.createElement("div");
    itemDiv.className = "grid-item"; // Add a class for styling

    if (index < 3) {
      itemDiv.classList.add("border-item");
    }
    const itemContent = `
      <div class="profile">
        <img
          src="https://api.dicebear.com/9.x/micah/svg?hair=fonze,pixie,full&seed=${
            item.owner
          },${item.email}&facialHairProbability=0&mouth=smile,laughing,smirk"
          class="profile-pic-thumbnail"
          alt="Profile Picture"
        /><br>
        <strong>${item.owner}</strong>
      </div>
      ${item.number_of_books_read} Bücher
      <button class="toggle-button">Welche?</button>
      <div class="details" style="display: none;">
        ${item.books
          .map(
            (book) => `
            <p class="book-title">${book.original_number}. ${
              book.category_title
            }</p>
            <p class="book-name"><strong>${book.book_name}</strong></p>
            <p class="book-author">von ${book.author}</p>
            <div class="rating">${generateStarRating(book.rating)}</div>
            <div class="section-divider spacer"></div>
          `
          )
          .join("")}
      </div>
    `;
    itemDiv.innerHTML = itemContent;

    itemDiv.addEventListener("mouseenter", () => {
      itemDiv.classList.add("hover");
    });
    itemDiv.addEventListener("mouseleave", () => {
      itemDiv.classList.remove("hover");
    });

    // Add click event to toggle details visibility
    const toggleButton = itemDiv.querySelector(".toggle-button");
    const detailsDiv = itemDiv.querySelector(".details");

    toggleButton.addEventListener("click", () => {
      const isVisible = detailsDiv.style.display === "block";
      detailsDiv.style.display = isVisible ? "none" : "block";
      toggleButton.textContent = isVisible ? "Show Books" : "Hide";
    });

    container.appendChild(itemDiv);
  });

  document.getElementById("tableContainer").appendChild(container);
}

function fetchData(year = null) {
  const apiUrl = "/all_users" + (year ? `?year=${year}` : "");

  fetch(apiUrl, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      createTable(data);
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const scriptTag = document.querySelector(
    'script[src="/static/js/all-users.js"]'
  );
  const fetchDataFlag = scriptTag.getAttribute("data-fetch");
  const year = localStorage.getItem("year");

  if (fetchDataFlag === "true") {
    fetchData(year);
  } else {
    fetchData();
  }
});

function generateStarRating(rating) {
  let stars = "";
  for (let i = 1; i <= 5; i++) {
    if (i <= rating) {
      stars += '<i class="fas fa-star"></i>'; // Full star
    } else {
      stars += '<i class="far fa-star"></i>'; // Empty star
    }
  }
  return stars;
}
