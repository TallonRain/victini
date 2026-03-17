import random

const_types = ["Normal Type", "Fire Type", "Water Type", "Grass Type", "Electric Type", "Ice Type", "Fighting Type",
               "Poison Type", "Ground Type", "Flying Type", "Psychic Type", "Bug Type", "Rock Type", "Ghost Type",
               "Dragon Type", "Dark Type", "Steel Type", "Fairy Type"]


class Wavecast:
    def __init__(self):
        self.bag = None
        self.queue = None

    def generate(self):
        self.bag = const_types.copy()  # fill the bag!
        self.queue = []
        for _ in range(7):
            index = random.randint(0, len(self.bag) - 1)  # grab a random index from the bag!
            next_type = self.bag.pop(index)  # grab the type from the random index!
            self.queue.append(next_type)  # add it to the queue

    def cycle(self):
        if len(self.bag) == 0:  # is bag empty?
            self.bag.extend(const_types)  # fill the bag!
        index = random.randint(0, len(self.bag) - 1)  # grab a random index from the bag!
        next_type = self.bag.pop(index)  # grab the type from the random index!
        self.queue.append(next_type)  # add it to the queue
        # queue now has 8 elements! pop to reduce it back to 7
        return self.queue.pop(0)

    def save(self, filepath):
        with open(filepath, "w") as file:
            for item in self.queue:  # save the queue first! always 7 elements
                file.write(f"{item},")
            for item in self.bag:  # save the bag next! variable number of elements (0 <= len(bag) <= 11)
                file.write(f"{item},")
        print("Wavecast saved!")

    def load(self, filepath):
        loaded_wavecast = None
        with open(filepath, "r") as file:
            loaded_wavecast = file.read().rstrip(",").split(",")  # read both bag and queue!
        self.queue = loaded_wavecast[:7]  # slice off the first seven elements for the queue
        self.bag = loaded_wavecast[7:]  # slice the rest for the bag

        # a wavecast is deemed corrupt if:
        # - the queue is not exactly seven elements long
        # - the wavecast has a type that doesn't exist (not in const_types)
        if (len(self.queue) == 7 and
                all(t in const_types for t in self.queue + self.bag)):
            # all checks clear!
            print(f"Wavecast loaded: queue={self.queue}, bag={self.bag}")
        else:
            print("Huh? The Wavecast file was corrupt... whatever! Generating a new Wavecast!")
            self.generate()
