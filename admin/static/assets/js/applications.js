let applicationsChecked = [];
let submitButton = document.getElementById('submit-selected-apps-btn-new');

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

/**
Removes application from applicationChecked array

params: application: application to be removed
**/
function removeApplicationFromChecked(application) {
    applicationsChecked = applicationsChecked.filter(applicationChecked => applicationChecked !== application);
}

/**
Disables submit button
**/
function disableSubmitButton() {
    if (applicationsChecked.length == 0) {
        submitButton.classList.add('govuk-button--disabled');
        submitButton.setAttribute('disabled', 'disabled');
    }
}

/**
Enables submit button
**/
function enableSubmitButton() {
    if (applicationsChecked.length > 0) {
        submitButton.classList.remove('govuk-button--disabled');
        submitButton.removeAttribute('disabled');
    }
}

/**
Selects all applications to be checked.

Adds all cases to applicationsChecked array, marks each case as checked, and enables submit button.

params: applications: applications to be marked for checked
**/
function selectAllApplications(applications) {
    applicationsChecked = [];
    for(let i = 0; i < applications.length; i++) {
        checkbox = document.getElementById(applications[i]);
        if (!checkbox.classList.contains('checkbox-registered')) {
            checkbox.checked = true;
            applicationsChecked.push(applications[i]);
        }
    }
    enableSubmitButton()
}

/**
Clears all applications from being checked,

Removes all cases from applicationsChecked array, marks each case as unchecked, and disables submit button.

params: applications: applications to be cleared from being checked
**/
function clearAllApplications(applications) {
    for(let i = 0; i < applications.length; i++) {
        checkbox = document.getElementById(applications[i]);
        if (!checkbox.classList.contains('checkbox-registered')) {
            checkbox.checked = false;
        }
    }
    applicationsChecked = [];
    disableSubmitButton();
}

/**
Selects or deselects an application

params: application: application reference number to be selected or deselected
**/
function selectOrDeselectApplication(application) {
    const applicationReference = document.getElementById(application);
    if (applicationReference.checked) {
        applicationsChecked.push(application);
        enableSubmitButton();
    } else if (!applicationReference.checked) {
        removeApplicationFromChecked(application);
        disableSubmitButton();
    }
}

/**
Sets case to be registered and therefore removed from applicationsChecked, disabled, and text changed to registered.

params: application: application to be case registered
**/
function setCaseRegistered(application) {
    const checkbox = document.getElementById(application);
    const label = document.getElementById(`label-${application}`);
    removeApplicationFromChecked(application);
    checkbox.classList.remove('checkbox-unregistered');
    checkbox.classList.add('checkbox-registered');
    checkbox.disabled = true;
    checkbox.checked = true;
    label.textContent = "Registered new case";

}

/**
Submits the selected applications for case registration and handles the GLiMR api call
**/
async function submitNewCaseRegistration() {
    if (applicationsChecked.length === 0) {
        return;
    }

    const spinner = document.getElementById('spinner');
    spinner.style.display = 'inline';

    try {
        const response = await fetch('/glimr/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({ 'applications':applicationsChecked })
            });

        const data = await response.json();
        const failedCases = data.failedCases;
        const processedCases = data.processedCases;

        if (response.ok) {
            if (failedCases.length > 0) {
                failedCases.forEach((failedCase) => {
                    console.log(`Error case: ${failedCase}`);
                });
            }

            if (processedCases.length > 0) {
                processedCases.forEach((processedCase) => {
                    setCaseRegistered(processedCase);
                    removeApplicationFromChecked(processedCase);
                });
            }

            disableSubmitButton()

        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

    } catch (fetchError) {
        console.error('Fetch error:', fetchError);
    } finally {
        spinner.style.display = 'None';
    }
}

