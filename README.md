# graph-search

building a routing engine from scratch. real road data from openstreetmap gets loaded into a directed weighted graph — intersections are nodes, roads are edges with distance and speed limits. dijkstra finds shortest paths by distance or travel time. the plan is to add grid-based graph partitioning so queries only search relevant cells instead of the entire network, then layer on eta using edge speeds. fastapi backend serves routes, next.js frontend will visualize them on a map.
