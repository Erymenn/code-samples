# Bus seating optimisation problem

## Context
A bus company is looking to improve the satifaction of them passengers. 
For that propose, each passenger are asked if they belong to a group and if they wish a seat near a window.

For each bus journey, this information is delivered under this kind of format :
```
5 2
1 2W 3 4W 
5W 6
10
7W 8 9
```
- The first two numbers are the number of seats per row and the number of rows in the bus
- Each other line represent a group of passengers
- Passenger with a `W` near their number want to be near a window

The conditions of satisfaction are:
- all the passenger wanting a seat near a window, have a seat near a window (nothing specified=satisfied)
- all the member of a group are on a same row.

The bus company want to know the satisfation of the passengers in regard of their seats. 
And if a 100% satifaction can't be reached, they want to maximise the satisfaction, optimisation process to be determined by the coder.

The expected output is something like this:
```
2 1 3 10 4
5 6 8 9 7
100%
```
where each row represent a row in the bus and the last line shows the global satisfaction.

## Some thoughts toward optimisation

It should be noted that a lone passenger not especially asking for a window will always be fully satisfied.

Cases were the maximum satisfaction can't be reached
1. more people asking for windows than number of windows (2 per row)
2. more that 2 people asking for a window in a group
3. group bigger than a row
4. no optimized configuration

Case 1 can't be solved and case 4 will depend a lot of the placement algorithm. However we can discuss cases 2 and 3.

For case 3, let's consider a group of 4 people in a bus of 12 rows (row 0 to 11) and 3 seats per row (seat A to C). 
With the current conditions, the group tickets *0A 3C 7B 11A* and *5A 5B 6A 6B* would generate the same 0% satisfaction.
However it seams reasonable to assume the group would be better satisfied by the 2nd configuration than by the 1rst, albeit not reaching a 100% satisfaction.

We hence attribute partial satisfaction for a group if:
- no one in the group is alone in their row
- the group covers adjacent rows
- if the group is spread on adjacent rows, they have the same seats numbers

Case 2 will then be optimised by choosing to favor the window satisfaction or group satisfaction depending on the size of the group and the partial satisfaction values.

## Algorithms

### I. Satisfaction score
The global satisfaction score is the average satisfaction for all passengers.

For each passenger the satisfaction is calculated as such:
```passenger_score = weight_of_window_satisfaction*window_score + weight_of_group_satisfaction*group_score```
the ration of weight will be adjustable and default to 1

The `window_score` is 0 if the passenger asked for the window and didn't get it and 1 in other cases

For each group `group_score` is 1 if all the group is in a row, else it is calculated as such:
```group_score = score_not_alone*satis_not_alone + score_near_rows*satis_near_rows + score_near_seats*satis_near_seats```
where:
- `score_not_alone` is 1 if no one is single out in a row, else 0
- `score_near_rows` is 1 if the group share adjacent rows, else 0
- `score_near_seats` is 1 if the group share adjacent rows and adjacent seats in those rows, else 0
- `satis_not_alone`, `satis_near_rows` and `satis_near_seats` are adjustable variables of partial satisfaction. By default 0.4, 0.2 and 0.2

### II. Place a group in a row
We suppose the group is small enough to fit the seats remaining in a row.
- if the group contains people wanting windows and windows are still available, place them near the window
- place the rest of the group by increasing number of the seat

### III. Indivisible groups naive algorithm (not implemended)
- convert the input in a list of groups
- for each row, check if there is enough place for the group to be placed
- if yes, apply algo II, if no, check next row
- some groups may be left

### IV. Indivisible groups complementarity algorithm (not implemended)
- convert the input in a list of groups
- for each row, check if the row is empty or if there is there is exactly enough place for the group to be placed
- if yes, apply algo II, if no, check next row
- if the group is still not placed, check all the rows again applying algo III
- some groups may be left

### V. Complementary algorithm
- convert the input in a list of groups
- split all the groups to big to fit a row into two subgroups, with the windows demands equally split in the two half groups
- apply algo IV
- if the group/subgroup is still not placed, split it again and apply algo IV
- everyone is placed

### VI. Window first complementary algorithm
- convert the input in a list of groups
- split all the groups to big to fit a row into two subgroups, with the windows demands equally split in the two half groups
- split all the groups containing more than 2 window demands
- sort the groups by number of windows asked (primary sort key) and size (secondary sort key)
- apply algo V
- everyone is placed

### VII. Group first complementary algorithm
- convert the input in a list of groups
- sort the groups by size (primary sort key) and number of windows asked (secondary sort key)
- split all the groups to big to fit a row into two subgroups, with the windows demands equally split in the two half groups (splitting at this stage increase the chance subgroups are in adjacent rows)
- apply algo V
- everyone is placed

### VIII. further algorithms...
Other algorithm splitting groups that ask for more than 2 windows and/or presenting different order of splitting/sorting could be implemented, favoring more or less window and group placements, or other additional optimisation parameters not defined here (corridor preference for example). 
But we will stop here.

## Use the code
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



