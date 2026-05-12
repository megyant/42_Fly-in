	#!/bin/bash
    
    echo "" >&2
    echo "==== Difficulty Selection ====" >&2
    echo "" >&2
	echo "1 - Easy" >&2
	echo "2 - Medium" >&2
	echo "3 - Hard" >&2
	echo "4 - Challenger" >&2
    echo "" >&2
	read -p "Select dificulty [1-4]: " difficulty

    ########## EASY ##########

	if [ "$difficulty" = "1" ]; then
        echo "" >&2
        echo "==== Map Selection ====" >&2
        echo "" >&2
        echo "1 - 01_linear_path.txt" >&2
        echo "2 - 02_simple_fork.txt" >&2
        echo "3 - 03_basic_capacity.txt" >&2
        echo "" >&2
        read -p "Select Map [1-3]: " map

        # map 1
        if [ "$map" = "1" ]; then 
            FILE="maps/easy/01_linear_path.txt"; \
        
        # map 2
        elif [ "$map" = "2" ]; then 
            FILE="maps/easy/02_simple_fork.txt"; \

        # map 3
        elif [ "$map" = "3" ]; then 
            FILE="maps/easy/03_basic_capacity.txt";

        else
            echo "Error: Invalid Map" >&2
            exit 0
        fi
    
    ########## MEDIUM ##########
    
    elif [ "$difficulty" = "2" ]; then
        echo "" >&2
        echo "==== Map Selection ====" >&2
        echo "" >&2
        echo "1 - 01_linear_path.txt" >&2
        echo "2 - 02_simple_fork.txt" >&2
        echo "3 - 03_basic_capacity.txt" >&2
        echo "" >&2
        read -p "Select Map [1-3]: " map

        # map 1
        if [ "$map" = "1" ]; then 
            FILE="maps/medium/01_dead_end_trap.txt"; \
        
        # map 2
        elif [ "$map" = "2" ]; then 
            FILE="maps/medium/02_circular_loop.txt"; \
        
        # map 3
        elif [ "$map" = "3" ]; then 
            FILE="maps/medium/03_priority_puzzle.txt";

        else
            echo "Error: Invalid Map" >&2
            exit 0
        fi
    
    ########## HARD ##########

    elif [ "$difficulty" = "3" ]; then
        echo "" >&2
        echo "==== Map Selection ====" >&2
        echo "" >&2
        echo "1 - 01_maze_nightmare.txt" >&2
        echo "2 - 02_capacity_hell.txt" >&2
        echo "3 - 03_ultimate_challenge.txt" >&2
        echo "" >&2
        read -p "Select Map [1-3]: " map

        # map 1
        if [ "$map" = "1" ]; then 
            FILE="maps/hard/01_maze_nightmare.txt"; \
        
        # map 2
        elif [ "$map" = "2" ]; then 
            FILE="maps/hard/02_capacity_hell.txt"; \
        
        # map 3
        elif [ "$map" = "3" ]; then 
            FILE="maps/hard/03_ultimate_challenge.txt";

        else
            echo "Error: Invalid Map" >&2
            exit 0
        fi
    
    ########## CHALLENGER ##########

    elif [ "$difficulty" = "4" ]; then
        echo "" >&2
        echo "==== Map Selection ====" >&2
        echo "" >&2
        echo "Selecting '01_the_impossible_dream.txt'..." >&2
        FILE="maps/challenger/01_the_impossible_dream.txt"; \

    else
        echo "Error: Invalid difficulty" >&2
        exit 0
    fi

echo "$FILE"
exit 0