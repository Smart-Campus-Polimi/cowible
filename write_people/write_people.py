#!/usr/bin/env python


path = "/home/pi/cowible/data/people.txt"

def main():
	while True:
		people = raw_input("How many people? ")
		with open(path, "w") as f: 
			f.write(people)

if __name__ == "__main__":
	main()

