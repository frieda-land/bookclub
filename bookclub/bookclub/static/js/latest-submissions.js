document.addEventListener("DOMContentLoaded", function () {
  fetch("/latest_submissions")
    .then((response) => response.json())
    .then((data) => {
      displayLatestSubmissions(data);
    })
    .catch((error) =>
      console.error("Error fetching latest submissions:", error)
    );
});

function displayLatestSubmissions(submissions) {
  const container = document.getElementById("submissionsContainer");
  const submissionsContainer = document.createElement("div");
  submissionsContainer.className = "submissions-container";

  submissions.forEach((submission) => {
    const submissionDiv = document.createElement("div");
    submissionDiv.className = "submission";

    const title = document.createElement("h3");
    title.textContent = submission.book_name;
    submissionDiv.appendChild(title);

    const author = document.createElement("p");
    author.textContent = `Author: ${submission.author}`;
    submissionDiv.appendChild(author);

    const user = document.createElement("p");
    user.textContent = `Submitted by: ${submission.username}`;
    submissionDiv.appendChild(user);

    const date = document.createElement("p");
    date.textContent = `Date: ${new Date(
      submission.created_at
    ).toLocaleDateString()}`;
    submissionDiv.appendChild(date);

    const rating = document.createElement("div");
    rating.className = "rating";
    rating.innerHTML = generateStarRating(submission.rating);
    submissionDiv.appendChild(rating);

    submissionsContainer.appendChild(submissionDiv);
  });

  container.appendChild(submissionsContainer);
}

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

function toggleSubmissions() {
  const container = document.getElementById("submissionsContainer");
  if (container.style.display === "none") {
    container.style.display = "block";
  } else {
    container.style.display = "none";
  }
}
