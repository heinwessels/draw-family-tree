import argparse
import csv
import copy

class Person:
    '''
    This will contain a individual person with his/her information
    and links to the households person belongs to.
    Person doesn't know if person is male or female.
    '''
    def __init__(self):
        self.households = []

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
        person.parents = args[7].split(",") if args[7] != "" else None
        person.spouses = args[8].split(",") if args[8] != "" else None
        person.description = args[9] if args[9] != "" else None
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

class Family:
    '''
    Contains all people and all households
    '''
    people = {}    # Dictionary of all people in the tree
    
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
        print(f"Imported {len(self.people)} people from:", path)

    """
    Process the list of people to generate all the
    valid connections.
    """
    def generate(self):
        
        for _, person in self.people.items():

            # First turn the temporary ID's used for 
            # parents and spouses into person links
            for index in range(len(person.spouses) if person.spouses else 0):
                person.spouses[index] = self.people[person.spouses[index]]
            for index in range(len(person.parents) if person.parents else 0):
                person.parents[index] = self.people[person.parents[index]]

            # We will create new households by looking at 
            # every new person's parents.
            if person.parents is not None:
                
                # This person needs to be part of an household
                # Find the first parent, and join said household.
                # Create if neccesary.
                main_parent = person.parents[0]
                for household in main_parent.households:
                    # How do I know if this household belongs
                    # to this person?
                    pass
                    


if __name__ == "__main__":

    family = Family()

    family.populate("output.csv")
    family.generate()