from src.simulation.models import SimulationState, WorldState
from src.parser.pydantic_validation import Zone
from dataclasses import dataclass
from typing import Any


@dataclass
class MoveRequest:
    drone: str
    origin: str
    dest: str
    connection_key: str
    is_restricted: bool


class SimulationStep:
    def __init__(self, state: SimulationState, world: WorldState):
        self.state = state
        self.world = world

    def key_format(self, start: str, end: str, placement: Any) -> str:
        if f"{start}-{end}" in placement:
            connection_key = f"{start}-{end}"
        else:
            connection_key = f"{end}-{start}"

        return connection_key

    def resolve_arrivals(self) -> dict[str, str]:
        resolved: dict[str, str] = {}

        for drone, (origin, dest) in list(self.state.in_transit.items()):
            key = self.key_format(origin, dest, self.world.connections)
            self.state.connection_occupancy[key] -= 1
            self.state.drone_positions[drone] = dest
            self.state.hub_occupancy[dest] += 1
            del self.state.in_transit[drone]
            resolved[drone] = dest
            if self.state.drone_paths[drone]:
                self.state.drone_paths[drone].pop(0)

        return resolved

    def collect_requests(self, just_arrived: dict[str, str]
                         ) -> list[MoveRequest]:
        requests: list[MoveRequest] = []

        for drone, current_pos in self.state.drone_positions.items():
            if current_pos == self.world.end:
                continue

            if drone in self.state.in_transit:
                continue

            if drone in just_arrived:
                continue

            if '-' in current_pos:
                continue

            remaining_path = self.state.drone_paths[drone]
            if not remaining_path:
                continue

            next_pos = remaining_path[0]

            connection_key = self.key_format(current_pos, next_pos,
                                             self.world.connections)

            next_hub_meta = self.world.hubs[next_pos].processed_meta
            if next_hub_meta is None:
                continue

            is_restricted = (next_hub_meta.zone == Zone.restricted)

            requests.append(MoveRequest(drone, current_pos, next_pos,
                                        connection_key,
                                        is_restricted))

        return requests

    def allocate_capacity(self, requests: list[MoveRequest],
                          hub_max: dict[str, int],
                          conn_max: dict[str, int]) -> \
            list[MoveRequest]:
        admitted: list[MoveRequest] = []

        ordered_requests = sorted(requests,
                                  key=lambda req: int(req.drone.split('D')[1]))

        tentative_hub = self.state.hub_occupancy.copy()

        tentative_conn = self.state.connection_occupancy.copy()

        for req in ordered_requests:
            conn_cap = conn_max.get(req.connection_key, 1)
            conn_used = tentative_conn.get(req.connection_key, 0)
            if conn_used >= conn_cap:
                continue

            if req.is_restricted:
                admitted.append(req)
                tentative_conn[req.connection_key] += 1
                tentative_hub[req.origin] -= 1
                continue

            hub_cap = hub_max.get(req.dest, 1)
            hub_used = tentative_hub.get(req.dest, 0)

            hub_ok = (req.dest == self.world.end) or (hub_used < hub_cap)
            if not hub_ok:
                continue

            admitted.append(req)
            tentative_conn[req.connection_key] += 1
            tentative_hub[req.origin] -= 1
            tentative_hub[req.dest] += 1

        return admitted

    def apply_moves(self, admitted: list[MoveRequest]) -> None:
        for req in admitted:
            if req.is_restricted:
                self.state.in_transit[req.drone] = (req.origin, req.dest)
                self.state.drone_positions[req.drone] = req.connection_key
                self.state.hub_occupancy[req.origin] -= 1

            else:
                self.state.drone_positions[req.drone] = req.dest
                self.state.hub_occupancy[req.origin] -= 1
                self.state.hub_occupancy[req.dest] += 1
                if self.state.drone_paths[req.drone]:
                    self.state.drone_paths[req.drone].pop(0)

        self.state.connection_occupancy = {key: 0 for key
                                           in self.world.connections}

        for drone, (origin, dest) in self.state.in_transit.items():
            key = self.key_format(origin, dest,
                                  self.world.connections)

            self.state.connection_occupancy[key] += 1

        self.state.turn += 1
