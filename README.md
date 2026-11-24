**Stanford Code in Place X — Final Project**

# Traflo

**Intelligent Traffic Simulation & ML-Based Signal Optimization**

Traflo is an interactive Python traffic simulation project being developed for the **Stanford Code in Place X final project**. It explores how traffic signal timings affect congestion and whether a machine-learning-assisted controller can improve traffic flow in a simulated four-way intersection.

**Status: In development.** The features, machine learning experiments, and public deployment described below are planned. Implementation and measured results will be documented as they are completed.

## Problem Statement

Traditional fixed-time traffic signals follow predefined green-light schedules, even when traffic volume changes. This can result in long queues and unnecessary delays.

Traflo aims to provide an educational simulation where users can change traffic conditions, test signal-control strategies, and compare their performance using measurable results.

## Project Objectives

- Build a working simulation of one four-way traffic intersection.
- Let users customize traffic volume and arrival rates on each road.
- Implement fixed-time and adaptive signal controllers.
- Train and evaluate a machine learning model on simulated traffic scenarios.
- Compare controllers under identical traffic conditions.
- Visualize queue lengths, waiting times, and vehicle throughput.
- Publish the code and deploy an interactive web application.

## Planned Features

### 1. Traffic Simulator
Simulate North, South, East, and West vehicle queues, vehicle arrivals, signal phases, and departures.

### 2. Interactive Scenarios
Choose predefined scenarios such as rush hour or light traffic, or adjust each road's conditions manually.

### 3. Signal Control Comparison
Compare fixed-time signal timings with a model-assisted adaptive controller.

### 4. Machine Learning
Train a scikit-learn regression model, such as Random Forest, to estimate waiting time for candidate timing decisions. Use the model's predictions to help select a signal duration within predefined safety and timing limits.

### 5. Analytics Dashboard
Display average waiting time, remaining queue length, and vehicles processed for each strategy.

### 6. Human vs AI Challenge (Future Feature)
Allow users to choose signal timings and compare their decisions with the model on the same simulated scenario.

## How the System Will Work

1. A user sets the traffic conditions of a four-way intersection.
2. Python simulation logic generates vehicle arrivals and maintains queues.
3. The fixed-time controller runs with predefined green phases.
4. The ML-assisted controller evaluates candidate phase durations.
5. Both approaches are tested against the same traffic arrivals.
6. The application compares actual simulated outcomes, rather than assuming the ML controller performs better.

**Important:** Traflo is a research and educational simulator. Synthetic traffic experiments cannot establish real-world traffic safety or performance, and the application is not intended to operate actual traffic lights.

## Proposed Technology Stack

| Component | Technology |
| --- | --- |
| Programming language | Python |
| Simulation engine | Python functions, classes, lists, and dictionaries |
| Data processing | NumPy, Pandas |
| Machine learning | scikit-learn |
| Visualizations | Matplotlib or Plotly |
| Web application | Streamlit |
| Source control | GitHub |
| Planned deployment | Streamlit Community Cloud |

## Stanford Code in Place X Concepts

This project extends concepts learned during CIPX:

- Variables, conditional statements, and loops
- Functions and modular programming
- Lists and dictionaries for storing traffic information
- Object-oriented programming for roads, controllers, and simulation state
- Problem-solving, debugging, and testing

## Development Roadmap

- [ ] Implement a four-way intersection simulation in Python.
- [ ] Create fixed-time and rule-based adaptive controllers.
- [ ] Generate simulated traffic data and document assumptions.
- [ ] Train and evaluate an ML prediction model.
- [ ] Integrate the ML controller and compare strategies fairly.
- [ ] Build a Streamlit user interface.
- [ ] Deploy the working application and add its link here.
- [ ] Add screenshots, evaluation results, and a demonstration video.

## Project Structure (Planned)

```text
traflo/
├── app.py
├── simulation/
│   ├── engine.py
│   └── controllers.py
├── ml/
│   └── train_model.py
├── data/
├── tests/
├── requirements.txt
└── README.md
```

The structure may change during development. No runnable application is available yet; installation and execution instructions will be added once the first version is implemented.

## Future Improvements

- More realistic vehicle movement and signal animations
- Human vs AI traffic-control challenge
- Multiple connected intersections
- Scenario export and extended performance reporting
- Additional baseline controllers and ML models
- Experiments with suitable real-world traffic datasets

## About

**Academic project:** Stanford Code in Place X — Final Project

**Developer:** Usman Shakir  
BS Data Science Undergraduate

[GitHub](https://github.com/Usmanshakir7) | [LinkedIn](https://www.linkedin.com/in/usman-shakir7/)
