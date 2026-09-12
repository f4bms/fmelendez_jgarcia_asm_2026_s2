from parameters import FS


SPEED_SOUND = 343


def calculate_distance(delay_samples):

    time = delay_samples / FS


    distance = (SPEED_SOUND*time) / 2


    return distance