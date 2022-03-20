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
        person.id = args[0]
        person.marker = args[1]
        person.name = args[2]
        person.surname = args[3]
        person.birth = args[4]
        person.christened = args[5]
        person.death = args[6]
        person.parents = args[7].split(",")
        person.spouse = args[8].split(",")
        person.description = args[9]
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
    def generate():
        pass

if __name__ == "__main__":

    family = Family()

    family.populate("output.csv")
    family.generate()