
[Gender Recognition Certificate service](../README.md) >
[Developer documentation](README.md) >
Deployments

# Deployments

We use [CircleCI](https://circleci.com/?utm_term=circle%20ci&utm_campaign=sem-google-dg--emea-en-brandAuth-tCPA-auth-brand&utm_source=google&utm_medium=sem&utm_content=&hsa_acc=2021276923&hsa_cam=20616025375&hsa_grp=155812226562&hsa_ad=675839591952&hsa_src=g&hsa_tgt=kwd-358251371487&hsa_kw=circle%20ci&hsa_mt=e&hsa_net=adwords&hsa_ver=3&gad_source=1&gad_campaignid=20616025375&gbraid=0AAAAAD2FEzwRynTxx_b1w9CqtAYxR57QC&gclid=CjwKCAjwiNXFBhBKEiwAPSaPCWje0aU7DvIIRk2W4coUWL9n0x7JCSjtd1x1WFcUFeTb9l3W9BFOlBoCs4wQAvD_BwE) for our deployments.  
Here are the [CircleCI pipelines for the GRC service](https://app.circleci.com/pipelines/github/ministryofjustice/grc-app).

## When are deployments run?
* Pushing to the `master` **branch** deploys to the `production` environment  
  You can see the [production deployments here](https://app.circleci.com/pipelines/github/ministryofjustice/grc-app?branch=master)


* Pushing a **tag** named `UAT` deploys to the `UAT` environment  
  You can see the [UAT deployments here](https://app.circleci.com/pipelines/github/ministryofjustice/grc-app?branch=UAT)


* Pushing a **tag** named `staging` deploys to the `staging` environment  
  You can see the [staging deployments here](https://app.circleci.com/pipelines/github/ministryofjustice/grc-app?branch=staging)


* Pushing a **tag** named `RST-*` deploys to the `dev` environment  
  You can see the [dev deployments here](https://app.circleci.com/pipelines/github/ministryofjustice/grc-app)


