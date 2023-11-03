let applicationsChecked = [];
let submitButton;

window.onload = function() {
    urlAnchor = window.location.hash;
    if (urlAnchor) {
        id = urlAnchor.substring(urlAnchor.indexOf("#")+1);
        submitButton = document.getElementById('submit-selected-apps-btn-' + id);
    }
}

function tabClicked(id, applications) {
    tabId = id
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
