document.addEventListener("DOMContentLoaded", function () {
  const challengeContainer = document.getElementById("challenge-container");

  const challenges = [
    { year: 2025, current: true, image: "/static/images/popsugar2025.png" },
    { year: 2024, current: false, image: "/static/images/popsugar2024.png" },
    { year: 2023, current: false, image: "/static/images/popsugar2023.png" },
  ];

  challenges.forEach((challenge) => {
    const challengeWrapper = document.createElement("div");
    challengeWrapper.className = "challenge-wrapper";

    const challengeBox = document.createElement("div");
    challengeBox.className = "challenge-box";
    challengeBox.style.backgroundImage = `url(${challenge.image})`;
    challengeBox.style.backgroundSize = "cover";
    challengeBox.style.backgroundPosition = "center";

    const titleContainer = document.createElement("div");
    titleContainer.className = "title-container";

    const challengeTitle = document.createElement("h3");
    challengeTitle.textContent = `Challenge ${challenge.year}`;
    titleContainer.appendChild(challengeTitle);
    challengeBox.appendChild(titleContainer);

    challengeWrapper.appendChild(challengeBox);

    const buttonContainer = document.createElement("div");
    buttonContainer.className = "button-container";

    const button = document.createElement("button");
    if (challenge.current) {
      button.textContent = "View Leaderboard";
      button.onclick = () => {
        window.location.href = `/`;
      };
    } else {
      button.textContent = "Final Leaderboard";
      button.onclick = () => {
        window.location.href = `/previous_challenges/leaderboard/${challenge.year}`;
      };
    }
    buttonContainer.appendChild(button);
    challengeWrapper.appendChild(buttonContainer);

    challengeContainer.appendChild(challengeWrapper);
  });
});
