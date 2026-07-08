*This project has been created as a part of the 42 curriculum by <mbotelho>mbotelho*

# Fly-in

## Description

Fly-in is an optimized routing system designed to navigate a fleet of autonomous drones from a starting base to a target location.

### The Maps

The framework parses map environments from standard text using a specific layout.

**Map Layout**

All maps must include exactly one ```start_hub``` and one ```end_hub```. Any metadata is defined within brackets and completely optional. For hubs, metadata specifies the zone type (normal, blocked, restricted, priority), color, and maximum drone capacity. For connections, metadata defines the maximum capacity of that link.

All connections must link previously defined hubs, and duplicate hubs of connections are forbidden. Connections are fully bidirectional; for example, a connection identified as ```start-end``` is treated identically to ```end-start```.

If the ```max_drones``` capacity specified for the ```start_hub``` or ```end_hub``` is smaller than the total number of drones in simulation, it will be ignored to allow all drones to deploy and arrive safely.

```
# comments are prefixed with '#' and ignored
nb_drones: 5
start_hub: start x y [color=green zone=priority max_drones=5]
hub: middle_hub x y [color=green zone=restricted max_drones=2]
end_hub: end x y

connection: start_hub-middle_hub [max_link_capacity = 2]
connection: middle_hub-end_hub
```

Note: ```x``` and ```y``` represent the coordinates of a hub in space

|   Zone Type        |  Movement Cost      |  Description                                                                 |   
| -------------------| --------------------|------------------------------------------------------------------------------|
| normal             | 1                   | Normal movement                                                              |
| blocked            | Inaccessible        | Inaccessible to any drone                                                    |
| restricted         | 2                   | Drone can move through this type of zone but it takes two turns (remains in the connection for one turn) |                                    |
| priority           | 1                   | Should be prioritized if it has the lowest cost along with other zone        |


### Algorithm

To optimize throughput across overlapping graph structures, the simulation engine calculates static travel costs and routes drones using structured discrete turn-mechanics:

```
Assign Base Weights -> (Normal/Priority: 1 Turn, Restricted: 2 Turns)

Function Dijkstra(graph, start, end):
    Evaluate optimal cost-weighted single-source paths
    Return dynamic array of prioritized path nodes

While remaining_undelivered_drones > 0:
    For each simulation step:
        1. Process exiting drones to immediately free zone capacity
        2. Validate 'max_drones' and 'max_link_capacity' for incoming moves
        3. Dispatch next movement step OR execute a strategic wait sequence
```

To find the fastest path for each drone, Dijkstra's Algorithm was implemented. It was chosen because it is one of the best at finding the shortest path, it is simple to comprehend, and it is straightforward to implement. It works perfectly for this system because we can directly treat the zone travel costs as fixed edge weights. By evaluating the paths based on these turn costs, the algorithm guarantees the quickest route to the destination before any drone movement begins.

### Visual Representation Features

The visualization was built using Pygame to create a clear, real-time graphical representation of the simulation. The zone type of each hub has been displayed as a facilitator for the user. An explicit turn counter is integrated directly into the display interface. This makes it much easier to visualize how many simulation turns have gone past and helps easily check that the algorithm is running efficiently within the target turn benchmarks.

The terminal displays a summary of each turn movement and the total turns done during the run.

## Instructions

### Instalation and Usage
Clone this repository
```
git@github.com:megyant/42_Fly-in.git fly-in
cd fly-in
```

Install project dependencies and execute the simulation using the provided maps and script
```
# install dependencies
make install

# run script
make run
```
OR

Execute the simulation manually
```
# install dependencies
make install

# activate virtual environment with dependencies installed
source .venv/bin/activate

# run the program
# python3 -m src path_to_file/map.txt
python3 -m src maps/test.txt
```

### Standards Compliance

The codebase maintains comprehensive type safety check

```
# Run flake8 compliance and static check via mypy
make lint
```

For a more thorough testing run:
```
# Run flake8 compliance and strict static check via mypy
make lint-strict
```

## Resources
### Dijkstra Algorithm
- [Mastering the essentials of dijkstra and A* algorithms](https://brandonkindred.medium.com/mastering-pathfinding-the-essentials-of-dijkstra-and-a-algorithms-691b226e71c4)
- [Dijkstra's shortest path algorithm](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/)
- [Wikipedia - Dijkstra Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Dijkstra short path finder](https://brilliant.org/wiki/dijkstras-short-path-finder/)
- [Difference between dijkstra's and A*](https://www.geeksforgeeks.org/dsa/difference-between-dijkstras-algorithm-and-a-search-algorithm/)

### Others
 - [Parsing files line-by-line in python](https://codesignal.com/learn/courses/fundamentals-of-text-data-manipulation/lessons/parsing-files-line-by-line-in-python)
 - [Wikipedia - A* search Algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)


### Use of Artificial Intelligence
Claude and Gemini were used to optimize the development workflow of this project. Some usages included:
- Assist with testing the program
- Logical improvement of functions
- Improve understanding of some concepts
- Quick and small debug checks througout the making of this program
- Improve this README wording

All algorithm and implementation of the logic in this program are the author's own work.

## IMPORTANT MESSAGE

DO NOT COPY OR CHEAT, YOU WILL NOT BE HELPING YOURSELF.