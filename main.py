if __name__ == "__main__":
    import pickle
    with open('data/asteroid_data.pkl', "rb") as file:
        data = pickle.load(file)
        print(data)
