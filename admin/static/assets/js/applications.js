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
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.checkbox-unregistered');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });

    const applyButton = document.getElementById('submit-selected-apps-btn-new');
    applyButton.disabled = false;
    applyButton.classList.remove('govuk-button--disabled');
}

//Clear all case checkboxes and disable the apply button
function clearAllCases() {
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.checkbox-unregistered');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    const applyButton = document.getElementById('submit-selected-apps-btn-new');
    applyButton.disabled = true;
    applyButton.classList.add('govuk-button--disabled');
}

//Enable the apply button if any case checkboxes are selected
function handleNewCaseCheckbox() {
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.checkbox-unregistered');
    const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    const applyButton = document.getElementById('submit-selected-apps-btn-new');
    applyButton.disabled = !anyChecked;
    if (anyChecked) {
        applyButton.classList.remove('govuk-button--disabled');
    } else {
        applyButton.classList.add('govuk-button--disabled');
    }
}

function setCaseRegistered(application) {
    const checkbox = document.getElementById(application);
    const label = document.getElementById(`label-${application}`);

    checkbox.classList.remove('checkbox-unregistered');
    checkbox.classList.add('checkbox-registered');
    checkbox.disabled = true
    checkbox.checked = true

    label.textContent = "Registered new case"

}

async function submitNewCaseRegistration() {
    const checkboxes = document.querySelector('.new-table').querySelectorAll('.checkbox-unregistered:checked');
    const applications = Array.from(checkboxes).map(checkbox => checkbox.id);

    if (applications.length === 0) {
        console.log("No applications selected.");
        return;
    }

    try {
        console.log(applications);
        const response = await fetch('/glimr/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ applications })
            });

        const data = await response.json();
        const failedCases = data.failedCases
        const processedCases = data.processedCases

        if (response.ok) {
            console.log(data)
            if (failedCases.length > 0) {
                //go through the failed array
                failedCases.forEach((failedCase) => {
                    alert(`Error case: ${failedCase}`);
                });
            }

            if (processedCases.length > 0) {
                processedCases.forEach((processedCase) => {
                    setCaseRegistered(processedCase)
                });
            }

        } else {

            alert(`Error cases: ${failedCases}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

    } catch (fetchError) {
        console.error('Fetch error:', fetchError);
    }
}

