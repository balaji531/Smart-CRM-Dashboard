fetch('/api/sales/customer-products')
  .then(res => res.json())
  .then(data => {
    const table = document.getElementById('customerTable');
    table.innerHTML = data.map(row => `
      <tr><td>${row.customer_name}</td><td>${row.customer_email}</td><td>${row.product_name}</td><td>${row.date}</td></tr>
    `).join('');
  });