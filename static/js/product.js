fetch('/api/products')
  .then(res => res.json())
  .then(data => {
    const table = document.getElementById('productTable');
    table.innerHTML = data.map(row => `
      <tr><td>${row.name}</td><td>${row.category}</td><td>${row.price}</td><td>${row.sold}</td></tr>
    `).join('');
  });
