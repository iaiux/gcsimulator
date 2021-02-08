# gcdocker
The  GreenCharge  simulator reproduces in a virtual environment the events that occur in a real energy smart neighborhood (ESN) using a collection of real misured data [1][1] http://somewebsite.org. It is based on the original  CoSSMic  simulator [2][2], and allows to extend the evaluation capability in real pilots, which are limited in the heterogeneity and number of devices and in the duration of operating trials.  
The simulator is based on the discrete-event simulation (DES) model where the system appears as a discrete sequence of events in time.  


The Container based deployment configuration allows for an easy deploy of the simulation platform on the user’s workstation, independently from the Operating System. The software architecture is shown in Figure 
![Contaner based deployment](/docs/images/docker_arc.png)

Using both a virtual or a real network many containerized components interoperate through a loosely coupled integration. The blue box represents the simulation engine and its  Graphical User Interface (GUI). The two components use a volume to access simulation input and output data such as configuration of scenarios, time-series and  results.
The XMPP server provides a peer-to-peer communication overlay for multi-agents  distributed implementation. A volume is used to save user-credentials, as the simulator can be used by multiple users who can run their simulations in parallel, in one or in multiple containers.
An optimization model can be integrated as Energy Management Systems (EMS) that  runs in its own container and  uses the Simulator interface to receive simulation events and to return the optimal energy schedule. In particular, the GreenCharge project will evaluate two different EMS innovative technological solutions, developed by the University of Oslo and by the Eurecat partner. Here we investigate an alternative solution that is used also to demonstrate how the simulation platform works.

[1]: R. Aversa, D. Branco, B. Di Martino, and S. Venticinque.  Greenchargesimulation  tool.Advances in Intelligent Systems and Computing,  1150AISC:1343–1351, 2020.
[2]:A. Amato, R. Aversa, B. Di Martino, M. Scialdone, and S. Venticinque. Asimulation approach for the optimization of solar powered smart migro-grids.Advances in Intelligent Systems and Computing, 611:844–853, 2018.

## Documentation
* [User Guide](docs/gcsim/user_guide/index.html)
* [API documentation](docs/gcsim/api/index.html)



## Build Simulator image
```
cd docker
docker build . --tag gcsim
```

## Build prosody and simulator containers
```
cd docker-compose up
```

The prosody configuration and the Simulation directory are mapped to the host directories
Currently the simulator container waits for a bash connection

## Run the simulator
```
docker exec -it docker_gcsimulator_1 bash
./starter.sh
```
