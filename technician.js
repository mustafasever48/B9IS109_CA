function refreshPageData() {
    const rmaTableBody = document.getElementById("rmaTableBody");
    rmaTableBody.innerHTML = ""; // Mevcut tabloyu temizle

    fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/technical`)
        .then(response => response.json())
        .then(data => {
            data.forEach(rma => {
                const newRow = document.createElement("tr");
                const cells = ["RMA_ID", "Inspaction_Start_Date", "Inspeciton_Completion_Date", "Product_Defect", "Check_Issue", "Result_Issue", "Product_ID", "Serial_Number", "Product_Name", "Technician_ID"];

                cells.forEach(cell => {
                    const newCell = document.createElement("td");

                    if (cell.includes("Date")) {
                        const dateValue = rma[cell] ? new Date(rma[cell]).toISOString().split('T')[0] : "";
                        newCell.textContent = dateValue;
                    } else {
                        const cellValue = rma[cell] !== null ? rma[cell] : "";
                        newCell.textContent = cellValue;
                    }

                    newRow.appendChild(newCell);
                });

                const assignCell = document.createElement("td");

                const technicianSelect = document.createElement("select");
                technicianSelect.classList.add("technician-select");

                fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/technicians`)
                    .then(response => response.json())
                    .then(technicians => {
                        if (technicians.length > 0) {
                            technicians.forEach(technician => {
                                const option = document.createElement("option");
                                option.value = technician['Technician_ID'];
                                option.textContent = technician['Tech_Name'];
                                technicianSelect.appendChild(option);
                            });

                            technicianSelect.style.display = "block";

                            const assignButton = document.createElement("button");
                            assignButton.classList.add("assign-button");
                            assignButton.textContent = "Assign Technician";
                            assignButton.addEventListener("click", function () {
                                const selectedTechnicianId = technicianSelect.value;
                                const rmaId = rma['RMA_ID'];
                                fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/assign_technician`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/x-www-form-urlencoded',
                                    },
                                    body: `rma_id=${rmaId}&technician_id=${selectedTechnicianId}`,
                                })
                                    .then(response => response.json())
                                    .then(responseData => {
                                        assignCell.textContent = selectedTechnicianId;
                                        assignButton.style.display = "none";
                                    })
                                    .catch(error => console.error('Data submission error:', error));
                            });

                            assignCell.appendChild(technicianSelect);
                            assignCell.appendChild(assignButton);
                        }
                    })
                    .catch(error => console.error('Technician data extraction error:', error));

                if (rma['Technician_ID'] !== null) {
                    assignCell.textContent = rma['Technician_ID'];
                }

                newRow.appendChild(assignCell);

                const viewDetailsCell = document.createElement('td');
                const viewDetailsButton = document.createElement('button');
                viewDetailsButton.classList.add('view-details-button');
                viewDetailsButton.textContent = 'View Details';
                viewDetailsButton.addEventListener('click', function () {
                    window.location.href = `rma-details?rmaId=${rma['RMA_ID']}`;
                });

                viewDetailsCell.appendChild(viewDetailsButton);
                newRow.appendChild(viewDetailsCell);

                rmaTableBody.appendChild(newRow);
            });
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener("DOMContentLoaded", refreshPageData);
