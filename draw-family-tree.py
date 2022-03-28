import argparse
import csv
import copy

class Person:
    '''
    This will contain a individual person with his/her information
    and links to the households person belongs to.
    Person doesn't know if person is male or female.
    '''

    @classmethod
    def from_csv_row(cls, args):
        person = cls()
        person.id = args[0] # Required
        person.marker = args[1] if args[1] != "" else None
        person.name = args[2]
        person.surname = args[3] if args[3] != "" else None
        person.birth = args[4] if args[4] != "" else None
        person.christened = args[5] if args[5] != "" else None
        person.death = args[6] if args[6] != "" else None
        person.spouses = args[7].split(",") if args[7] != "" else None
        person.household_as_child = args[8] if args[8] != "" else None
        person.households_as_parent = args[9].split(",") if args[9] != "" else None
        person.description = args[10] if args[10] != "" else None
        return person

class Household:
    '''
    This is a household, i.e parents and their children.
    Parents can belong to more than one household
    Due to a current limitation if there are multiple spouses
    it will handled as-if all spouses and all subsequent children
    are part of a single household.
    '''
    
    def __init__(self, id):
        self.id = id
        self.parents = []
        self.children = []        

    def add_child(self, parent):
        if parent in self.parents:
            raise RuntimeError(f"Child {parent.id} already in household!")
        self.children.append(parent)

    def add_parent(self, parent):
        if parent in self.parents:
            raise RuntimeError(f"Parent {parent.id} already in household!")
        self.parents.append(parent)

class Family:
    '''
    Contains all people and all households
    '''
    people = {}     # Dictionary of all people in the tree
    households = {} # Dictionary of all households
    
    '''
    Popualte the entire family tree with 
    people from a *.csv file. This will not build
    all the connections. That has to be done by
    calling <generate>
    '''
    def populate(self, path):

        # Read all the data into a table
        with open(path, 'r') as table:
            csv_reader = csv.reader(table, delimiter=";")
            for row in csv_reader:
                person = Person.from_csv_row(row)
                self.people[person.id] = copy.deepcopy(person)
        
        # Done populating family with people

    """
    Process the list of people to generate all the
    valid connections.
    """
    def generate(self):
        
        for _, person in self.people.items():

            # First turn the temporary ID's used for 
            # spouses into person links
            for index in range(len(person.spouses) if person.spouses else 0):
                person.spouses[index] = self.people[person.spouses[index]]

            # Now turn households into links, and creating them if
            # they don't exist already. We will do this for both
            # households as parent and households as child
            for index in range(len(person.households_as_parent) \
                    if person.households_as_parent else 0):
                if not person.households_as_parent[index] in self.households:
                    self.households[person.households_as_parent[index]] = Household(person.households_as_parent[index])
                person.households_as_parent[index] = self.households[person.households_as_parent[index]]
                person.households_as_parent[index].add_parent(person)
            if person.household_as_child:
                if not person.household_as_child in self.households:
                    self.households[person.household_as_child] = Household(person.household_as_child)
                person.household_as_child = self.households[person.household_as_child]
                person.household_as_child.add_child(person)

    def parents_of(self, person):
        if person.household_as_child is None:
            return None
        return person.household_as_child.parents # Will retun None if there was none

    def find_linage(self, ancestor, descendent, linage=None):
        """
        Finds a path between an ancestor and a descended. It will
        Return a list a list of People, starting at the ancestor,
        down to the descendend, signifying the direct linage.
        The input is the _PEOPLE_ objects, not IDs.
        
        This is done by simply checking the descendents parents, 
        until the ancestor is found.
        
        This is a recursive function that calls itself. I like those.
        """
        first = False
        if linage is None:
            # Probably first iteration. 
            # Keep track of this so that we can add him at the end
            first = True
            linage = [] # Man, this is hacky

        parents = self.parents_of(descendent)
        if parents is None:
            return None

        for parent in parents:
            if parent == ancestor:
                # Should be the end of recursion!
                # Start building the list on the way back
                return [parent] + linage
            else:
                # This parent is not the ancestor we're looking for.
                # Do the recursion thing by checking again.
                parents_linage = self.find_linage(ancestor, parent, linage)
                if parents_linage is not None:
                    # This parent is in the right direction!
                    if first:
                        return parents_linage + [parent, descendent]
                    return parents_linage + [parent]
                # This parent is not in the linage. Ignore.

        # None of these parents are in the linage. 
        # Linage probably doesn't exist.
        return None

    def draw(self, root_id, depth=100):

        print('digraph {\n' + \
            '\tnode [shape=box,splines=false,ranksep=0.05];\n' + \
            '\tconcentrate=true;\n' + \
            '\tranksep=0.01;\n' + \
            '\tgraph [center=true, margin=0.2, nodesep=0.1, ranksep=0.3;] ;\n' + \
            # '\tsize="10,30";\n' + \
            # '\tratio="compress";\n' + \
            '\tedge [dir=none];\n' + \
            '\tsplines=ortho;\n' + \
            '')

        # Find the root
        if not root_id in self.people:
            raise RuntimeError(f"Root ID '{root_id}' does not exist")
        root = self.people[root_id]

        # So far draw only the first household
        self.draw_households_recusive(root.households_as_parent[0], depth)

        print('}')

    def draw_households_recusive(self, household, depth):
        
        dummy_node_properties = f'fontsize = 0,' \
                        'height = 0.03,' \
                        'label = <&#x200B;>' \
                        'style = invis, ' \
                        'width = 0' # GraphVis Issue#1337 for zero sized unflattened node

        # If this household has no children the recursion ends
        if household.children and depth > 0:
            
            # Create a dummy node for this household 
            print("\tnode [fixedsize = true]")
            print(f'\t"h{household.id}"[{dummy_node_properties}];') 
            print("\tnode [fixedsize = false]")

            # Now point the parents to this household
            for parent in household.parents:
                print(f'\t\t"{parent.id}"[label="{parent.name}"];')
                print(f'\t\t"{parent.id}" -> "h{household.id}";')

            # Now point the household to every child
            # We will do this wacky though: center, left, right, left, right...
            previous_node = {"left":f"h{household.id}", "right":f"h{household.id}"}
            position = "center"
            for i in range(len(household.children)):
                child = household.children[i]   # TODO Modify this to make hierarchical                
                print(f'\t\t"{child.id}"[label="{child.name}"];')
                
                print("\tnode [fixedsize = true]")
                print(f'\t\t"c{child.id}"[{dummy_node_properties}];')
                print("\tnode [fixedsize = false]")
                
                if position == "center":
                    # First child is in the center below parents                    
                    print(f'\t\t"h{household.id}":s -> "c{child.id}":n;')
                    previous_node["left"] = f"c{child.id}"
                    previous_node["right"] = f"c{child.id}"
                    position = "right"
                else: # Position is left or right
                    if position == "left":
                        print(f'\t\t"{previous_node["left"]}":w -> "c{child.id}":e;')
                        previous_node["left"] = f"c{child.id}"
                        position = "right"
                    else:
                        print(f'\t\t"{previous_node["right"]}":e -> "c{child.id}":w;')
                        previous_node["right"] = f"c{child.id}"                        
                        # position = "left" # It works better placing all right?
                print(f'\t\t"c{child.id}":s -> "{child.id}":n;')
                    
            
            # Put all child connection nodes on same rank
            print(f"\t\t{{rank=same;{';'.join('c'+child.id for child in household.children)}}}")

            # Now repeat the process for every child
            for child in household.children:
                if child.households_as_parent:
                    for childs_household in child.households_as_parent:
                        self.draw_households_recusive(childs_household, depth=depth-1)

if __name__ == "__main__":

    family = Family()

    family.populate("output.csv")
    family.generate()

    family.draw(root_id="a1b2c2d4e5f5g9h4i1", depth=100)
    family.draw(root_id="a1b2c2d4e5f5g9h4i1", depth=100)
    family.draw(root_id="a1b2c2d4e5f5")
