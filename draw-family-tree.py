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
    
    def __init__(self):
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
                    self.households[person.households_as_parent[index]] = Household()
                person.households_as_parent[index] = self.households[person.households_as_parent[index]]
                person.households_as_parent[index].add_parent(person)
            if person.household_as_child:
                if not person.household_as_child in self.households:
                    self.households[person.household_as_child] = Household()
                person.household_as_child = self.households[person.household_as_child]
                person.household_as_child.add_child(person)
            
    def draw(self, root_id):

        # Find the root
        if not root_id in self.people:
            raise RuntimeError(f"Root ID '{root_id}' does not exist")
        root = self.people[root_id]

        # So far draw only the first household
        self.draw_households_recusive(root.households_as_parent[0])

    def draw_households_recusive(self, household, iteration=0):

        # Draw all the parents for this household
        print((iteration*" ") + " | ".join([parent.name for parent in household.parents]))

        for child in household.children:
            if child.households_as_parent:
                self.draw_households_recusive(child.households_as_parent[0], iteration + 1)
            else:
                print(((iteration+1)*" ") + child.name)
        
            




        

if __name__ == "__main__":

    family = Family()

    family.populate("output.csv")
    family.generate()

    family.draw(root_id="a1b2c2d4e5f5g9")
