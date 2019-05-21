import argparse
import code

parser = argparse.ArgumentParser()
parser.add_argument("input",
                    help="The input can be a string as described in the requirements or the path of a file containing said string",
                    type=str)
parser.add_argument("--output", help="the result will be copied in a file", default=None)
parser.add_argument("--algo", help="algorithm used for optimisation", default="simple")
parser.add_argument("--window_group_satis_ratio", help="value for the ratio of window/group satisfaction", default=1)
parser.add_argument("--satis_not_alone", help="partial group satisfaction value if no one is alone in a row", default=0.4)
parser.add_argument("--satis_near_rows", help="partial group satisfaction value if group shares adjacent rows", default=0.2)
parser.add_argument("--satis_near_seats", help="partial group satisfaction value if group shares adjacent seat numbers", default=0.2)
args = parser.parse_args()

if args.satis_not_alone + args.satis_near_rows + args.satis_near_seats > 1:
    raise ValueError("satis_not_alone + satis_near_rows + satis_near_seats must be <= 1")
flight = code.Flight(args.input)
flight.optimise(getattr(code, "optimise_"+args.algo),
                file=args.output,
                window_group_satis_ratio=args.window_group_satis_ratio,
                satis_not_alone=args.satis_not_alone,
                satis_near_rows=args.satis_near_rows,
                satis_near_seats=args.satis_near_seats
                )