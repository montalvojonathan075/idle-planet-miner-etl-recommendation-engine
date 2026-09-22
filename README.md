# Idle Planet Miner ETL Recommendation Engine

## Executive Summary

This project is a modular Python and pandas ETL application that transforms raw source data into validated metrics and actionable recommendations.

The pipeline extracts and cleans source data, validates schema and business rules, calculates operational KPIs, generates possible actions, measures projected gains and costs, scores alternatives using ROI and breakeven logic, and produces ranked recommendations.

The application also maintains persistent state between sessions. After a user selects an action, the program updates the saved state, reruns the analytical workflow, and generates a new set of recommendations based on the updated conditions.

Although the scenario is based on the game *Idle Planet Miner*, the underlying workflow reflects real analytical problems involving data quality, ETL processing, operational metrics, decision support, optimization, and workflow automation.

---

## Key Features

- Modular Python ETL architecture
- pandas-based data processing
- Schema and business-rule validation
- Fail-fast data-quality controls
- Structured pipeline logging
- Persistent application state
- KPI and operational metric creation
- ROI and breakeven analysis
- Automated action generation
- Profitability filtering
- Multi-strategy recommendation engine
- Interactive decision loop
- Runtime and pipeline-stage monitoring
- Reusable calculation modules
- Automated intermediate dataset generation

---

## Business Problem

The challenge is to determine which available action provides the greatest measurable value when multiple alternatives compete for limited resources.

Possible actions include:

- Unlocking a new planet
- Increasing mining production
- Increasing cargo capacity
- Increasing ship speed

Each option has a different cost, expected benefit, recovery time, and long-term value.

Rather than relying on intuition, the application evaluates the available choices using measurable business-style metrics and ranks the most valuable actions.

---

## Solution Architecture

The project divides the analytical workflow into independent processing stages.

```text
Raw Data
   ↓
Load & Clean
   ↓
Schema Validation
   ↓
Business-Rule Validation
   ↓
Planet Worth Calculations
   ↓
Persistent State Processing
   ↓
Operational Metrics
   ↓
Possible Action Generation
   ↓
Cost & Gain Analysis
   ↓
Profitability Filtering
   ↓
Action Scoring
   ↓
Decision Engine
   ↓
Ranked Recommendations
   ↓
User Selection
   ↓
State Update
   ↓
Pipeline Re-runs
```

This modular design makes individual stages easier to test, troubleshoot, maintain, and improve.

---

## ETL Workflow

### 1. Extract

The application loads raw planet and ore reference data.

### 2. Transform

Source data is:

- Standardized
- Validated
- Converted into structured datasets
- Combined with saved player state
- Used to calculate operational metrics
- Expanded into possible upgrade actions

### 3. Validate

Before downstream calculations occur, the pipeline checks:

- Required schema
- Planet identifiers
- Ore symbols
- Yield values
- Business rules
- Record consistency

If a validation fails, the pipeline stops and reports the problem rather than allowing invalid data to affect downstream calculations.

### 4. Score

Valid actions are evaluated using:

- Projected gain
- Upgrade cost
- ROI
- Breakeven time
- Hybrid scoring
- Cost-based logic

Actions with non-positive gains are removed before final ranking.

### 5. Recommend

The decision engine produces ranked recommendations based on multiple strategies.

---

## Recommendation Strategies

### Best ROI

Identifies the action generating the strongest return relative to its cost.

### Best Breakeven

Identifies the action with the fastest investment recovery.

### Best Hybrid

Balances multiple analytical factors instead of maximizing a single metric.

### Lowest Cost

Identifies the lowest-cost valid action available to continue progression.

Using multiple strategies demonstrates that decision-making often requires balancing value, cost, speed, and long-term benefit.

---

## Data Quality & Validation

Data quality is handled before recommendations are generated.

The pipeline includes validation for:

- Required columns
- Expected schema
- Valid planet numbers
- Valid ore symbols
- Yield values
- Business rules
- Record counts

The pipeline follows a **fail-fast approach**.

If required data or a business rule fails validation, processing stops and the error is reported. This prevents unreliable source data from reaching downstream metrics and recommendation logic.

Example successful validation:

```text
INFO: Schema validation passed.
INFO: Business rule validation passed.
INFO: Planet number validation passed.
INFO: Ore symbol validation passed.
INFO: Yield validation passed.
```

---

## Pipeline Logging & Monitoring

Structured logging was added so every stage of the ETL process can be traced and failures can be isolated quickly.

The log records information including:

- Pipeline start and completion
- Individual script execution
- Validation results
- Record counts
- Generated datasets
- Actions generated
- Actions filtered
- Output creation
- Intermediate-file cleanup
- Runtime
- Errors and failures

Example:

```text
INFO: Starting load_and_clean pipeline.
INFO: Schema validation passed.
INFO: Business rule validation passed.
INFO: Loaded and cleaned 76 planets.
INFO: Loaded and cleaned 27 ores.
INFO: Created 10 possible actions.
INFO: Removed 6 actions with non-positive gain.
INFO: Remaining profitable actions: 4
INFO: ETL Pipeline Completed Successfully (5.29s)
```

This makes it easier to understand what the pipeline did during each execution and determine where a failure occurred.

---

## Persistent State & Interactive Decision Loop

The application maintains persistent state through saved data.

When the application starts, it checks whether an existing state is available.

```text
INFO: planet_levels.csv already exists. Using existing galaxy state.
```

After recommendations are generated:

1. The user reviews the available choices.
2. The user selects an action.
3. The application's stored state is updated.
4. The pipeline recalculates the affected metrics.
5. Available actions are regenerated.
6. The recommendation engine produces a new set of ranked choices.

This creates a continuous analytical loop rather than a one-time static report.

```text
Current State
     ↓
ETL Pipeline
     ↓
Recommendations
     ↓
User Decision
     ↓
Update State
     ↓
Recalculate
     ↓
New Recommendations
```

---

## Project Structure

```text
ETL_Projects/
│
├── ETL Scripts/
│   ├── Main.py
│   ├── load_and_clean.py
│   ├── galaxy_setup.py
│   ├── planet_worth.py
│   ├── planet_levels.py
│   ├── planet_metrics.py
│   ├── possible_actions.py
│   ├── action_gains.py
│   ├── action_scores.py
│   ├── decision_engine.py
│   ├── questionnaire.py
│   ├── report_generator.py
│   ├── calculations.py
│   │
│   └── calculations/
│       ├── core_metrics.py
│       ├── gain_calculations.py
│       └── score_calculations.py
│
├── Raw Data/
│   ├── Planets.txt
│   └── Ores.txt
│
├── DataFrames/
│   ├── planet_data.csv
│   ├── planet_levels.csv
│   ├── planet_metrics.csv
│   ├── action_scores.csv
│   ├── choices.csv
│   └── pipeline_log.txt
│
├── .gitignore
└── README.md
```

---

## Core Components

### `Main.py`

Coordinates the complete workflow and controls application execution.

### `load_and_clean.py`

Loads raw data, standardizes columns, validates schema and business rules, creates data-quality summaries, and prepares clean datasets.

### `galaxy_setup.py`

Supports initialization of the application state.

### `planet_worth.py`

Calculates planet value using ore composition and associated reference values.

### `planet_levels.py`

Maintains persistent state so progress is retained between sessions.

### `planet_metrics.py`

Calculates operational metrics including:

- Mining rate
- Cargo capacity
- Ship speed
- Trip time
- Deposit rate
- Operational efficiency

### `possible_actions.py`

Generates currently available actions, including:

- Planet unlocks
- Mining upgrades
- Cargo upgrades
- Speed upgrades

### `action_gains.py`

Calculates projected costs and gains and removes actions that do not produce positive value.

### `action_scores.py`

Scores profitable actions using ROI, breakeven, and hybrid analytical logic.

### `decision_engine.py`

Ranks scored alternatives and converts analytical results into actionable recommendations.

### `questionnaire.py`

Provides the interactive terminal workflow used to capture user decisions.

### `report_generator.py`

Supports presentation and reporting of recommendation results.

### `calculations/`

Contains reusable calculation logic separated from the primary ETL workflow.

---

## Example Recommendation Output

The decision engine can produce recommendations such as:

```text
Best ROI: Unlock Planet 2
Best Hybrid: Mining Upgrade Planet 1
Best Breakeven: Cargo Upgrade Planet 1
Lowest Cost: Speed Upgrade Planet 1
```

After the user selects an action, the application updates its saved state and generates another set of recommendations.

---

## Technical Skills Demonstrated

### Python Development

- Modular script design
- Functions and reusable components
- File input/output
- State management
- Error handling
- Program flow
- Interactive terminal input

### pandas & Data Processing

- Data loading
- Cleaning
- Standardization
- Filtering
- Dataset merging
- Calculated fields
- CSV output generation

### ETL

- Extraction
- Transformation
- Validation
- Intermediate datasets
- Pipeline orchestration
- Output management

### Data Quality

- Schema validation
- Business-rule validation
- Record validation
- Fail-fast processing
- Data-quality summaries

### Pipeline Reliability

- Structured logging
- Stage-level monitoring
- Runtime tracking
- Failure isolation
- Persistent state

### Analytics

- KPI creation
- ROI analysis
- Breakeven analysis
- Cost-benefit evaluation
- Action prioritization
- Recommendation logic

---

## How to Run

From the project root:

```bash
python "ETL Scripts/Main.py"
```

The application will:

1. Load source data
2. Validate data quality
3. Calculate current metrics
4. Generate valid actions
5. Calculate projected gains and costs
6. Filter non-profitable actions
7. Score remaining alternatives
8. Generate ranked recommendations
9. Ask the user to select an action
10. Update the saved state
11. Recalculate recommendations based on the new state

---

## Portfolio Relevance

This project was built to demonstrate an end-to-end **data-to-decision workflow**.

While the scenario uses data from *Idle Planet Miner*, the underlying technical workflow mirrors real analytical problems in areas such as:

- Operations analysis
- Resource allocation
- Performance optimization
- Financial analysis
- Data quality
- ETL development
- Decision-support systems

The project demonstrates the ability to move beyond simply analyzing a dataset and instead build a repeatable system that:

```text
Collects Data
      ↓
Validates Data
      ↓
Transforms Data
      ↓
Creates Metrics
      ↓
Applies Business Rules
      ↓
Evaluates Alternatives
      ↓
Recommends Actions
      ↓
Tracks Changing State
```

---

## Future Improvements

Potential future enhancements include:

- SQL-based data storage
- Power BI reporting and visualization
- Automated testing
- Additional recommendation strategies
- Historical recommendation tracking
- Expanded error handling
- Configuration-driven scoring weights

---

## Final Note

The goal of this project was not simply to build a game calculator.

The goal was to take a multi-variable decision problem and turn it into a structured, validated, repeatable analytical workflow.

The result is a modular Python application that demonstrates ETL development, data validation, logging, analytical scoring, automation, persistent state, and data-driven decision support.