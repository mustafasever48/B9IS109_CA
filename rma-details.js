document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const rmaId = urlParams.get('rmaId');

    fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/technical/rma_details?rmaId=${rmaId}`)
        .then(response => response.json())
        .then(data => {
            const rmaDetailsHtml = createRmaDetailsHtml(data);
            document.getElementById('rmaDetailsContainer').innerHTML = rmaDetailsHtml;

            document.getElementById('productDefect').value = data['Product_Defect'];
            document.getElementById('resultIssue').value = data['Result_Issue'];
        })
        .catch(error => console.error('Error:', error));
});
function createRmaDetailsHtml(data) {

    const formattedInspactionDate = new Date(data['Inspaction_Start_Date']).toLocaleDateString();

    const html = `
                    <div id="rmaDetails">
                        <table>
                            <tr>
                                <th>Inspaction Start Date</th>
                                <td>${formattedInspactionDate}</td>
                            </tr>
                            <tr>
                                <th>Inspection Completion Date</th>
                                <td><button class="updateButton" onclick="updateCompletionDate()">Update</button></td>
                            </tr>
                            <th>Product Defect</th>
                            <td><textarea name="productDefect" id="productDefect">${data['Product_Defect']}</textarea> <button class="updateButton" onclick="updateProductDefect()">Update</button></td>
                        </tr>
                        <tr>
                            <th>Check Issue</th>
                            <td>${data['Check_Issue']}</td>
                        </tr>
                        <tr>
                            <th>Result Issue</th>
                            <td><textarea name="resultIssue" id="resultIssue">${data['Result_Issue']}</textarea> <button class="updateButton" onclick="updateResultIssue()">Update</button></td>
                        </tr>
                        <tr>
                            <th>Product Name</th>
                            <td>${data['Product_Name']}</td>
                        </tr>
                        <tr>
                            <th>Technician Name</th>
                            <td>${data['Tech_Name']}</td>
                        </tr>
                        <!-- Ekstra bilgiler için -->
                        <tr>
                            <th>Brand Information</th>
                            <td>${data['Brand_Name']}<br>${data['Brand_Website']}<br>${data['Brand_Category']}<br>${data['Brand_Details']}</td>
                            </tr>
                                <tr>
                                    <th>Model Information</th>
                                    <td>${data['Model_Name']}<br>${data['Model_Category']}<br>${data['Model_Details']}</td>
                                    </tr>
                                        <tr>
                                            <th>Customer Information</th>
                                            <td>${data['Customer_Name']}<br>${data['Customer_Address']}<br>${data['Customer_Phone']}<br>${data['Customer_Email']}</td>
                                            </tr>
                                            </table>
                                            </div>
                                            <button id="deleteButton" onclick="deleteRma()">Delete RMA</button>

                                        </div>
                                        `;

    return html;
}

function updateResultIssue() {
    const rmaId = new URLSearchParams(window.location.search).get('rmaId');
    const resultIssue = document.getElementById('resultIssue').value;

    if (!resultIssue.trim()) {
        alert('Result Issue cannot be empty.');
        return;
    }

    fetch('https://msubuntu.northeurope.cloudapp.azure.com:8080/update_rma', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `rma_id=${rmaId}&result_issue=${resultIssue}`,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            alert(`Updated Result Issue: ${resultIssue}`);
        })
        .catch(error => {
            console.error('Error:', error.message);
            alert('An error occurred while updating Result Issue.');
        });
}
function updateProductDefect() {
    const rmaId = new URLSearchParams(window.location.search).get('rmaId');
    const productDefect = document.getElementById('productDefect').value;

    if (!productDefect.trim()) {
        alert('Product Defect cannot be empty.');
        return;
    }

    fetch('https://msubuntu.northeurope.cloudapp.azure.com:8080/update_product_defect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `rma_id=${rmaId}&product_defect=${productDefect}&product_defecet=`,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            alert(`Updated Product Defect: ${productDefect}`);
        })
        .catch(error => {
            console.error('Error:', error.message);
            alert('An error occurred while updating Product Defect.');
        });
}
function updateCompletionDate() {
    const rmaId = new URLSearchParams(window.location.search).get('rmaId');
    const currentDate = new Date();
    const formattedDate = currentDate.toISOString().split('T')[0];

    fetch('https://msubuntu.northeurope.cloudapp.azure.com:8080/update_inspection_completion_date', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            rma_id: rmaId,
            completion_date: formattedDate,
        }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            alert(`Updated Inspection Completion Date: ${formattedDate}`);
        })
        .catch(error => {
            console.error('Error:', error.message);
            alert('An error occurred while updating Inspection Completion Date.');
        });
}


function deleteRma() {
    const rmaId = new URLSearchParams(window.location.search).get('rmaId');

    const confirmation = confirm("Are you sure you want to delete this case?");
    if (!confirmation) {
        return;
    }

    fetch(`https://msubuntu.northeurope.cloudapp.azure.com:8080/delete_rma?rma_id=${rmaId}`, {
        method: 'DELETE',
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            alert(`Case deleted successfully.`);
        })
        .catch(error => {
            console.error('Error:', error.message);
            alert('An error occurred while deleting the case.');
        });

}
