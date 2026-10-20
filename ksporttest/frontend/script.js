const form = document.getElementById("scanForm");
const msg = document.getElementById("message");
const table = document.getElementById("results");
const button = document.getElementById("scanButton");
const exportBtn = document.getElementById("exportButton");

let scanned = [];

form.onsubmit = async (e) => {
    e.preventDefault();
    button.disabled = true;
    msg.textContent = "Scanning...";
    table.innerHTML = "";
    scanned = [];
    exportBtn.disabled = true;

    try {
        const res = await fetch("/api/scan", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                host: document.getElementById("host").value,
                start: document.getElementById("start").value,
                end: document.getElementById("end").value
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error);

        scanned = data.results;

        scanned.forEach(p => {
            const row = table.insertRow();
            row.insertCell().textContent = p.port;
            const status = row.insertCell();
            status.textContent = p.status;
            if (p.status === "Open") status.className = "open";
        });

        msg.textContent = "Scan complete!";
        exportBtn.disabled = scanned.length === 0;

    } catch (err) {
        msg.textContent = "Error: " + (err.message || "Request failed");
    } finally {
        button.disabled = false;
    }
};

exportBtn.onclick = () => {
    const csv = "Port,Status\n" +
        scanned.map(p => `${p.port},${p.status}`).join("\n");

    const link = document.createElement("a");
    link.href = URL.createObjectURL(
        new Blob([csv], {type: "text/csv"})
    );
    link.download = "scan-results.csv";
    link.click();
    URL.revokeObjectURL(link.href);
};