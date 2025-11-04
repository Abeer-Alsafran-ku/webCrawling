from best_first.cp_h_sample import greedy_best_first_search,visualize_graph
import pickle
from best_first.h import analyze_graph
import time
import networkx as nx
import matplotlib.pyplot as plt


# ----------------------------------------------

def main():

    user_input = input("~~~~\nTo run the greedy best-first search, type '1'\nTo run A* search, type '2'\nTo exit, type 'exit'\n~~~~-> ")

    while user_input != "exit":
        if user_input == "exit":
            break
        if user_input == "1":
            src = input("Enter the start node: ")
            if src[:7] != "https://" and len(src) < 10:
                print("Please enter a valid URL starting with http or https:// or enter a full URL.")
                continue
            dest = input("Enter the goal node (can be a description): ")
            with open("best_first/crawled_graph2.gpickle", "rb") as f: # Depth = 2  
                graph = pickle.load(f)
            heuristic = analyze_graph(graph, dest)
            pos = nx.spring_layout(graph)
            stime = time.time()
            result_path = greedy_best_first_search(graph, src, dest, heuristic)
            etime = time.time()
            print(f"Greedy Best-First Search took {etime - stime:.4f} seconds.")
            # Print the result
            print(f"Path from {src} to {dest}: {result_path}")
            # print(f"Path from {start_node} to {goal_node}: {result_path} and the score is {heuristic[goal_node]}")
            # from array to graph
            if result_path:
                nx_path = nx.path_graph(result_path)
                print("Resulting path as graph edges:", nx_path.edges())
                # Visualize the graph and the resulting path
                visualize_graph(nx_path, result_path, pos)
        elif user_input == "2":
            print("You have chosen A* search.")
        else:
            print("Invalid input. Please try again.")

        user_input = input("~~~~\nTo run the greedy best-first search, type '1'\nTo run A* search, type '2'\nTo exit, type 'exit'\n~~~~-> ")
# ----------------------------------------------


if __name__ == "__main__":
    main()