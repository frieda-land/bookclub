const ctx = document.getElementById("myChart").getContext("2d");
console.log(chartData);
const data = {
  labels: chartData.months,
  datasets: [
    {
      label: "",
      barThickness: 40,
      minBarLength: 2,
      data: chartData.data,
      backgroundColor: ["#1f456e"],
    },
  ],
};
const config = {
  type: "bar",
  data: data,
  options: {
    plugins: {
      legend: {
        display: false,
      },
    },
    maintainAspectRatio: false, // Allow the chart to expand to the specified height
    scales: {
      x: {
        ticks: {
          font: {
            family: "Libre Baskerville", // Set font family for x-axis labels
          },
        },
      },
      y: {
        ticks: {
          font: {
            family: "Libre Baskerville", // Set font family for y-axis labels
          },
        },
      },
    },
    font: {
      family: "Libre Baskerville", // Set font family for all text in the chart
    },
  },
};
const myChart = new Chart(ctx, config);
