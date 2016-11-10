# ndex-server2-query
Search query engine for server 2

####REST endpoint:
**verb:** POST

**url:** http://{server host}:8282/v1/network/{network uuid}/query

**content type:** application/json

**body content:** 


    {
        "terms":  <comma delimited search term string>,
        "depth": <integer between 1 - 3>, 
        "edgeLimit":  <integer edge limit> 
    }
    
    
**To run the service:**
1. Create a user qengine
2. run this command: sudo su qengine -c "nohup python -m app.api 8282 &"