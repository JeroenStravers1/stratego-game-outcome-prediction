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
    STDEVS = []
    MEANS = [
        [5.1015298269548905, 5.075144439604748, 0.6192740599615745, 0.6258125467749911, 0.4915881893536858,
         0.4897818551923719, 56.92381604607166, 60.838894881052596, 57.68341095010918, 56.93365733907849,
         0.8261311127337594, 0.8038027813261196, 0.9778687553415427, 1.011306121128455, 16.187577145739372,
         16.79196946280662, 28.984145261452685, 28.537678027290408, 24.770962398452358, 25.032501871007476,
         18.090896421677837, 18.37078393312384, 0.48142859126040854, 0.48123605351651844, 0.6192740599615745,
         0.6258125467749911, 175.35129098496913, 177.86098102142407, 0.9899482956263949, 0.17043872618828396,
         0.17461611680917635, 4.050483271238469, 4.143286729599982, 210.10870135244784, 0.7961223166385518,
         0.665810040331209, 254.3370141658904, 256.6796187537772, 5.472592602991502, 4.744826382836794,
         45.552822152728524, 45.91159829116461, 17.873923098062516, 18.69952087001576, 1.240163280025461,
         1.235480819050495, 42.946630747644676, 42.31142228483402, 1.179293144322026, 110.75965823970559,
         6.785676341229715, 70.23939876004012, 10.693356667656905, 11.561766860207436, 69.48875437324165,
         8.039347949600476, 112.72716212703403, 1.4909188786157386, 1.0973517428959312, 157.90813991470142,
         8.589261845706984, 110.53538286382629, 16.59530834860306, 17.076971540099795, 107.9241379288231,
         9.932274690272992, 160.29433405852578, 1.4400379231295828, 1.368435939163776, 110.88855382816406,
         7.7091992984227975, 69.46614225914668, 11.486382296866898, 10.704095369500633, 69.78094661663553,
         7.1581616948413025, 113.0884423419385, 1.3277179880255487]

    ]
    # 9206270 rows

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


    def generate_standardized_dataset(self):
        pass

if __name__ == "__main__":
    standardizer = DatasetStandardizer("D:/Schooldata/Stage/jaar 4/ICT Automatisering/programmeren/Stratego games-20170320T133045Z-001/train_eval_test_sets/train_cleaned.txt")
    standardizer.get_mean_per_column()
    #standardizer.generate_stdev()
# dus pak voor elke kolom het gemiddelde en de stdev
# bereken dan vervolgens de Z-score per waarde
# dan heb je je dataset gestandaardiseerd
# stdev == sqrt( sum( (x[i] - mean(x)) ^ 2) / n )
# dus root of (squared variance divided by n)