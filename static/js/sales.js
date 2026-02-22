fetch('/api/dashboard/sales-details')
  .then(res => res.json())
  .then(data => {
    const table = document.getElementById('salesTable');
    table.innerHTML = data.map(row => `
      <tr><td>${row.customer_name}</td><td>${row.product_name}</td><td>${row.quantity}</td><td>${row.total_price}</td><td>${row.date}</td></tr>
    `).join('');
  });