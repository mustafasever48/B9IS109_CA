function fetchData() {
    const serialNumber = document.getElementById("serialNumber").value;

    fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/?serial_number=${serialNumber}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("tableBody");
            const warrantyStatus = document.getElementById("warrantyStatus");

            tableBody.innerHTML = "";

            data.Results.forEach(x => {
                const newRow = document.createElement("tr");
                const cells = ["Brand_Name", "Model_Name", "Product_Name", "Serial_Number", "Product_Sold_Date"];

                cells.forEach(cell => {
                    const newCell = document.createElement("td");

                    if (cell === "Product_Sold_Date") {
                        const productSoldDate = new Date(x[cell]);
                        const daysRemaining = Math.floor((productSoldDate - new Date()) / (1000 * 60 * 60 * 24));
                        newCell.textContent = x[cell];
                        warrantyStatus.textContent = `Warranty Status: ${daysRemaining <= 720 ? 'Warranty is still valid.' : 'Warranty has expired.'}`;
                    } else {
                        newCell.textContent = x[cell];
                    }

                    newRow.appendChild(newCell);
                });

                tableBody.appendChild(newRow);
            });
        })
        .catch(error => console.error('Error:', error));
}

function createRma() {
    const serialNumber = document.getElementById("serialNumber").value;
    const issueDescription = document.getElementById("issueDescription").value;

    fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/create_rma?serial_number=${serialNumber}&issue_description=${issueDescription}`)
        .then(response => response.json())
        .then(data => {
            alert(`RMA Case ID: ${data.RMA_ID}`);
        })
        .catch(error => console.error('Error:', error));
}

function checkRmaStatus() {
    const serialNumberCheck = document.getElementById("serialNumberCheck").value;

    fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/check_rma_status?serial_number=${serialNumberCheck}`)
        .then(response => response.json())
        .then(data => {
            const rmaTableBody = document.getElementById("rmaTableBody");
            const rmaStatus = document.getElementById("rmaStatus");

            rmaStatus.textContent = "";
            rmaTableBody.innerHTML = "";

            if (data.length > 0) {
                data.forEach(rma => {
                    const newRow = document.createElement("tr");
                    const cells = ["RMA_ID", "Inspaction_Start_Date", "Inspeciton_Completion_Date", "Product_Defect", "Check_Issue", "Result_Issue", "Product_ID", "Serial_Number", "Product_Name"];

                    cells.forEach(cell => {
                        const newCell = document.createElement("td");

                        if (cell.includes("Date")) {
                            const dateValue = rma[cell] ? new Date(rma[cell]).toISOString().split('T')[0] : "";
                            newCell.textContent = dateValue;
                        } else {
                            newCell.textContent = rma[cell];
                        }

                        newRow.appendChild(newCell);
                    });

                    rmaTableBody.appendChild(newRow);
                });
            } else {
                rmaStatus.textContent = 'RMA not found.';
            }
        })
        .catch(error => console.error('Error:', error));
}
