# Reverse-engeering [https://apply.jackfrosttower.com](https://apply.jackfrosttower.com)

Objective 10 of the [2021 SANS Holiday Hack Challenge](https://2021.kringlecon.com)
involved exploiting an SSRF vulnerability on a website to fetch AWS credentials
from an internal AWS meta-data service. By abusing this SSRF, it's possible to
reverse engineer the container the website runs in and spin up a local version. 

The python code used to leverage the SSRF is also included here.

[pugpug](https://twitter.com/joeammond)
