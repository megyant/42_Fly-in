	#!/bin/bash

# Keep looping until a valid map file is selected or the user quits
while true; do
    echo "" >&2
    echo "==== Difficulty Selection ====" >&2
    echo "" >&2
    echo "1 - Easy" >&2
    echo "2 - Medium" >&2
    echo "3 - Hard" >&2
    echo "4 - Challenger" >&2
    echo "5 - Test" >&2
    echo "q - Quit" >&2
    echo "" >&2
    read -p "Select difficulty [1-5 or q]: " difficulty


    if [ "$difficulty" = "q" ] || [ "$difficulty" = "Q" ]; then
        echo "Exiting game..." >&2
        exit 1
    fi

    ########## EASY ##########
    if [ "$difficulty" = "1" ]; then
        while true; do
            echo "" >&2
            echo "==== Map Selection (Easy) ====" >&2
            echo "" >&2
            echo "1 - 01_linear_path.txt" >&2
            echo "2 - 02_simple_fork.txt" >&2
            echo "3 - 03_basic_capacity.txt" >&2
            echo "h - Home" >&2
            echo "" >&2
            read -p "Select Map [1-3 or b]: " map

            if [ "$map" = "1" ]; then 
                FILE="maps/easy/01_linear_path.txt"
                break 2 
            elif [ "$map" = "2" ]; then 
                FILE="maps/easy/02_simple_fork.txt"
                break 2
            elif [ "$map" = "3" ]; then 
                FILE="maps/easy/03_basic_capacity.txt"
                break 2
            elif [ "$map" = "h" ] || [ "$map" = "H" ]; then
                break
            else
                echo "Error: Invalid Map Choice" >&2
            fi
        done

    ########## MEDIUM ##########
    elif [ "$difficulty" = "2" ]; then
        while true; do
            echo "" >&2
            echo "==== Map Selection (Medium) ====" >&2
            echo "" >&2
            echo "1 - 01_dead_end_trap.txt" >&2
            echo "2 - 02_circular_loop.txt" >&2
            echo "3 - 03_priority_puzzle.txt" >&2
            echo "h - Home" >&2
            echo "" >&2
            read -p "Select Map [1-3 or b]: " map

            if [ "$map" = "1" ]; then 
                FILE="maps/medium/01_dead_end_trap.txt"
                break 2
            elif [ "$map" = "2" ]; then 
                FILE="maps/medium/02_circular_loop.txt"
                break 2
            elif [ "$map" = "3" ]; then 
                FILE="maps/medium/03_priority_puzzle.txt"
                break 2
            elif [ "$map" = "h" ] || [ "$map" = "H" ]; then
                break
            else
                echo "Error: Invalid Map Choice" >&2
            fi
        done

    ########## HARD ##########
    elif [ "$difficulty" = "3" ]; then
        while true; do
            echo "" >&2
            echo "==== Map Selection (Hard) ====" >&2
            echo "" >&2
            echo "1 - 01_maze_nightmare.txt" >&2
            echo "2 - 02_capacity_hell.txt" >&2
            echo "3 - 03_ultimate_challenge.txt" >&2
            echo "h - Home" >&2
            echo "" >&2
            read -p "Select Map [1-3 or h]: " map

            if [ "$map" = "1" ]; then 
                FILE="maps/hard/01_maze_nightmare.txt"
                break 2
            elif [ "$map" = "2" ]; then 
                FILE="maps/hard/02_capacity_hell.txt"
                break 2
            elif [ "$map" = "3" ]; then 
                FILE="maps/hard/03_ultimate_challenge.txt"
                break 2
            elif [ "$map" = "h" ] || [ "$map" = "H" ]; then
                break
            else
                echo "Error: Invalid Map Choice" >&2
            fi
        done

    ########## CHALLENGER ##########
    elif [ "$difficulty" = "4" ]; then
        echo "" >&2
        echo "Selecting '01_the_impossible_dream.txt'..." >&2
        FILE="maps/challenger/01_the_impossible_dream.txt"
        break

    ########## TEST ##########
    elif [ "$difficulty" = "5" ]; then
        echo "" >&2
        echo "Selecting 'test.txt'..." >&2
        FILE="maps/test.txt"
        break

    else
        echo "Error: Invalid difficulty" >&2
        exit 1
    fi
done

echo "$FILE"
exit 1