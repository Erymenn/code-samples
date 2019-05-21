#Code interview for Boxever

##Conditions of success and optimisation margin

The conditions of success are:
- all the passenger wanting a seat near a window, have a seat near a window. (nothing specified=satisfied)
- all the member of a group are on a same row.

It should be noted that a lone passenger not especially asking for a window will always be fully satisfied.

Cases were the conditions can't be reached
1. more people asking for windows than number of windows (2 per row)
2. more that 2 people asking for a window in a group
3. group bigger than a row
4. no optimized configuration

Case 1 can't be solved and case 4 will depend a lot of the placement algorithm. However we can discuss cases 2 and 3.

For case 3, let's consider a group of 4 people in a plane of 12 rows and 3 seats per row. 
With the current conditions, the group tickets *0A 3C 7B 11A* and *5A 5B 6A 6B* would generate the same 0% satisfaction.
However it seams reasonable to assume the group would be better satisfied by the 2nd configuration than by the 1rst, albeit not reaching a 100% satisfaction.

We hence attribute partial satisfaction for a group if:
- no one in the group is alone in their row
- the group covers adjacent rows
- if the group is spread on adjacent rows, they have the same seats numbers

Case 2 will then be optimised by choosing to favor the window satisfaction or group satisfaction depending on the size of the group and the partial satisfaction values.

##Algorithms

###I Place a group in a row
We suppose the group is small enough to fit the seats remaining in a row.
- if the group contains people wanting windows and windows are still available, place them near the window
- place the rest of the group by increasing number of the seat

###II Indivisible groups naive algorithm (not implemended)
- convert the input in a list of groups
- for each row, check if there is enough place for the group to be placed
- if yes, apply algo I, if no, check next row
- some groups may be left

###III Indivisible groups complementarity algorithm (not implemended)
- convert the input in a list of groups
- for each row, check if the row is empty or if there is there is exactly enough place for the group to be placed
- if yes, apply algo I, if no, check next row
- if the group is still not placed, check all the rows again applying algo II
- some groups may be left

###IV Complementary algorithm
- convert the input in a list of groups
- split all the groups to big to fit a row into two subgroups, with the windows demands equally split in the two half groups.
- apply algo III
- if the group/subgroup is still not placed, split it again and apply algo III
- everyone is placed

###V Window first complementary algorithm
- convert the input in a list of groups
- split all the groups to big to fit a row into two subgroups, with the windows demands equally split in the two half groups.
- split all the groups containing more than 2 window demands
- sort the groups by number of windows asked (primary sort key) and size (secondary sort key)
- apply algo IV
- everyone is placed

###VI Group first complementary algorithm
- convert the input in a list of groups
- sort the groups by size (primary sort key) and number of windows asked (secondary sort key)
- split all the groups to big to fit a row into two subgroups, with the windows demands equally split in the two half groups (splitting at this stage increase the chance subgroups are in adjacent rows)
- apply algo IV
- everyone is placed

###VII further algorithms...
Other algorithm splitting groups that ask for more than 2 windows and/or presenting different order of splitting/sorting could be implemented, favoring more or less window and group placements, or other additional optimisation parameters not defined here (corridor preference for example). But we will stop here.

##Use the code
Require python 3.6

Check if automated tests run ok, including example one:

```
python code.py
```

Run an optimisation:

```
python optimise.py <input> --output <filepath> --algo <simple/window_first/group_first> --window_group_satis_ratio 1 --satis_not_alone 0.4 --satis_near_rows 0.2 --satis_near_seats 0.2
```
The input can be a string as described in the requirements or the path of a file containing said string. The code will run the optimisation and print the result.

If output is specified, the result will be copied in a file.

The algorithm used for optimisation can be choosen. By default it will be the simple complementary one.

The value for the ratio of window/group satisfaction can be changed. 
At 1, window and group demands have the same weight.
At 2, window demand weight twice as much as the group demand for a passenger satisfaction.
At 0.5, group demand weight twice as much as the window demand for a passenger satisfaction.

The values for groups partial satisfaction can be changed. it should be so `satis_not_alone + satis_near_rows + satis_near_seats <= 1` or an error will be raised.



