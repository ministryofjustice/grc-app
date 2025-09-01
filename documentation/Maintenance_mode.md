
[Gender Recognition Certificate service](../README.md) >
[Developer documentation](README.md) >
How to put the service into Maintenance Mode

# How to put the service into Maintenance Mode / make the service unavailable

## What is this for?
It may occasionally be necessary to put the application into Maintenance Mode / make the service unavailable.

For example, if we detect a problem, and want to make sure no-one uses the service whilst the service is broken.


## What does maintenance mode look like?
![img_1.png](img_1.png)


## Put service into maintenance mode?

Maintenance is set in the ingress files under the deploy > [environment] folder.

You will find code like this in uat for example:

```
  rules:
  - host: uat.gender-recognition.service.justice.gov.uk
    http:
      paths:
          - path: /
            pathType: ImplementationSpecific
            backend:
              service:
                name: grc-app-service
                port: 
                  number: 3000
```

We need to change the service name from `grc-app-service` to `maintenance-page-svc` and port `3000` to port `8080`. It will look like this:

```
  rules:
  - host: uat.gender-recognition.service.justice.gov.uk
    http:
      paths:
          - path: /
            pathType: ImplementationSpecific
            backend:
              service:
                name: maintenance-page-svc
                port: 
                  number: 8080
```

After this, either push to that environment branch, or simply apply the change using `kubectl apply -f <ingress file>`

## Take service out of maintenance mode?

Just reverse back to what it was and either push to environment or apply with kubectl.



