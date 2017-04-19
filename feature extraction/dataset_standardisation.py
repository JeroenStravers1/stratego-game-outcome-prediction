import numpy as np
#
# X = np.array([[1., 2., 0.]])
# # [ 1., -1.,  2.],
# #           [ 2.,  0.,  0.],
# #           [ 0.,  1., -1.]])
# print(X.std())
# print(X.mean())
# print((0 - X.mean()) / X.std())
import math

class DatasetStandardizer:
    """script written specifically to standardize my generated Stratego datasets"""

    COLUMNS_TO_PROCESS = 78
    CLASS_LABEL_INDEX = 78

    def __init__(self, path_file_to_standardize):
        self.file_path = path_file_to_standardize


    def get_mean_per_column(self):
        iterations = 0
        sum_values = [0.] * self.COLUMNS_TO_PROCESS
        mean_values = list()
        with open(self.file_path) as dataset:
            for line in dataset:
                if iterations == 0:
                    iterations += 1
                    continue
                line_components = line.split(",")
                for component_index in range(self.COLUMNS_TO_PROCESS):
                    sum_values[component_index] += float(line_components[component_index])
                iterations += 1
        for summed_value in sum_values:
            mean_current_value = summed_value / iterations
            mean_values.append(mean_current_value)
        print(iterations)
        print(mean_values)

    def generate_stdev(self, means):
        iterations = 0
        sum_squared_variances = [0] * self.COLUMNS_TO_PROCESS
        with open(self.file_path, "r") as dataset:
            for line in dataset:
                if iterations == 0:
                    iterations += 1
                    continue
                line_components = line.split(",")
                for component_index in range(self.COLUMNS_TO_PROCESS):
                    variance = float(line_components[component_index]) - means[component_index]
                    sum_squared_variances[component_index] += variance ** 2
                iterations += 1
        stdevs = []
        for sum_square_var in sum_squared_variances:
            mean_square_var = sum_square_var / iterations
            stdevs.append(math.sqrt(mean_square_var))
        print(stdevs)





if __name__ == "__main__":
    standardizer = DatasetStandardizer("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/train_cleaned.txt")
    # standardizer.get_mean_per_column()
    standardizer.generate_stdev([5.11013418163104, 5.072764985556317, 0.6192700748626645, 0.6256810558807668, 0.49222236813409936, 0.48949422377892715, 56.898636358432164, 60.91834620363312, 57.7488490251215, 56.9783247921724, 0.826709799130482, 0.8030950383074574, 0.9774804031329198, 1.0115613933807084, 16.199834859450764, 16.81393070205716, 29.016106755736995, 28.56909842268997, 24.770802994502592, 25.02724223524192, 18.086393720493334, 18.364340609644064, 0.4817739326877629, 0.48151421756601104, 0.6192700748626645, 0.6256810558807668, 175.4799835075396, 178.06380011223945, 0.9895205383025231, 0.13884957898774902, 0.1497867248541314, 3.8520457389030573, 4.018724196054919, 5472311.778490119, 0.6650436566122269, 0.3563452451461001, 272.86971837787854, 321.1204584918436, 6.644381306375132, 13.268876597634579, 1173590.4521608553, 1205837.6256533675, 17.8516720739176, 18.705258598488975, 1.2454783403183078, 1.2414349019995767, 43.161860781878175, 42.511353300021725, 1.1953812204204186, 110.6520367146288, 6.879656222743554, 70.17414677552945, 10.688186048731067, 11.57022641769024, 69.25378524867897, 8.095167132531758, 112.92760718409951, 1.4938798676184881, 1.1107461842187314, 158.20261453389128, 8.679569759209835, 110.62486170252588, 16.57366173677203, 17.076632305467406, 107.66837527086875, 10.012186911230128, 161.05919793614896, 1.4310858629873477, 1.3785515648644002, 110.93893710776575, 7.757012873507457, 69.39085851481194, 11.44628407958457, 10.710480280089447, 69.4764474867024, 7.22884622802197, 113.21485369628594, 1.3303718672499099]
)

# dus pak voor elke kolom het gemiddelde en de stdev
# bereken dan vervolgens de Z-score per waarde
# dan heb je je dataset gestandaardiseerd
# stdev == sqrt( sum( (x[i] - mean(x)) ^ 2) / n )
# dus root of (squared variance divided by n)