import argparse
from group import GroupManager
from participant import ParticipantManager
from bill import BillManager


def main():
    parser = argparse.ArgumentParser(description="Xsplittr")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Group commands
    group_parser = subparsers.add_parser("group", help="Group management")
    group_parser.add_argument("action", choices=["create", "delete"], help="Action to perform")
    group_parser.add_argument("--name", help="Group name")
    group_parser.add_argument("--split", choices=["equal", "percentage"], help="Split method (required for create)",
                              required=False)

    # Participant commands
    participant_parser = subparsers.add_parser("participant", help="Participant management")
    participant_parser.add_argument("action", choices=["add", "remove"], help="Action to perform")
    participant_parser.add_argument("--group", required=True, help="Group name")
    participant_parser.add_argument("--first_name", help="First name of participant", required=False)
    participant_parser.add_argument("--last_name", help="Last name of participant", required=False)

    # Bill commands
    bill_parser = subparsers.add_parser("bill", help="Bill management")
    bill_parser.add_argument("action", choices=["add", "remove"], help="Action to perform")
    bill_parser.add_argument("--group", required=True, help="Group name")
    bill_parser.add_argument("--title", help="Bill title", required=False)
    bill_parser.add_argument("--amount", type=float, help="Bill amount", required=False)
    bill_parser.add_argument("--date", help="Bill date (YYYY-MM-DD)", required=False)
    bill_parser.add_argument("--split", choices=["equal", "percentage"], required=False, help="Split method for the bill")

    args = parser.parse_args()

    if args.command == "group":
        group_manager = GroupManager()
        if args.action == "create":
            if not args.name or not args.split:
                print("Error: Group name and split method are required.")
            else:
                group_manager.create_group(args.name, args.split)
                print(f"Group '{args.name}' created with '{args.split}' split method.")
        elif args.action == "delete":
            if not args.name:
                print("Error: Group name is required.")
            else:
                group_manager.delete_group(args.name)
                print(f"Group '{args.name}' deleted.")

    elif args.command == "participant":
        participant_manager = ParticipantManager()
        if args.action == "add":
            if not args.group or not args.first_name or not args.last_name:
                print("Error: Group name, first name, and last name are required.")
            else:
                participant_manager.add_participant(args.group, args.first_name, args.last_name)
                print(f"Participant '{args.first_name} {args.last_name}' added to group '{args.group}'.")
        elif args.action == "remove":
            if not args.group or not args.first_name or not args.last_name:
                print("Error: Group name, first name, and last name are required.")
            else:
                participant_manager.remove_participant(args.group, args.first_name, args.last_name)
                print(f"Participant '{args.first_name} {args.last_name}' removed from group '{args.group}'.")

    elif args.command == "bill":
        bill_manager = BillManager()
        if args.action == "add":
            if not args.group or not args.title or args.amount is None or not args.date or not args.split:
                print("Error: Group name, title, amount, date, and split method are required.")
            else:
                bill_manager.add_bill(args.group, args.title, args.amount, args.date, args.split)
                print(f"Bill '{args.title}' added to group '{args.group}'.")
        elif args.action == "remove":
            if not args.group or not args.title:
                print("Error: Group name and title are required.")
            else:
                bill_manager.remove_bill(args.group, args.title)
                print(f"Bill '{args.title}' removed from group '{args.group}'.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
