// static/script.js
function updateTable(data) {
    const tbody = document.querySelector("#poolTable tbody");
    tbody.innerHTML = "";
    data.forEach(pool => {
        const row = `<tr>
            <td>${pool.token}</td>
            <td>${pool.dex}</td>
            <td>${pool.pool_address}</td>
            <td>${pool.price}</td>
            <td>${pool.volume}</td>
        </tr>`;
        tbody.innerHTML += row;
    });
}

setInterval(() => {
    fetch('/api/pools')
        .then(res => res.json())
        .then(updateTable);
}, 5000);

document.getElementById("tokenForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const mint = document.getElementById("mint").value;
    const name = document.getElementById("name").value;
    const symbol = document.getElementById("symbol").value;
    fetch("/add-token", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({mint, name, symbol})
    }).then(() => {
        document.getElementById("mint").value = "";
        document.getElementById("name").value = "";
        document.getElementById("symbol").value = "";
    });
});
