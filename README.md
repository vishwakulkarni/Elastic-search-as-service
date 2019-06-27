# Elastic search as a service

this is service broker extended from  [blog post](https://www.altoros.com/blog/creating-a-sample-service-broker-for-cloud-foundry-with-pythons-flask/) for
to create elastic search as a service for cloudfoundry

requirement:-

1) cloudfoundry developer access to any space ( if no space is created please refer to cloudfoundry document to create space and assign application runtime to it)
2) one VM access on aws
3) finally some patience and will to make it work

Steps to deploy "Elastic search as a service"

1) git clone https://github.com/vishwakulkarni/Elastic-search-as-service.git

2) cd Elastic-search-as-service

3) cf push --random-route

4) cf apps

(here you will get route of your application which is deployed)
example

Getting apps in org vishwa / space elk-broker as vishwa.kulkarni@gmail.com...
OK

name           requested state   instances   memory   disk   urls
elk-broker   started           1/1         512M     1G     elk-broker-example.cfapps.io

5)curl alex:bob@${broker_url}/v2/catalog

here alex is username and bob is password

6) cf create-space demo-space \
   cf target -s demo-space

create your space(demo-space) and target your cf cli to that space.

7) cf create-service-broker elk-broker  \
  alex bob https://elk-broker-example.cfapps.io \
  --space-scoped

8) cf marketplace

to check for your service live


9) cf update-service-broker elk-broker \
    alex bob https://elk-broker-example.cfapps.io

if you want to update your service then do above command



checkout https://starkandwayne.com/blog/register-your-own-service-broker-with-any-cloud-foundry/ for more.