This is the readme file for the code package for the paper: 
"Inclusive Multimodal Routing: Who Gets Left Behind?" 
by Ioanna Gogousou (ioanna.gogousou@geo.tuwien.ac.at), Manuela Canestrini, Negar Alinaghi and Ioannis Giannopoulos

================================================================================================================
Environment Setup:
The file environment.yml specifies the required libraries and dependencies for this project.
The code was developed and tested using Python 3.13.5, as specified in the environment.yml file.
To create the environment, run:
	conda env create -f environment.yml
	conda activate <environment_name>

Repository Structure:
The zip folder is structured as follows: 
.
├── data/
│   └── Contains the datasets used, including the preprocessed graph structure of the city of Vienna and the raw origin–destination(OD) pairs required for the routing process (The transportation network graph is stored as a serialized Python object (pickle file)).
├── code/
│   └── Python scripts required to perform the analysis.
├── results/
│   └── Routing results used in the analysis and discussed in the associated paper.
├── plots/
│   └── Visualizations and figures presented in the paper.
└── environment.yml


All scripts are written in Python.
The results and plots directories reproduce the outputs presented in the paper. The study focuses on the transportation network of the city of Vienna, with emphasis on cycling, walking, and public transport modes. A routing process is performed under multiple scenarios by applying different restrictions (filters) within the routing algorithm to model varying user preferences. The goal of the analysis is to investigate how routing outcomes change in terms of average travel time, distance, OD pair feasibility, and modal share as these constraints are tightened.

**************** To ensure the scripts run correctly, the folder structure must remain unchanged.
		 Modifying directory names or moving files may cause the scripts to fail. *********************

Step 1: Routing Computation

	Run the following scripts:
	* routing_filters_nofilters.py
	* routing_filter_variations.py

	These scripts generate the routing results used for the analysis.
	Note: The routing process is computationally intensive and may take time until further optimization is implemented.
	(We also provide the results)

	After successful execution, the following directory structure will be created:

	results/
	└── vienna/
	    ├── filters/MultiGraph_walk_bike_PT/
	    ├── nofilters/MultiGraph_walk_bike_PT/
	    └── transitions/MultiGraph_walk_bike_PT/


Step 2: Route Number Grouping

	After the routing results are generated, run:
	*route_nr_group.py

	This script creates the unique_route_nr folder, which is required for subsequent analyses and visualizations.


Figures and Tables Reproduction

Figure 1 and Tables 3 & 4 (Partial)

	Run: 
 	* no_filters.py

	This script produces: Figure 1, Table 3 & 4 (column 2 values)


Figures 2 & 3 and Table 3 & 4 (Remaining Columns)

	Run:
 	* filter_variations.py

	This script produces: Figure 2, Figure 3, Table 3 & 4 (column 3, 4, 5, 6, 7, and 8 values)

