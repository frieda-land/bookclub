document
  .getElementById("signupForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        if (response.status === 201) {
          form.style.display = "none";
          const errorMessage = document.querySelector(".error-message");
          if (errorMessage) {
            errorMessage.style.display = "none";
          }
        }
        return response.json();
      })
      .then((data) => {
        // Display the message returned by the backend
        const messageContainer = document.getElementById("messageContainer");
        messageContainer.textContent = data.message;
        messageContainer.style.display = "block";
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
        const messageContainer = document.getElementById("messageContainer");
        messageContainer.textContent = `There was a problem with the fetch operation: ${error}`;
        messageContainer.style.display = "block";
        messageContainer.classList.add("error-message-container");
      });
  });
