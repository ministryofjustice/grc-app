let applicationsChecked = [];
let submitButton;

window.onload = function() {
    const urlAnchor = window.location.hash;
    if (urlAnchor) {
        const id = urlAnchor.substring(urlAnchor.indexOf("#")+1);
        submitButton = document.getElementById('submit-selected-apps-btn-' + id);
    }
}

function tabClicked(id, applications) {
    const tabId = id
    if (id) {
        id = id.replace('tab_', '');
    }

    submitButton = document.getElementById('submit-selected-apps-btn-' + id)

    const tab = document.getElementById(tabId)
    if (!tab.classList.contains('govuk-tabs__list-item--selected')) {
        applicationsChecked = []
        if (applications && applications.length > 0) {
            clearAllApplications(applications);
        }
    }
}

function submitBulkMarkAsComplete(url) {
    const form = document.createElement('form');
    form.action = url;
    form.method = 'POST';
    if (applicationsChecked.length) {
        for (let i = 0; i < applicationsChecked.length; i++) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = applicationsChecked[i];
            hiddenField.value = applicationsChecked[i];

            form.appendChild(hiddenField);
        }
        document.body.appendChild(form);
        form.submit();
    }
}

function selectAllApplications(applications) {
    applicationsChecked = [];
    for(let i = 0; i < applications.length; i++) {
        document.getElementById(applications[i]).checked = true;
        applicationsChecked.push(applications[i]);
    }
    submitButton.classList.remove('govuk-button--disabled');
    submitButton.removeAttribute('disabled');
}

function clearAllApplications(applications) {
    for(let i = 0; i < applications.length; i++) {
        document.getElementById(applications[i]).checked = false;
    }
    applicationsChecked = [];
    submitButton.classList.add('govuk-button--disabled');
    submitButton.setAttribute('disabled', 'disabled');
}

function selectOrDeselectApplication(application) {
    const applicationReference = document.getElementById(application);
    if (applicationReference.checked) {
        applicationsChecked.push(application);
        submitButton.classList.remove('govuk-button--disabled');
        submitButton.removeAttribute('disabled');
    }

    if (!applicationReference.checked) {
        const index = applicationsChecked.indexOf(application);
        if (index > -1) {
          applicationsChecked.splice(index, 1);
        }
        if (!applicationsChecked.length) {
            submitButton.classList.add('govuk-button--disabled');
            submitButton.setAttribute('disabled', 'disabled');
        }
    }
}

//Select all case checkboxes and enable the apply button
function selectAllCases() {
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.govuk-checkboxes__input');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });

    const applyButton = document.getElementById('submit-selected-apps-btn-new');
    applyButton.disabled = false;
    applyButton.classList.remove('govuk-button--disabled');
}

//Clear all case checkboxes and disable the apply button
function clearAllCases() {
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.govuk-checkboxes__input');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    const applyButton = document.getElementById('submit-selected-apps-btn-new');
    applyButton.disabled = true;
    applyButton.classList.add('govuk-button--disabled');
}

//Enable the apply button if any case checkboxes are selected
function handleNewCaseCheckbox() {
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.govuk-checkboxes__input');
    const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    const applyButton = document.getElementById('submit-selected-apps-btn-new');
    applyButton.disabled = !anyChecked;
    if (anyChecked) {
        applyButton.classList.remove('govuk-button--disabled');
    } else {
        applyButton.classList.add('govuk-button--disabled');
    }
}

async function submitNewCaseRegistration() {
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.govuk-checkboxes__input:checked');
    const applications = Array.from(checkboxes).map(checkbox => checkbox.id);
    console.log('applications:', applications);
    
    if (applications.length === 0) {
        return;
    }

    try {
        for (const referenceNumber of applications) {
            console.log('Sending request for reference number:', referenceNumber);
            
            try {
                const detailsResponse = await fetch(`/applications/${referenceNumber}`);
                if (!detailsResponse.ok) {
                    throw new Error(`Failed to fetch application details: ${detailsResponse.status}`);
                }

                const htmlContent = await detailsResponse.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlContent, 'text/html');

                // Extract the data from the HTML
                // You'll need to adjust these selectors based on your HTML structure
                const applicationDetails = {
                    firstName: doc.querySelector('#value-grc-first-name').textContent.trim(),
                    lastName: doc.querySelector('#value-grc-last-name').textContent.trim(),
                };
                console.log('Parsed application details:', applicationDetails);

                const requestBody = {
                    'jurisdictionId': 2000000,
                    'onlineMappingCode': 'APPEAL_OTHER',
                    'contactFirstName': applicationDetails.firstName,
                    'contactLastName': applicationDetails.lastName,
                    'contactPhone': '07700900000',
                    'contactEmail': 'test@example.com',
                    'contactPostalCode': 'SW1A 1AA',
                    'contactCity': 'London',
                    'contactCountry': 'UK',
                    'documentsURL': 'https://example.com/docs',
                    'referenceNumber': referenceNumber
                };
                console.log('Request body:', requestBody);

                const response = await fetch('/glimr/api/tdsapi/registernewcase', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': 'apikey TEST_KEY'
                    },
                    body: JSON.stringify(requestBody)
                });

                console.log('Response status:', response.status);
                const responseText = await response.text();

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}, body: ${responseText}`);
                }

                const data = JSON.parse(responseText);
                console.log('Case registered:', data);
            } catch (fetchError) {
                console.error('Fetch error:', fetchError);
                throw fetchError;
            }
        }

        // Refresh the page after successful registration
        // window.location.reload();
    } catch (error) {
        console.error('Error details:', error);
        alert('Error registering new case(s). Please try again. Check console for details.');
    }
}
