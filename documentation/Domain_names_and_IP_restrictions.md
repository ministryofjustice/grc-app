
[Gender Recognition Certificate service](../README.md) >
[Developer documentation](README.md) >
Domain names and IP restrictions

# IP restrictions

We have IP restrictions in place for non-production environments so the public do not mistake them for live environments.


We also have IP restrictions in place for the admin and dashboard apps in production so that only Gender Recognition Certification service staff can access the app.

## How do I change the IP restrictions?

IP restrictions are set in the ingress files under the deploy > [environment] folder.

You will find them under code like this:

```
  annotations:
    nginx.ingress.kubernetes.io/whitelist-source-range: >-
      128.77.75.64/26,
      194.33.196.0/24,
      194.33.192.0/24,
      51.149.249.0/29,
      51.149.249.32/29,
      51.149.250.0/24,
      81.153.123.31/32,
      90.209.17.46/32,
      90.209.73.29/32,
      86.145.190.211,
      86.135.149.138,
      109.224.139.207,
      80.6.230.76
```

To add or remove IP restrictions, simply add or remove the according IP addresses from this list.

Users who are IP restricted will see:

![img.png](img.png)