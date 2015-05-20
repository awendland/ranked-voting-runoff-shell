# -*- coding: utf-8 -*-
import cmd, os
import glob
from datetime import datetime
import pprint, random

class C:
    BG_WHITE = '\033[47m'
    BG_YELLOW = '\033[43m'
    PURPLE = '\033[35m'
    RED = '\033[31m'
    BLACK = '\033[30m'
    BLINK = '\033[5m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class RankedVotingShell(cmd.Cmd):
    """Simple ranked-voting instant-runoff assistance utility."""

    intro = "="*55 + "\nSimple ranked-voting instant-runoff assistance utility.\n" + "="*55
    prompt = '(--) '

    # Class variables
    vote_data = []
    votes = {}
    
    def do_greet(self, person):
        """greet [?person]\nGreet the named person"""
        if person:
            print("hi," + person)
        else:
            print('hi')

    def do_shell(self, line):
        """Run a shell command"""
        print("running shell command:" + line)
        output = os.popen(line).read()
        print(output)
        self.last_output = output

    def do_load(self, file):
        """load filename.csv\nLoad a csv file containing voting results in the format\n\tTime, Voter Name, First Choice, Second Choice, ..."""
    	try:
    	    f = open(file, "r")
    	    try:
    	        self.vote_data = f.read().split("\n")
                self.votes = {}
                for line in self.vote_data:
                    if "Your Name" not in line:
                        data = line.split(',')
                        time = datetime.strptime(data[0], '%m/%d/%Y %H:%M:%S')
                        name = data[1]
                        choices = data[3:]
                        # Make sure than only the most recent vote is counted
                        if name in self.votes and self.votes[name]["time"] > time:
                            pass
                        else:
                            self.votes[name] = {
                                "time": time,
                                "votes": choices,
                                "name": name
                            }
    	        print("Loaded " + str(len(self.votes)) + " unique votes out of " + str(len(self.vote_data)) + " lines from " + file)
    	    finally:
    	        f.close()
    	except IOError as e:
    	    print(e)

    def complete_load(self, text, line, begidx, endidx):
        return [text+"test", text+"test1"]

    def do_preview(self, last_line):
        """preview [?last_line=3]\nQuick printout of the second through LAST_LINE lines,\n\tdefaults to the 4th"""
        if last_line:
            last_line = int(last_line.strip())
        else:
            last_line = 4;
    	for i in range(1,last_line):
            print(self.vote_data[i])

    def run_scenario(self, ignore, print_random):
        # Setup list of candidates to ignore votes for
        if ignore:
            ignore = ignore.split("\\")
        else:
            ignore = []

        candidates = {}
        # Iterate over each voter's vote
        for name, voter in self.votes.iteritems():
            # Iterate over the voters candidate choices, which are 
            # sorted in order of their preference
            for vote in voter["votes"]:
                # Bypass candidates that are on the ignored list
                if vote not in ignore:
                    candidate = vote
                    # Add candidate to candidates list if not added already
                    if candidate not in candidates:
                        candidates[candidate] = 0
                    # Add a vote to this candidate
                    candidates[candidate] += 1
                    # If a random sample was requested, print this vote w/ P = 5 / n
                    if print_random and random.random() < (5.0 / len(self.votes)):
                        print(name + " --> " + candidate)
                    # This vote counted, so break loop
                    break

        max_name = 0
        max_count = 0
        for name, count in candidates.iteritems():
            if len(name) > max_name:
                max_name = len(name)
            if count > max_count:
                max_count = count
        
        print("-"*(max_name+10))
        
        # Print out results
        winner = []
        loser = []
        for candidate, count in candidates.iteritems():
            # Print the results
            print(
                candidate + ":" + " " * (max_name + 2 - len(candidate))
                + str(count) + " " * (len(str(max_count)) + 1 - len(str(count)))
                + ("█" * int(15.0 * count / max_count))
                )
            # Check if this candidate is a winner
            if not winner or winner[0][1] == count:
                winner.append((candidate, count))
            elif winner[0][1] < count:
                winner = [(candidate, count)]
            # Check if this candidate is a loser / last place
            if not loser or loser[0][1] == count:
                loser.append((candidate, count))
            elif loser[0][1] > count:
                loser = [(candidate, count)]
        print("-"*(max_name+10))
        # Print winner and losers
        print("Winner(s): " + ", ".join([w[0] for w in winner]))
        print("Loser(s): " + ", ".join([l[0] for l in loser]))

    def do_count(self, ignore):
        """count [?ignore]\nCount the votes for each candidate by first priority,\n\texcluding candidates specified with IGNORE\n\tIGNORE should be formatted 'Candidate A\\CandidateB'"""
        self.run_scenario(ignore, False)

    def do_counttest(self, ignore):
        """count [?ignore]\nSame as count, but with random votes printed out in\n\torder for spot checking algorithm accuracy"""
        self.run_scenario(ignore, True)

    def do_exit(self, line):
    	return True
    
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    RankedVotingShell().cmdloop()