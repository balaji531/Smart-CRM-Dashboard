fetch('/api/dashboard/stats')
  .then(res => res.json())
  .then(data => {
    document.getElementById('totalCustomers').innerText = `Total Customers: ${data.total_customers}`;
    document.getElementById('totalProducts').innerText = `Total Products: ${data.total_products}`;
    document.getElementById('revenue').innerText = `YTD Revenue: ₹${data.ytd_revenue}`;
    document.getElementById('topProduct').innerText = `Top Product: ${data.top_product} (${data.top_product_sold} sold)`;
  });

fetch('/api/dashboard/sales-chart')
  .then(res => res.json())
  .then(data => {
    new Chart(document.getElementById('salesChart'), {
      type: 'line',
      data: { labels: data.months, datasets: [{ label: 'Sales', data: data.totals }] }
    });
  });

fetch('/api/dashboard/product-chart')
  .then(res => res.json())
  .then(data => {
    new Chart(document.getElementById('productChart'), {
      type: 'doughnut',
      data: { labels: data.categories, datasets: [{ data: data.counts }] }
    });
  });