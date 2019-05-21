import copy

class Passenger:
    def __init__(self, itself, group):
        if itself[-1] == "W":
            self.id = int(itself[:-1])#take less memory than str and can be used as index
            self.window = True
        else:
            self.id = int(itself)
            self.window = False
        self.group = group
        self.row = None
        self.seat = None

    def __repr__(self):
        return "p"+str(self.id)

    def satis_window(self, nb_seats_row):
        if not self.window:
            return 1
        return int(self.seat == 0 or self.seat == nb_seats_row-1)

    def set_pos(self, row, seat):
        self.row = row
        self.seat = seat


class Group:
    def __init__(self, passengers=None):
        self.passengers = [] if passengers is None else passengers
        self.windows = None
        self.score = 0

    def __str__(self):
        return "Group("+" ".join([str(p.id) for p in self.passengers])+")"

    def get_window_demands(self):
        self.windows = [p for p in self.passengers if p.window]

    def calculate_score(self, satis_not_alone=0.4, satis_near_rows=0.2, satis_near_seats=0.2):
        rows = set([p.row for p in self.passengers])
        if len(rows) == 1:
            self.score = 1
        else:
            self.score = 0
            seats = set([p.seat for p in self.passengers])
            pass_by_row = {r:0 for r in rows}
            for p in self.passengers:
                pass_by_row[p.row] += 1
            nb_pass = pass_by_row.values()
            if max(rows)-min(rows) == len(rows)-1:
                self.score += satis_near_rows
                if len(seats) == max(nb_pass):
                    self.score += satis_near_seats
            if all(x>1 for x in nb_pass):
                self.score += satis_not_alone

    def __len__(self):
        return len(self.passengers)

    def get_halfgroups(self):
        if len(self.windows) < 3:
            a, b = list_halves(self.passengers)
        else:
            a_w, b_w = list_halves(self.windows)
            without_w = [p for p in self.passengers if p not in self.windows]
            a, b = list_halves(a_w + without_w + b_w)
        ga, gb = Group(a), Group(b)
        ga.get_window_demands()
        gb.get_window_demands()
        return ga, gb


class Journey:
    def __init__(self, input):
        # a raw input begin with a number, a file name with a letter
        try:
            int(input[0])
        except ValueError:
            with open(input, "r") as f:
                raw = f.read()
        else:
            raw = input
        lines = raw.split("\n")
        self.nb_seats_row, self.nb_rows = (int(x) for x in lines[0].split())
        nb_seats = self.nb_rows * self.nb_seats_row
        self.passengers = [None for i in range(nb_seats)]
        self.groups = []
        for line in lines[1:]:
            group = Group()
            for x in line.split():
                p = Passenger(x, group)
                self.passengers[p.id-1] = p
                group.passengers.append(p)
            group.get_window_demands()
            self.groups.append(group)

        nb_p = sum([1 for p in self.passengers if not p is None])
        if nb_p > nb_seats:
            raise ValueError("There is more passenger than seats in the plane.")
        if nb_p < nb_seats:
            print("There is more seats than passengers. Empty seats are marked by X")
        self.score = None
        self.output = [[None for i in range(self.nb_seats_row)] for j in range(self.nb_rows)]

    def calculate_score(self, window_group_satis_ratio=1, satis_not_alone=0.4, satis_near_rows=0.2, satis_near_seats=0.2):
        for g in self.groups:
            g.calculate_score(satis_not_alone, satis_near_rows, satis_near_seats)
        weight_window = float(window_group_satis_ratio) / (window_group_satis_ratio+1.)
        weight_group = 1. / (window_group_satis_ratio + 1.)
        all_scores = [weight_window*p.satis_window(self.nb_seats_row) + weight_group*p.group.score for p in self.passengers if p]
        self.score = sum(all_scores)/len(all_scores)

    def optimise(self, func, file=None, window_group_satis_ratio=1, satis_not_alone=0.4, satis_near_rows=0.2, satis_near_seats=0.2):
        func(self)
        self.calculate_score(window_group_satis_ratio, satis_not_alone, satis_near_rows, satis_near_seats)
        return self.get_output(file)

    def get_output(self, file=None):
        sout = "\n".join([" ".join(["X" if p is None else str(p.id) for p in row]) for row in self.output])
        sout += "\n"+str(int(self.score*100))+"%"
        if file:
            with open(file, "w") as f:
                f.write(sout)
        print(sout)
        return sout



def list_halves(input):
    middle = (len(input) + 1) // 2
    return input[:middle], input[middle:]


def seat_group(journey, group, row, seats_left, w_left):
    # seat group, giving priority to windows
    # it's known there is enough space
    # if there is more window demands than windows availables, they are seated without window
    nb_w = len(group.windows)
    tmp_group = copy.copy(group.passengers)
    index_w = 0 if seats_left == journey.nb_seats_row else -1
    i = 0
    while index_w > -2 and i < len(group.windows) and w_left:
        p = group.windows[i]
        journey.output[row][index_w] = p
        seat = 0 if index_w == 0 else journey.nb_seats_row-1
        p.set_pos(row, seat)
        tmp_group.remove(p)
        i += 1
        index_w -= 1
        w_left -= 1
        seats_left -= 1
    if tmp_group:
        compt = journey.output[row].index(None)
        for p in tmp_group:
            journey.output[row][compt] = p
            p.set_pos(row, compt)
            compt += 1
            seats_left -= 1
    return seats_left, w_left


def split_groups(groups, max_val, limit="passengers"):
    if max_val < 1: raise ValueError("max_val should be 1 or higher")
    res = []
    for g in groups:
        if len(getattr(g, limit)) > max_val:
            res.extend(split_groups(g.get_halfgroups(), max_val, limit))
        elif g:
            res.append(g)
    return res


def optimise_simple(journey, groups=None):
    if groups is None:
        groups = split_groups(journey.groups, journey.nb_seats_row)# ensure all the groups are smaller than a row
    seats_left = [journey.nb_seats_row for j in range(journey.nb_rows)]
    w_left = [2 for j in range(journey.nb_rows)]

    def group_loop(g):
        loop = True
        len_g = len(g)
        i = 0
        while loop and i < journey.nb_rows:
            if seats_left[i] == journey.nb_seats_row or (len_g == seats_left[i] and len(g.windows) <= w_left[i]):
                seats_left[i], w_left[i] = seat_group(journey, g, i, seats_left[i], w_left[i])
                loop = False
            i += 1
        i = 0
        while loop and i < journey.nb_rows:
            if len_g <= seats_left[i] and len(g.windows) <= w_left[i]:
                seats_left[i], w_left[i] = seat_group(journey, g, i, seats_left[i], w_left[i])
                loop = False
            i += 1
        i = 0
        while loop and i < journey.nb_rows:
            if len_g <= seats_left[i]:
                seats_left[i], w_left[i] = seat_group(journey, g, i, seats_left[i], w_left[i])
                loop = False
            i += 1
        if loop:
            inner_groups = split_groups([g], max(seats_left))
            for inner_g in inner_groups:
                group_loop(inner_g)

    for g in groups:
        group_loop(g)


def optimise_window_first(journey):
    groups = copy.copy(journey.groups)
    groups = split_groups(groups, journey.nb_seats_row, limit="passengers")
    groups = split_groups(groups, 2, limit="windows")
    groups.sort(key=lambda g:len(g), reverse=True)
    groups.sort(key=lambda g:len(g.windows), reverse=True)
    optimise_simple(journey, groups)

def optimise_group_first(journey):
    groups = copy.copy(journey.groups)
    groups.sort(key=lambda g:len(g.windows), reverse=True)
    groups.sort(key=lambda g:len(g), reverse=True)
    groups = split_groups(groups, journey.nb_seats_row, limit="passengers")
    optimise_simple(journey, groups)



if __name__ == "__main__":
    #check simple
    assert Journey("3 2\n1 2W\n3W\n4 5 6").optimise(optimise_simple) == "2 1 3\n4 5 6\n100%"
    #check diff algo
    assert Journey("4 2\n5\n6\n1 2W 3W 4W").optimise(optimise_simple) == "5 3 X 2\n6 1 X 4\n85%"
    assert Journey("4 2\n5\n6\n1 2W 3W 4W").optimise(optimise_window_first) == "2 5 6 3\n4 1 X X\n86%"
    assert Journey("4 2\n5\n6\n1 2W 3W 4W").optimise(optimise_group_first) == "2 1 4 3\n5 6 X X\n91%"
    #check split
    assert Journey("5 2\n1 2W 3W 4W 5W 6\n10\n7W 8 9").optimise(optimise_simple) == "2 1 10 9 3\n4 6 7 8 5\n80%"
    assert Journey("5 2\n1 2W 3W 4W 5W 6\n10\n7W 8 9").optimise(optimise_window_first) == "2 1 7 8 3\n4 6 9 10 5\n80%"
    assert Journey("5 2\n1 2W 3W 4W 5W 6\n10\n7W 8 9").optimise(optimise_group_first) == "2 1 7 8 3\n4 6 9 10 5\n80%"
    #check example
    assert Journey("example.txt").optimise(optimise_simple) == "2 1 3 10 4\n5 6 8 9 7\n100%"


