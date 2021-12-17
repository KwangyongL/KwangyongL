1. containing any special instructions for running your code (e.g., how to supply API keys) as well as a brief description of how to interact with your program.

 A) I used two web APIs, “Yelp Fusion” and “Openweather”, and their API keys are written in my code. When executing my code, users need to answer two questions; (1) "which city do you want to eat? or 'exit' to quit: ", (2) "what kind of food you want to eat? or 'exit' to quit: ". After answering the questions, a bar graph, scatter plot, and a web page by Flask will automatically be displayed with the information about restaurants and weather where they are located.

2. Describing your Data Structure

(Binary tree)

I built a binary tree to show the rating of restaurants that user searched. First, I stored the rating information in ‘nodes’ list.

Second, I used ‘build’ method in binarytree package to bulid the binary tree.

(Cashing)

I used cache by creating the function ‘make_request_with_cache’. When user searches parameters, the function checks if there is a saved result in the stored data. If the result is found, it returns the result. Otherwise, it sends a new request, saves, and returns the data.
