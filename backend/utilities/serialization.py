from .timer_utils import timer
import pickle


@timer 
def serialize_object(obj, filename):
    """Serializes an object to a file using pickle."""
    with open(filename, "wb") as file:
        pickle.dump(obj, file)

@timer 
def deserialize_object(filename):
    """Deserializes an object from a pickle file."""
    with open(filename, "rb") as file:
        return pickle.load(file)