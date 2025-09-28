<canvas id="riskChart"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  const ctx = document.getElementById('riskChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Low', 'Medium', 'High'],
      datasets: [{
        label: 'Risk Count',
        data: [12, 5, 3],
        backgroundColor: ['#4caf50', '#ff9800', '#f44336']
      }]
    }
  });
</script>