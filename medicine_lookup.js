// ===============================
// Medicine Lookup – Backend Powered
// ===============================

async function fetchMedicine(name) {
    const response = await fetch(
        `http://127.0.0.1:5000/api/medicine?name=${encodeURIComponent(name)}`
    );

    if (!response.ok) return null;
    return response.json();
}

function showMessage(msg) {
    const resultsBox = document.getElementById("medicineResults");
    resultsBox.style.display = "block";

    // Hide content but keep structure
    resultsBox.querySelector(".medicine-name").innerText = "";
    resultsBox.querySelector(".medicine-category").innerText = "";

    const infoBlocks = resultsBox.querySelectorAll(".info-block p");
    infoBlocks.forEach(p => p.innerText = "");

    // Show message in first block
    infoBlocks[0].innerText = msg;
}


function renderMedicine(data) {
    const resultsBox = document.getElementById("medicineResults");

    const nameEl = resultsBox.querySelector(".medicine-name");
    const categoryEl = resultsBox.querySelector(".medicine-category");
    const infoBlocks = resultsBox.querySelectorAll(".info-block p");

    if (!nameEl || infoBlocks.length < 5) {
        console.error("Medicine result structure missing in HTML");
        return;
    }

    nameEl.innerText = data.name;
    categoryEl.innerText = data.category;

    infoBlocks[0].innerText = data.composition;
    infoBlocks[1].innerHTML = data.uses.join("<br>");
    infoBlocks[2].innerText = data.action;
    infoBlocks[3].innerHTML = data.common.join("<br>");
    infoBlocks[4].innerHTML = data.serious.join("<br>");

    resultsBox.style.display = "block";
}


document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("medicineSearch");
    const btn = document.querySelector(".search-btn");

    async function search() {
        const value = input.value.trim();
        if (!value) return;

        showMessage("Searching medicine…");

        const data = await fetchMedicine(value);

        if (!data) {
            showMessage("Medicine not found.");
            return;
        }

        renderMedicine(data);
    }

    btn.addEventListener("click", search);
    input.addEventListener("keydown", e => {
        if (e.key === "Enter") search();
    });
});
