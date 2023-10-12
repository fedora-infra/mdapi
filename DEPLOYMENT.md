# Deploying MDAPI on OpenShift

## Preparation

1. Clone the `ansible` repository to the local environment.
   ```
   git clone ssh://git@pagure.io/fedora-infra/ansible.git
   ```
2. Make the necessary changes in the deployment playbook and push them to the repository.
   ```
   nano ansible/playbooks/openshift-apps/mdapi.yml
   ```
3. Ensure that the project codebase is updated in the target branches for the relevant deployment.
   ```
   git clone https://github.com/gridhead/protop2g.git
   ```
4. Confirm that the `develop` branch is used for staging and `prod` branch is used for production.

## Deployment

1. While ensuring that the related SSH config are in place, connect to the `batcave01` node using SSH.
   ```
   ssh batcave01
   ```
2. Execute the following command when connected to the `batcave01` TTY.  
   For staging,
   ```
   sudo rbac-playbook openshift-apps/mdapi.yml -l staging
   ```  
   For production,  
   ```
   sudo rbac-playbook openshift-apps/mdapi.yml -l production
   ```
3. Follow the steps provided in the **Diagnosis** section to check the build and deployment statuses.

## Diagnosis

1. While ensuring that the related SSH config are in place, connect to the following nodes using SSH.  
   For staging  
   ```
   ssh root@os-control01.stg.iad2.fedoraproject.org
   ```  
   For production  
   ```
   ssh t0xic0der@os-control01.iad2.fedoraproject.org
   ```
2. Execute the following command to check which user you have logged in as.
   ```
   oc whoami
   ```
   Example output
   ```
   system:admin
   ```
3. List all the projects using the following projects and filter specifically for the `mdapi` namespace.
   ```
   oc projects | grep mdapi
   ```
4. List all the builds associated with the `mdapi` project namespace.
   ```
   oc -n mdapi get builds
   ```
   Example output
   ```
   NAME             TYPE     FROM          STATUS                       STARTED        DURATION
   mdapi-build-8    Docker   Git@bad0092   Failed (DockerBuildFailed)   9 months ago   17s
   mdapi-build-9    Docker   Git@435fa01   Failed (DockerBuildFailed)   9 months ago   8s
   mdapi-build-10   Docker   Git@43ddd19   Failed (DockerBuildFailed)   9 months ago   48s
   mdapi-build-23   Docker   Git@aafb5c4   Failed (DockerBuildFailed)   4 months ago   1m4s
   mdapi-build-24   Docker   Git@dd81099   Complete                     4 months ago   1m44s
   mdapi-build-25   Docker   Git@fe39071   Complete                     2 months ago   2m1s
   mdapi-build-26   Docker   Git@4081354   Complete                     2 months ago   1m56s
   mdapi-build-27   Docker   Git@4081354   Complete                     2 months ago   1m56s
   mdapi-build-28   Docker   Git@4081354   Complete                     2 months ago   2m2s
   mdapi-build-29   Docker   Git@e32fa9b   Cancelled (CancelledBuild)   4 weeks ago    12h9m37s
   ```
5. List all the pods associated with the `mdapi` project namespace.
   ```
   oc -n mdapi get pods
   ```
   Example output
   ```
   NAME                   READY   STATUS      RESTARTS   AGE
   mdapi-28282100-mvq95   0/1     Completed   0          125m
   mdapi-28282160-9xtv4   0/1     Completed   0          65m
   mdapi-28282220-hfrzf   0/1     Completed   0          5m4s
   mdapi-39-xxxdq         1/1     Running     0          19d
   ```
6. View all the logs associated with a certain pod in the `mdapi` namespace.
   ```
   oc -n mdapi logs mdapi-39-xxxdq
   ```
   Example output
   ```
   ....
   [2023-10-10 10:26:50 +0000] [INFO] index <Request GET / >
   [2023-10-10 10:27:15 +0000] [INFO] index <Request GET / >
   [2023-10-10 10:27:50 +0000] [INFO] index <Request GET / >
   [2023-10-10 10:28:15 +0000] [INFO] index <Request GET / >
   ....
   ```
7. List the routes associated with the namespace.
   ```
   oc get routes -n mdapi
   ```
   Example output
   ```
   NAME    HOST/PORT                     PATH   SERVICES   PORT       TERMINATION     WILDCARD
   mdapi   mdapi.stg.fedoraproject.org          mdapi      8080-tcp   edge/Redirect   None
   ```
8. Get into the TTY of a certain pod.
   ```
   oc -n mdapi rsh mdapi-41-q9m8q
   ```
   Example output
   ```
   sh-5.2$ mdapi --version
   mdapi, version 3.1.3
   ```

## Troubleshooting

Please connect with [Fedora Infrastructure](https://pagure.io/fedora-infrastructure/issues) for more information.
