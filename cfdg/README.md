# How to execute the CFDG

## 1 - Compile de image generator

0.1 - You are going to have to install the libpng library:

macOS

    `brew install libpng`

Ubuntu

    `sudo apt-get install libpng`

1.1 - Go to the folder `ContextFreeAlterado`

1.2 - Remove the `objs` folder

1.3 - On the terminal, go to the `ContextFreeAlterado` and type `make`

1.4 - Check for possible compilation errors

1.5 - Then go to the folder `cfdg`and execute the following commands to create a symbolic link to the image generator:

    rm cfdg
    ln -s ../ContextFreeAlterado/cfdg

## 2 - Run the Evolutionary Algorithm

2.1 - The `config.cfg`contains most of the important configurations for algorithm to work.
2.2 - There are some configs that should be sent through the terminal as arguments. An example of the command to execute is as follows:

    python motor.py --best_number 10 --nthreads 1 --target-class stingray

The best number corresponds to the number of best individuals that will be saved in the end of the experiment. note that we have access to all individuals during all generations. The --target-class corresponds to the class that we are evolving too. Check the motor.py file to see the remaining commands.