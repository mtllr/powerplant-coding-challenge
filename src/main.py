# main.py
import os
from fastapi import FastAPI
import uvicorn
from psutil import cpu_percent, virtual_memory
from pydantic import (
    BaseModel,
    ConfigDict,
    AliasGenerator,
    AliasChoices,
    field_validator,
    computed_field,
)
from typing import List
from scipy.optimize import linprog


#########################
# ENVIRONMENT VARIABLES #
#########################
HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", "8888"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
RELOAD: bool = bool(os.getenv("RELOAD", False))
TEST: bool = bool(os.getenv("TEST", False))
WORKERS: int = int(os.getenv("WORKERS", "4"))
CO2_CONVERSION_FACTOR = 0.3  # 1 MWh -> 0.3 t of fuel used

###############
# DATA MODELS #
###############

fuels_aliases = {
    "gas": AliasChoices("gas(euro/MWh)"),
    "kerosine": AliasChoices("kerosine(euro/MWh)"),
    "co2": AliasChoices("co2(euro/ton)"),
    "wind": AliasChoices("wind(%)"),
}


class FuelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=lambda field_name: fuels_aliases.get(field_name, None)
        )
    )
    gas: float
    kerosine: float
    co2: float
    wind: int


class PowerplantModel(BaseModel):
    name: str
    type: str
    efficiency: float
    pmin: int
    pmax: int

    @field_validator("type")
    def to_fuel_type(cls, value):
        fuel_types = {"windturbine": "wind", "gasfired": "gas", "turbojet": "kerosine"}
        return fuel_types[value]

    # @computed_field
    def cost_per_MWh(
        self, fuel: float, co2_price: float = 0.0, co2_conversion: float = 0.0
    ) -> float:
        """cost of 1 MWh of generated electricity with the given fuel"""
        if self.type == "wind":
            res = 0
        elif self.type == "gas":
            res = fuel / self.efficiency
        else:  # kerosine
            res = (fuel + co2_conversion * co2_price) / self.efficiency
        return res

    # @computed_field
    def output_range(self, fuel) -> tuple[float, float]:
        """pmin and pmax for each plants, only wind changes in MWh"""
        if self.type == "wind":
            res: tuple[float, float] = (
                self.pmax * fuel / 100.0,
                self.pmax * fuel / 100.0,
            )
        else:
            res = float(self.pmin), float(self.pmax)
        return res


class LoadModel(BaseModel):
    load: int
    fuels: FuelModel
    powerplants: List[PowerplantModel]


###############
# APPLICATION #
###############
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {
        "status": "running",
        "cpu_load": cpu_percent(1),
        "ram_load": virtual_memory(),
    }


@app.post("/productionplan")
def prod_plan(loadmsg: LoadModel) -> list[dict]:
    """naive implementation"""

    def assign_power(range: tuple[float, float], load: float) -> float:
        if load < range[0]:
            return 0
        elif range[0] < load < range[1]:
            return load
        else:  # range[1] < load
            return range[1]

    res = []
    load = loadmsg.load
    fuels = loadmsg.fuels
    powerplants = loadmsg.powerplants

    # create data structure [[name, type, price, output], ...]
    names = [pp.name for pp in powerplants]
    costs = [
        pp.cost_per_MWh(getattr(fuels, pp.type), fuels.co2, CO2_CONVERSION_FACTOR)
        for pp in powerplants
    ]
    types = [pp.type for pp in powerplants]
    output_ranges = [pp.output_range(getattr(fuels, pp.type)) for pp in powerplants]
    supply = list(zip(names, types, costs, output_ranges))

    # if there is no wind we set wind output to 0 automatically and continue the optimization over the leftover plants
    if fuels.wind == 0:
        windfarms = list(filter(lambda item: item[1] == "wind", supply))
        res.extend([{"name": pp[0], "p": 0} for pp in windfarms])
        supply = list(filter(lambda item: item[1] != "wind", supply))

    # sort supply on ppMWh (=> cost minimization)
    supply.sort(key=lambda item: item[2])

    # remove load until it matches with cumulative production output
    # no guarantee on the existence of result
    # no guarantee on result optimality
    for plant in supply:
        p = assign_power(plant[3], load)
        res.append({"name": plant[0], "p": p})
        load -= p

    return res


@app.post("/productionplanlinprog")
def prod_plan_hack(loadmsg: LoadModel) -> list[dict]:
    """linear optimization implementation"""
    load = loadmsg.load
    fuels = loadmsg.fuels
    powerplants = loadmsg.powerplants

    names = [pp.name for pp in powerplants]

    costs = [
        pp.cost_per_MWh(getattr(fuels, pp.type), fuels.co2, CO2_CONVERSION_FACTOR)
        for pp in powerplants
    ]

    output_ranges = [pp.output_range(getattr(fuels, pp.type)) for pp in powerplants]

    eq_constraint = [[1] * len(names)]
    eq_val = [[load]]

    res = linprog(costs, A_eq=eq_constraint, b_eq=eq_val, bounds=output_ranges)

    res = [{"name": n, "p": float(p)} for (n, p) in zip(names, res.x)]

    print(res)

    return res


def run():
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL,
        reload=RELOAD,
        workers=WORKERS,
    )


if __name__ == "__main__":
    run()
