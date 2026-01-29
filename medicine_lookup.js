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

    // Show container
    resultsBox.style.display = "block";

    // Set title as message
    resultsBox.querySelector(".medicine-name").innerText = msg;
    resultsBox.querySelector(".medicine-category").innerText = "";

    // Hide all info blocks
    const infoBlocks = resultsBox.querySelectorAll(".info-block");
    infoBlocks.forEach(block => {
        block.style.display = "none";
    });
}



function renderMedicine(data) {
    const resultsBox = document.getElementById("medicineResults");

    const nameEl = resultsBox.querySelector(".medicine-name");
    const categoryEl = resultsBox.querySelector(".medicine-category");

    // Re-show info blocks
    const infoContainers = resultsBox.querySelectorAll(".info-block");
    infoContainers.forEach(block => {
        block.style.display = "block";
    });

    const infoBlocks = resultsBox.querySelectorAll(".info-block p");

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

    try {
        const data = await fetchMedicine(value);

        if (!data || data.error) {
            showMessage("Medicine not found.");
            return;
        }

        renderMedicine(data);
    } catch (err) {
        console.error(err);
        showMessage("Server error. Please try again.");
    }
}


    btn.addEventListener("click", search);
    input.addEventListener("keydown", e => {
        if (e.key === "Enter") search();
    });
});
