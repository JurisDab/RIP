import time
from collections import deque

class Router:
    def __init__(self, name):
        self.name = name
        self.routing_table = {}
        self.has_changed = False

    #function to add a route
    def add_route(self, dest, next_hop, hops):
        if dest != self.name: 
            self.routing_table[dest] = {'next_hop': next_hop, 'hops': hops}

    #function to delete a route
    def delete_route(self, destination):
        if destination in self.routing_table:
            del self.routing_table[destination]
            self.has_changed = True

    #function to get a routers routing table
    def get_routing_table(self):
        return self.routing_table

    #function to display routing table
    def display_routing_table(self, exclude_router=None):
        print(f"Routing table for {self.name}:")
        print("Destination\tNext Hop\tHops")
        for destination, info in self.routing_table.items():
            if destination == exclude_router:
                continue
            print(f"{destination}\t\t{info['next_hop']}\t\t{info['hops']}")


#creation of preexisting routers and connections
def create_routers():
    routers = {
        'A': Router('A'),
        'B': Router('B'),
        'C': Router('C'),
        'D': Router('D'),
        'E': Router('E')
    }
    return routers

connections = {
    'A': [('B', 1), ('C', 1)],
    'B': [('A', 1), ('D', 1)],
    'C': [('A', 1), ('E', 1)],
    'D': [('B', 1), ('E', 1)],
    'E': [('C', 1), ('D', 1)]

}

#function to connect the routers based on the hardcoded connections
def connect_routers(routers):
    for router, neighbors in connections.items():
        if router not in routers:
            continue
        for neighbor, hops in neighbors:
            if neighbor in routers and neighbor != router:  
                routers[router].add_route(neighbor, neighbor, hops)
    return routers

#function to display all routing tables
def display_all_routing_tables(routers):
    
    #displays the intial tables
    for router in routers.values():
        router.display_routing_table()
        print()
    time.sleep(5)

    #Performs initial updates
    send_updates(routers, connections)
    
    #loop is set to a fixed ammount of times to keep updating the routers
    for _ in range(5):
        routing_tables_changed = send_updates(routers, connections)
        
        if routing_tables_changed:
            for router in routers.values():
                router.display_routing_table()
                print()
            time.sleep(5)


#funcional responsible for handling router updates
def send_updates(routers, connections, update_enabled=True, router_name=None):
    routing_tables_changed = False
    updates_to_propagate = {router: {} for router in routers}

    #a Breadth-First Search queue is initialised to manage router processing 
    bfs_queue = deque([router_name]) if router_name else deque(routers.keys())
    visited = set()

    #Main while loop to traverse the routers, getting updates
    while bfs_queue:
        current_router_name = bfs_queue.popleft()
        if current_router_name not in routers:
            continue
        current_router = routers[current_router_name]

        #Process current router if not visited before
        if current_router_name not in visited:
            visited.add(current_router_name)

            #Gather updates for the current router
            received_routing_table = {}
            for neighbor, _ in connections.get(current_router_name, []):
                if neighbor in routers:
                    for dest, info in routers[neighbor].get_routing_table().items():
                        if dest != current_router_name:
                            if dest not in current_router.routing_table:
                                received_routing_table[dest] = {'next_hop': neighbor, 'hops': info['hops'] + 1}
                            else:
                                current_hops = current_router.routing_table[dest]['hops']
                                if info['hops'] + 1 < current_hops:
                                    received_routing_table[dest] = {'next_hop': neighbor, 'hops': info['hops'] + 1}

            updates_to_propagate[current_router_name] = received_routing_table

            for neighbor, _ in connections.get(current_router_name, []):
                if neighbor not in visited:
                    bfs_queue.append(neighbor)
                    
    #Applies the updates to routers
    for router_name, updates in updates_to_propagate.items():
        for dest, info in updates.items():
            if dest not in routers[router_name].routing_table or routers[router_name].routing_table[dest] != info:
                routers[router_name].add_route(dest, info['next_hop'], info['hops'])
                routing_tables_changed = True
    
    #Prints the tables
    if routing_tables_changed:
        for router in routers.values():
            router.display_routing_table()
            print()
    

    return routing_tables_changed

#Function to find route to a destination router based on the routing table of other routers
def find_route(routers, start_router, destination_router):
    route = [start_router]
    current_router = start_router
    while current_router != destination_router:
        if destination_router not in routers[current_router].get_routing_table():
            return []
        next_hop = routers[current_router].get_routing_table()[destination_router]['next_hop']
        if next_hop == current_router:
            return []
        route.append(next_hop)
        current_router = next_hop
    return route

#Function to Add a router to the topology
def add_router(routers):
    name = input("Enter the name of the router: ").upper()
    if name in routers:
        print("Router with that name already exists.")
        return routers

    #Gather the immediate neighbors of the new router
    neighbors_count = int(input("Enter the number of neighbors for the router: "))
    neighbors = []
    for i in range(neighbors_count):
        neighbor = input(f"Enter the name of neighbor {i+1}: ").upper()
        if neighbor not in routers:
            print(f"Router {neighbor} doesn't exist. Please add it first.")
            return routers
        neighbors.append(neighbor)

    #Add the new router to the routers dictionary with empty routing table
    routers[name] = Router(name)
    connections[name] = []
    
    #Print the initial routers
    for router in routers.values():
                router.display_routing_table()
                print()
                
    time.sleep(5)

    #Update the routing tables for the new router and its neighbors
    for neighbor in neighbors:
        routers[name].add_route(neighbor, neighbor, 1)
        routers[neighbor].add_route(name, name, 1)
        if name not in [n[0] for n in connections[neighbor]]:
            connections[neighbor].append((name, 1))
        if neighbor not in [n[0] for n in connections[name]]:
            connections[name].append((neighbor, 1))

    #Perform Breadth-First Search to update all routing tables
    update_routes_for_router(routers, name, len(routers))
    
    return routers


#function to remove a router from the topology, simulating a shutdown
def delete_router(routers):
    name = input("Enter the name of the router to delete: ").upper()
    if name not in routers:
        print("Router with that name does not exist.")
        return routers

    immediate_neighbors = [neighbor for neighbor, _ in connections.get(name, [])]

    connections.pop(name, None)
    
    #starts the route poisoning process
    update_routes_after_deletion(routers, immediate_neighbors, name)
    
    #the router is flushed
    del routers[name]

    return routers

#function to update routes after the deletion, used in the delete router function
def update_routes_after_deletion(routers, initial_routers, deleted_router_name):
    #initial neighbor routes to deleted router are poisoned and changed 
    neighbors_to_update = []
    for neighbor_name in initial_routers:
        neighbor_router = routers.get(neighbor_name)
        if neighbor_router and deleted_router_name in neighbor_router.routing_table:
            neighbor_router.routing_table[deleted_router_name] = {'next_hop': None, 'hops': float('inf')}
            neighbors_to_update.append(neighbor_name)
            calculate_routes_for_single_router(neighbor_router, routers, deleted_router_name)
            
            
    for neighbor_name in neighbors_to_update:
        neighbor_router = routers.get(neighbor_name)
        if neighbor_router:
            neighbor_router.routing_table[deleted_router_name] = {'next_hop': None, 'hops': float('inf')}
    
    #prints the result
    for router in routers.values():
            router.display_routing_table()
            print()
    time.sleep(5)
    
    visited = set()
    bfs_queue = deque(initial_routers)
#a Breadth-First Search queue is used 
    while bfs_queue:
        current_level_routers = list(bfs_queue)
        bfs_queue.clear()

        for current_router_name in current_level_routers:
            if current_router_name not in routers:
                continue
            current_router = routers[current_router_name]
            visited.add(current_router_name)
            #neighbors are iterated through to get and check their routing tables
            for neighbor, _ in connections.get(current_router_name, []):
                if neighbor not in visited and neighbor_router:
                    neighbor_router = routers[neighbor]
                    updated = False

                    for dest, info in current_router.get_routing_table().items():
                        if dest != deleted_router_name and (dest not in neighbor_router.routing_table or neighbor_router.routing_table[dest]['hops'] > info['hops'] + 1):
                            neighbor_router.add_route(dest, current_router_name, info['hops'] + 1)
                            updated = True

                    if deleted_router_name in neighbor_router.routing_table and neighbor_router.routing_table[deleted_router_name]['hops'] != float('inf'):
                        neighbor_router.routing_table[deleted_router_name] = {'next_hop': None, 'hops': float('inf')}
                        updated = True


                    if updated:
                        bfs_queue.append(neighbor)
        for router_up_name in neighbors_to_update:
            updated_router = routers.get(router_up_name)
            if updated_router:
                updated_router.routing_table[deleted_router_name] = {'next_hop': None, 'hops': float('inf')}
        
        for router in routers.values():
            router.display_routing_table()
            print()
        time.sleep(5)

        #final recalculation to avoid poisoned routes
        for router in routers.values():
            if router.name != deleted_router_name:
                calculate_routes_for_single_router(router, routers, deleted_router_name)
                neighbors_to_update.append(current_router_name)
                
        for router_up_name in neighbors_to_update:
            updated_router = routers.get(router_up_name)
            if updated_router:
                updated_router.routing_table[deleted_router_name] = {'next_hop': None, 'hops': float('inf')}
                

#function to calculate routes for a single router     
def calculate_routes_for_single_router(router, all_routers, deleted_router_name):

    for destination in list(router.routing_table.keys()):
        if router.routing_table[destination]['hops'] != float('inf') and destination != deleted_router_name:

            del router.routing_table[destination]

    #reconects the routers based on which router was shut down
    routers2 = connect_routers(all_routers)
    

    updated_routing_table = {}
    distance = {r: float('inf') for r in routers2}
    distance[router.name] = 0
    predecessor = {r: None for r in routers2}


    #finds the shortest route
    for _ in range(len(routers2) - 1):
        for r in routers2:
            if r == deleted_router_name:  
                continue
            for neighbor, data in routers2[r].get_routing_table().items():
                if neighbor == deleted_router_name:  
                    continue
                if distance[r] != float('inf') and data['hops'] != float('inf') and distance[r] + data['hops'] < distance[neighbor]:
                    distance[neighbor] = distance[r] + data['hops']
                    predecessor[neighbor] = r
                    

    #determines the next hop
    for destination in routers2:
        if destination != router.name:
            next_hop = destination
            while predecessor[next_hop] != router.name and predecessor[next_hop] is not None:
                if next_hop == deleted_router_name: 
                    break
                next_hop = predecessor[next_hop]
            if next_hop != deleted_router_name: 
                if distance[destination] < float('inf'):
                    updated_routing_table[destination] = {'next_hop': next_hop, 'hops': distance[destination]}
                    
                else:
                    updated_routing_table[destination] = {'next_hop': None, 'hops': float('inf')}
    #verification that all destinations have an entry  
    for dest in routers2:
        if dest != router.name:
            if dest in router.routing_table and router.routing_table[dest]['hops'] == float('inf'):
                updated_routing_table[dest] = router.routing_table[dest]
                
            elif dest not in updated_routing_table:
                updated_routing_table[dest] = {'next_hop': None, 'hops': float('inf')}
              
    router.routing_table = updated_routing_table
        
    return router

#function to update routes after the addition, used in the add router function
def update_routes_for_router(routers, router_name, number_of_routers):
    if router_name not in routers:
        return

    visited = set()
    bfs_queue = deque([router_name])

    #update current router with routes from neighbors
    current_router = routers[router_name]
    for neighbor, _ in connections.get(router_name, []):
        neighbor_router = routers.get(neighbor)
        if neighbor_router:
            for dest, info in neighbor_router.get_routing_table().items():
                if dest != router_name and (dest not in current_router.routing_table or current_router.routing_table[dest]['hops'] > info['hops'] + 1):
                    current_router.add_route(dest, neighbor, info['hops'] + 1)
    #use Breadth-First Search to update routers and checks whether all routes are updated
    all_destinations_updated = all(len(router.routing_table) >= number_of_routers - 1 for router in routers.values())
    if not all_destinations_updated:
        while bfs_queue:
            level_size = len(bfs_queue)
            for _ in range(level_size):
                #pops the router and marks as visited
                current_router_name = bfs_queue.popleft()
                current_router = routers[current_router_name]
                visited.add(current_router_name)

                #process neighbors
                for neighbor, _ in connections.get(current_router_name, []):
                    if neighbor not in visited and neighbor in routers:
                        for dest, info in current_router.get_routing_table().items():
                            if dest != neighbor and (dest not in routers[neighbor].routing_table or routers[neighbor].routing_table[dest]['hops'] > info['hops'] + 1):
                                routers[neighbor].add_route(dest, current_router_name, info['hops'] + 1)
                        bfs_queue.append(neighbor)
                        visited.add(neighbor)

            #display routing tables after updating each level
            for router in routers.values():
                router.display_routing_table()
                print()
            
            time.sleep(5)

#main loop
def main():
    routers = create_routers()
    routers = connect_routers(routers)
    display_all_routing_tables(routers)

    while True:
        print("\nChoose an action:")
        print("1. Display routing tables")
        print("2. Find route between routers")
        print("3. Add a router")
        print("4. Delete a router")
        print("5. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            display_all_routing_tables(routers)
        elif choice == '2':
            start_router = input("Enter starting router: ").upper()
            destination_router = input("Enter destination router: ").upper()
            if start_router in routers and destination_router in routers:
                route = find_route(routers, start_router, destination_router)
                if route:
                    print(f"Route from {start_router} to {destination_router}: {' -> '.join(route)}")
                else:
                    print(f"No route found from {start_router} to {destination_router}.")
            else:
                print("Invalid router name.")
        elif choice == '3':
            routers = add_router(routers)
        elif choice == '4':
            routers = delete_router(routers)
        elif choice == '5':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()


