let applicationsChecked = []
const submitButton = document.getElementById('submit-selected-apps-btn')

function submitBulkMarkAsComplete(url) {
    console.log('submitBulkMarkAsComplete');
    console.log(applicationsChecked)
    const form = document.createElement('form');
    console.log(url)
    form.action = url;
    form.method = 'POST'
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
    console.log('selectAllApplications');
    for(let i = 0; i < applications.length; i++) {
        document.getElementById(applications[i]).checked = true;
        applicationsChecked.push(applications[i]);
    }
    submitButton.classList.remove('govuk-button--disabled')
    submitButton.removeAttribute('disabled');
    console.log(applicationsChecked)
}

function clearAllApplications(applications) {
    console.log('clearAllApplications');
    for(let i = 0; i < applications.length; i++) {
        document.getElementById(applications[i]).checked = false;
    }
    applicationsChecked = [];
    submitButton.classList.add('govuk-button--disabled')
    submitButton.setAttribute('disabled', 'disabled');
    console.log(applicationsChecked)
}

function selectOrDeselectApplication(application) {
    console.log('selectOrDeselectApplication');
    const applicationReference = document.getElementById(application);
    if (applicationReference.checked) {
        applicationsChecked.push(application);
        console.log(submitButton)
        submitButton.classList.remove('govuk-button--disabled');
        submitButton.removeAttribute('disabled');
    }

    if (!applicationReference.checked) {
        const index = applicationsChecked.indexOf(application);
        if (index > -1) {
          applicationsChecked.splice(index, 1);
        }
        if (!applicationsChecked.length) {
            submitButton.classList.add('govuk-button--disabled')
            submitButton.setAttribute('disabled', 'disabled');
        }
    }
    console.log(applicationsChecked)
}

