
[Gender Recognition Certificate service](../README.md) >
[Developer documentation](README.md) >
Our environments

# Our environments

The Gender Recognition Certificate service currently has 3 environments:

* **Development**  
  This is mainly used by developers. We need to port forward this environment to our local machines
  * Public-facing website: Run `kubectl port-forward pod <app pod> -n grc-dev -n grc-dev 3000:3000` and go to [http://localhost:3000]("http://localhost:3000")
  * Admin website: Run `kubectl port-forward pod <admin pod> -n grc-dev -n grc-dev 3001:3001` and go to [http://localhost:3001]("http://localhost:3001")
  * Dashboard facing website: Run `kubectl port-forward pod <dashboard pod> -n grc-dev -n grc-dev 3002:3002` and go to [http://localhost:3002]("http://localhost:3002")


* **Staging**  
  This is where we do testing
  * Public-facing website: https://preprod.gender-recognition.service.justice.gov.uk/
  * Admin website: https://preprod.admin.gender-recognition.service.justice.gov.uk/
  * Dashboard website: https://preprod.dashboard.gender-recognition.service.justice.gov.uk/
  * JWKS url: https://preprod.jwks.apply-gender-recognition-certificate.service.gov.uk/.well-known/jwks.json


* **User Acceptance Testing (UAT)**  
  This is where we do business testing
  * Public-facing website: https://uat.gender-recognition.service.justice.gov.uk/
  * Admin website: https://uat.admin.gender-recognition.service.justice.gov.uk/
  * Dashboard website: https://uat.dashboard.gender-recognition.service.justice.gov.uk/


* **Production**  
  The real / live website
  * Public-facing website: https://apply-gender-recognition-certificate.service.gov.uk  
  * Admin website: https://admin.apply-gender-recognition-certificate.service.gov.uk  
  * Dashboard website: https://dashboard.apply-gender-recognition-certificate.service.gov.uk  
  * JWKS url: https://jwks.apply-gender-recognition-certificate.service.gov.uk/.well-known/jwks.json
  