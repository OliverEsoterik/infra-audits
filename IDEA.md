i have this idea to start a consulting offering for IT audits.. my background is DevOps Engineer / Architecture / Infrastructure Lead.
The core idea is i create a repository with Skills and Graph Loops. so everytime i have a client who needs some kind of Infrastructure audit i just run the workflow and get reports with all findings and as well recommendations.
The repo should be extensible. so i have a collection of skills and i can add more and more skills to it to extend it. 
also we need to keep in mind e.g. the client wants to audit "Azure Cloud" or "vCenter" or "vmware" or its "Oracle DBs" or its "Windows Servers 2022" etc. etc. 
so we need probably kind of modules. 
We need to have the ability to plug into every client organization very quickly. we just need like e.g. a user or a service account. and then we are ready to go.
The clients may also have kind of guidelines where they need to be compliant with e.g. Nis2 or something like that. so there are benchmarks we have to evaluate everything against.
when doing these kind of checks - sometimes its easier to have an e.g. python script than just a SKILL.md file.
so we need a good structure.
the whole program at the end should be able to audit everything the clients wants to audit. 
maybe they want to check if their terraform code is compliant. or they want to check if their kubernetes policies are compliant. in general and against the specific guidelines probably (i dont know exactly whats best practice here - but we should aim for best industry practice like the major IT audit firms).
maybe they want to check if their active directory group management is compliant - or if not - whats the best practice it should be set up.
Always gain for best industry practices.
maybe they want to audit their AD infrastructure only. maybe they want to audit their cloud environments only - whole cloud organizations e.g. azure or subscriptions only - or whole google or aws orgs. or only single projects.
everything can happen with the client but our repo should have a perfect structure to fulfill those needs. we do not need the skills for that now - but we should have a structure to fill in those skills very easily and have our repo extensible.
if required it would also be good to have kind of "prompt templates" maybe. i am not sure if required or if we need them. think about that.
my workflow for me as the IT auditor should be straight forward -> the client just gives me a service account or a user account - tells me what he wants to audit (e.g. his kubernetes cluster or his 10 vcenters or his 20 Windows Servers, or his 30 SQL databases etc. etc. and then - maybe he has also information against what kind of guidelines he wants to audit (e.g. nis2) or just best practice -> i just run the Skill perform the whole Audit and will hand the report to the client with everything in place.

