from nwb_datajoint.common.common_position import TrackGraph
from replay_trajectory_classification.continuous_state_transitions import (
    Identity, RandomWalk, RandomWalkDirection1, RandomWalkDirection2, Uniform)
from replay_trajectory_classification.discrete_state_transitions import (
    DiagonalDiscrete, RandomDiscrete, UniformDiscrete, UserDefinedDiscrete)
from replay_trajectory_classification.environments import Environment
from replay_trajectory_classification.initial_conditions import (
    UniformInitialConditions, UniformOneEnvironmentInitialConditions)
from replay_trajectory_classification.misc import NumbaKDE
from replay_trajectory_classification.observation_model import ObservationModel


def _convert_dict_to_class(d: dict, class_conversion: dict):
    class_name = d.pop('class_name')
    return class_conversion[class_name](**d)


def _convert_env(env_params):
    if env_params['track_graph'] is not None:
        env_params['track_graph'] = (TrackGraph & {
                                     'track_graph_name': env_params['track_graph']}).get_networkx_track_graph()

    return env_params

def _to_dict(transition):
    parameters = vars(transition)
    parameters['class_name'] = type(transition).__name__

    return parameters


def _convert_transitions_to_dict(transitions):
    return [[_to_dict(transition) for transition in transition_rows]
            for transition_rows in transitions]


def _restore_classes(params):
    continuous_state_transition_types = {
        'RandomWalk': RandomWalk,
        'RandomWalkDirection1': RandomWalkDirection1,
        'RandomWalkDirection2': RandomWalkDirection2,
        'Uniform': Uniform,
        'Identity': Identity,
    }

    discrete_state_transition_types = {
        'DiagonalDiscrete': DiagonalDiscrete,
        'UniformDiscrete': UniformDiscrete,
        'RandomDiscrete': RandomDiscrete,
        'UserDefinedDiscrete': UserDefinedDiscrete,
    }

    initial_conditions_types = {
        'UniformInitialConditions': UniformInitialConditions,
        'UniformOneEnvironmentInitialConditions':  UniformOneEnvironmentInitialConditions,
    }

    model_types = {
        'NumbaKDE': NumbaKDE,
    }

    params['classifier_params']['continuous_transition_types'] = [
        [_convert_dict_to_class(
            st, continuous_state_transition_types) for st in sts]
        for sts in params['classifier_params']['continuous_transition_types']]
    params['classifier_params']['environments'] = [Environment(
        **_convert_env(env_params)) for env_params in params['classifier_params']['environments']]
    params['classifier_params']['discrete_transition_type'] = _convert_dict_to_class(
        params['classifier_params']['discrete_transition_type'], discrete_state_transition_types)
    params['classifier_params']['initial_conditions_type'] = _convert_dict_to_class(
        params['classifier_params']['initial_conditions_type'], initial_conditions_types)

    if params['classifier_params']['observation_models'] is not None:
        params['classifier_params']['observation_models'] = [ObservationModel(
            obs) for obs in params['classifier_params']['observation_models']]

    try:
        params['classifier_params']['clusterless_algorithm_params']['model'] = (
            model_types[params['classifier_params']['clusterless_algorithm_params']['model']])
    except KeyError:
        pass

    return params