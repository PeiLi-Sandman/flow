"""Example of modified intersection network with human-driven vehicles."""
from flow.controllers import RLController, IDMController, ConstAccController,\
    SumoCarFollowingController, SumoLaneChangeController,\
    RandomConstAccController, RandomLaneChanger, StaticLaneChanger
from flow.core.experiment import SumoExperiment
from flow.core.params import SumoParams, EnvParams, NetParams, InitialConfig,\
    SumoCarFollowingParams
from flow.core.vehicles import Vehicles
from flow.envs.intersection_env import IntersectionEnv, ADDITIONAL_ENV_PARAMS
from flow.scenarios.intersection import IntersectionScenario, ADDITIONAL_NET_PARAMS
from flow.controllers.routing_controllers import IntersectionRandomRouter
from flow.core.params import InFlows
import numpy as np
seed=204
np.random.seed(seed)


def intersection_example(render=None,
                     save_render=None,
                     sight_radius=None,
                     pxpm=None,
                     show_radius=None):
    """
    Perform a simulation of vehicles on modified minicity of University of
    Delaware.

    Parameters
    ----------
    render: bool, optional
        specifies whether to use sumo's gui during execution

    Returns
    -------
    exp: flow.core.SumoExperiment type
        A non-rl experiment demonstrating the performance of human-driven
        vehicles on the minicity scenario.
    """
    sumo_params = SumoParams(render=False,seed=seed)

    if render is not None:
        sumo_params.render = render

    if save_render is not None:
        sumo_params.save_render = save_render

    if sight_radius is not None:
        sumo_params.sight_radius = sight_radius

    if pxpm is not None:
        sumo_params.pxpm = pxpm

    if show_radius is not None:
        sumo_params.show_radius = show_radius

    # sumo_params.sim_step = 0.2

    vehicles = Vehicles()

    # Add mixed-autonomy traffic
    insertion_prob = 0.1
    autonomy_percent = 1.0#0.5
    prob_table = {
        'manned': (1 - autonomy_percent)*insertion_prob,
        'autonomous': autonomy_percent*insertion_prob,
    }
    inflow = InFlows()
    for type in ['autonomous']:#['manned', 'autonomous']:
        vehicles.add(
            veh_id=type,
            speed_mode=0b11111,
            lane_change_mode=0b011001010101,
            acceleration_controller=(SumoCarFollowingController, {}),
            lane_change_controller=(SumoLaneChangeController, {}),
            routing_controller=(IntersectionRandomRouter, {}),
            num_vehicles=0,
        )
        inflow.add(
            veh_type=type,
            edge='e_1_in',
            probability=prob_table[type],
            departSpeed=8,
            departLane='random'
        )
        inflow.add(
            veh_type=type,
            edge='e_3_in',
            probability=prob_table[type],
            departSpeed=8,
            departLane='random'
        )
        inflow.add(
            veh_type=type,
            edge='e_5_in',
            probability=prob_table[type],
            departSpeed=8,
            departLane='random'
        )
        inflow.add(
            veh_type=type,
            edge='e_7_in',
            probability=prob_table[type],
            departSpeed=8,
            departLane='random'
        )

    env_params = EnvParams(
        additional_params=ADDITIONAL_ENV_PARAMS,
    )

    net_params = NetParams(
        inflows=inflow,
        no_internal_links=False,
        junction_type='traffic_light',
        additional_params=ADDITIONAL_NET_PARAMS.copy(),
    )

    initial_config = InitialConfig(
        spacing='uniform',
        edges_distribution=['e_1'], # add a placeholder
        min_gap=5,
    )

    scenario = IntersectionScenario(
        name='intersection',
        vehicles=vehicles,
        initial_config=initial_config,
        net_params=net_params,
    )

    env = IntersectionEnv(env_params, sumo_params, scenario)

    return SumoExperiment(env, scenario)


if __name__ == "__main__":
    exp = intersection_example(render=True,
                               save_render=False,
                               sight_radius=20,
                               pxpm=4,
                               show_radius=False)

    # run for a set number of rollouts / time steps
    exp.run(1, 2000)
