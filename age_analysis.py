import json
import constants


def get_averages(totals):
    averages = {}
    for key, total in totals.items():
        averages[key] = total / totals["GP"]
    return averages


def analyze_data(data):
    for age, players in data.items():
        totals = {"GP": 0}
        for key in constants.STAT_COEFFS.keys():
            totals[key] = 0
        for player in players:
            for key, total in totals.items():
                totals[key] = total + player[key]
        print("Age: " + age)
        print(
            get_averages(
                totals,
            )
        )
        print("\n")


if __name__ == "__main__":
    with open("Data/seasonTotalsByAge.json") as json_file:
        data = json.load(json_file)
        analyze_data(data)