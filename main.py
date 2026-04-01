import logging

from preparation import read_data


def main():
    logging.basicConfig(
        level=logging.DEBUG,
    )

    df = read_data("data/superstore.csv")
    print(df)


if __name__ == "__main__":
    main()
