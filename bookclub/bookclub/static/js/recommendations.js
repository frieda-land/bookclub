document
  .getElementById("recommendationsForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const userId = localStorage.getItem("userId");
    const outputBox = document.getElementById("outputBox");
    const submitButton = document.getElementById("submitButton");
    // const formContainer = document.getElementById('formContainer');
    outputBox.innerHTML = ""; // Clear previous output
    outputBox.style.display = "none"; // Make the box invisible when empty
    submitButton.disabled = true; // Disable the submit button
    submitButton.classList.add("loading"); // Add loading class to show blinking dots
    localStorage.setItem("category", formData.get("category"));

    fetch(form.action, {
      method: "POST",
      body: formData,
      credentials: "include", // Include credentials (cookies) in the request
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = ""; // Buffer to accumulate text chunks
        return new ReadableStream({
          start(controller) {
            function push() {
              reader.read().then(({ done, value }) => {
                if (done) {
                  if (buffer) {
                    renderBookCards(buffer);
                  }
                  controller.close();
                  submitButton.disabled = false; // Enable the submit button
                  submitButton.classList.remove("loading"); // Remove loading class
                  // formContainer.style.display = 'none'; // Hide the form
                  return;
                }
                buffer += decoder.decode(value, { stream: true });
                push();
              });
            }
            push();
          },
        });
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
        submitButton.disabled = false;
        submitButton.classList.remove("loading");
      });
  });

function renderBookCards(text) {
  const outputBox = document.getElementById("outputBox");
  const submitButton = document.getElementById("submitButton");
  const lines = text.split("\n").filter((line) => line.trim() !== ""); // Split and filter out empty lines
  if (lines.length > 0) {
    outputBox.style.display = "block"; // Make the box visible when it has content
    submitButton.disabled = false; // Enable the submit button
    submitButton.classList.remove("loading"); // Remove loading class
  }
  lines.forEach((line) => {
    const bookCard = createBookCard(line);
    outputBox.appendChild(bookCard);
  });
}

function createBookCard(text) {
  const card = document.createElement("div");
  card.className = "book-card";

  const [titleAuthor, summary] = text.split(" - ", 2);

  const header = document.createElement("div");
  header.className = "book-header";

  const titleAuthorElement = document.createElement("div");
  titleAuthorElement.className = "book-title-author";
  titleAuthorElement.textContent = titleAuthor;
  titleAuthorElement.title = summary; // Add summary as tooltip
  titleAuthorElement.addEventListener("click", () => {
    summaryElement.classList.toggle("visible");
    card.classList.toggle("expanded");
  });

  const saveIcon = document.createElement("i");
  saveIcon.className = "far fa-bookmark save-icon"; // Empty bookmark icon
  saveIcon.addEventListener("click", () => toggleFavourite(text, saveIcon));

  header.appendChild(titleAuthorElement);
  header.appendChild(saveIcon);

  const summaryElement = document.createElement("div");
  summaryElement.className = "book-summary";
  summaryElement.textContent = summary;

  card.appendChild(header);
  card.appendChild(summaryElement);

  return card;
}

function toggleFavourite(text, icon) {
  if (icon.classList.contains("saved")) {
    unsaveFavourite(text, icon);
  } else {
    saveFavourite(text, icon);
  }
}

function saveFavourite(text, icon) {
  const category = localStorage.getItem("category");
  const userId = localStorage.getItem("userId");
  fetch("/recommendations/save_favourite", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      content: text,
      category: category,
      user_id: userId,
    }),
    credentials: "include", // Include credentials (cookies) in the request
  })
    .then((response) => {
      if (response.ok) {
        icon.classList.remove("far"); // Remove empty bookmark class
        icon.classList.add("fas", "saved"); // Add filled bookmark and saved class
      } else {
        throw new Error("Network response was not ok");
      }
    })
    .catch((error) => {
      console.error("There was a problem with the save operation:", error);
    });
}

function unsaveFavourite(text, icon) {
  const category = localStorage.getItem("category");
  const userId = localStorage.getItem("userId");
  fetch("/recommendations/unsave_favourite", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      content: text,
      category: category,
      user_id: userId,
    }),
    credentials: "include", // Include credentials (cookies) in the request
  })
    .then((response) => {
      if (response.ok) {
        icon.classList.remove("fas", "saved"); // Remove filled bookmark and saved class
        icon.classList.add("far"); // Add empty bookmark class
      } else {
        throw new Error("Network response was not ok");
      }
    })
    .catch((error) => {
      console.error("There was a problem with the unsave operation:", error);
    });
}
