# Powerplant Coding Challenge

## The problem

Determine the merit-order of the powerplant production in order to match the Load (power demand on the grid in MWh) during the following hour. This merit order is chiefly summarized as:

objective: $$min(\sum_{i=1}^{n}C_i)$$
with $C_i$ the cost of running the Powerplant i at power P during the next hour.

constraints: $$\sum_{i=1}^{n}P_i = L$$
with $P_i$ the power the Powerplant i is producing during the next hour.

## Requirements

- [X] a README.md file
  - [X] instructions on how to build
- [X] a server that provides an API (fastapi)
- [X] exposed port 8888

## How to build

### With uv

`git clone <powerplant-coding-challenge>`
`cd <powerplant-coding-challenge>`
`uv venv`
`uv sync`
`run`

you can now send your posts to the API using curl:

```bash
curl -X POST http://localhost:8888/productionplan \
-H "Content-Type: application/json" \
-d '{
  "load": 480,
  "fuels":
  {
    "gas(euro/MWh)": 13.4,
    "kerosine(euro/MWh)": 50.8,
    "co2(euro/ton)": 20,
    "wind(%)": 60
  },
  "powerplants": [
    {
      "name": "gasfiredbig1",
      "type": "gasfired",
      "efficiency": 0.53,
      "pmin": 100,
      "pmax": 460
    },
    {
      "name": "gasfiredbig2",
      "type": "gasfired",
      "efficiency": 0.53,
      "pmin": 100,
      "pmax": 460
    },
    {
      "name": "gasfiredsomewhatsmaller",
      "type": "gasfired",
      "efficiency": 0.37,
      "pmin": 40,
      "pmax": 210
    },
    {
      "name": "tj1",
      "type": "turbojet",
      "efficiency": 0.3,
      "pmin": 0,
      "pmax": 16
    },
    {
      "name": "windpark1",
      "type": "windturbine",
      "efficiency": 1,
      "pmin": 0,
      "pmax": 150
    },
    {
      "name": "windpark2",
      "type": "windturbine",
      "efficiency": 1,
      "pmin": 0,
      "pmax": 36
    }
  ]
}'
```

### With poetry

`git clone <powerplant-coding-challenge>`
`cd powerplant-coding-challenge>`
`poetry install`
`poetry shell`
`poetry run run`

you can now send your posts to the API using curl:

```bash
curl -X POST http://localhost:8888/productionplan \
-H "Content-Type: application/json" \
-d '{
  "load": 480,
  "fuels":
  {
    "gas(euro/MWh)": 13.4,
    "kerosine(euro/MWh)": 50.8,
    "co2(euro/ton)": 20,
    "wind(%)": 60
  },
  "powerplants": [
    {
      "name": "gasfiredbig1",
      "type": "gasfired",
      "efficiency": 0.53,
      "pmin": 100,
      "pmax": 460
    },
    {
      "name": "gasfiredbig2",
      "type": "gasfired",
      "efficiency": 0.53,
      "pmin": 100,
      "pmax": 460
    },
    {
      "name": "gasfiredsomewhatsmaller",
      "type": "gasfired",
      "efficiency": 0.37,
      "pmin": 40,
      "pmax": 210
    },
    {
      "name": "tj1",
      "type": "turbojet",
      "efficiency": 0.3,
      "pmin": 0,
      "pmax": 16
    },
    {
      "name": "windpark1",
      "type": "windturbine",
      "efficiency": 1,
      "pmin": 0,
      "pmax": 150
    },
    {
      "name": "windpark2",
      "type": "windturbine",
      "efficiency": 1,
      "pmin": 0,
      "pmax": 36
    }
  ]
}'
```

### With Docker

`git clone <powerplant-coding-challenge>`
`cd powerplant-coding-challenge>`
`docker build -t challenge-image .`
`docker run -d --name powerplant-challenge-server challenge-image`

```bash
curl -X POST http://localhost:8888/productionplan \
-H "Content-Type: application/json" \
-d '{
  "load": 480,
  "fuels":
  {
    "gas(euro/MWh)": 13.4,
    "kerosine(euro/MWh)": 50.8,
    "co2(euro/ton)": 20,
    "wind(%)": 60
  },
  "powerplants": [
    {
      "name": "gasfiredbig1",
      "type": "gasfired",
      "efficiency": 0.53,
      "pmin": 100,
      "pmax": 460
    },
    {
      "name": "gasfiredbig2",
      "type": "gasfired",
      "efficiency": 0.53,
      "pmin": 100,
      "pmax": 460
    },
    {
      "name": "gasfiredsomewhatsmaller",
      "type": "gasfired",
      "efficiency": 0.37,
      "pmin": 40,
      "pmax": 210
    },
    {
      "name": "tj1",
      "type": "turbojet",
      "efficiency": 0.3,
      "pmin": 0,
      "pmax": 16
    },
    {
      "name": "windpark1",
      "type": "windturbine",
      "efficiency": 1,
      "pmin": 0,
      "pmax": 150
    },
    {
      "name": "windpark2",
      "type": "windturbine",
      "efficiency": 1,
      "pmin": 0,
      "pmax": 36
    }
  ]
}'
```

## API Resources

- `POST productionplan`: manual solution to the coding challenge according to the explicit preference to code the optimization manually.
- `POST productionplanlinprog`: solution using scipy lib for linear optimization to measure manual solution performance.
- `GET health`: is the server running?

## Dev choices

I usually user TDD methodology in  order to create robust and well covered code. However given the nature of this challenge, I have decided to concentrate on making a working solution, at the expense of a couple of bugs.

Installation works with astral uv.

BUG: poetry install
BUG: Dockerfile does not build (cannot find requirements.txt)